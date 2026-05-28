"""坦克大战 - 主入口"""

import sys
import pygame

from const import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CELL_SIZE,
    EMPTY, WALL, STEEL, WATER, BUNKER, COMMANDER,
    COLOR_BLACK, COLOR_GREEN, COLOR_DARK_GREEN, DIR_VEC,
)
from map import GameMap, pos_to_grid
from bullet import Bullet


class Tank:
    """玩家坦克"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = CELL_SIZE - 4
        self.height = CELL_SIZE - 4
        self.speed = 3
        self.direction = "up"
        self.alive = True
        self.cooldown = 0          # 射击冷却帧计数
        self.cooldown_max = 12     # 冷却帧数

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def clamp(self):
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

    def can_move_to(self, dx, dy, game_map):
        """检测目标位置是否与不可通行图块重叠"""
        new_rect = self.rect.move(dx, dy)

        # 边界检测
        if (new_rect.left < 0 or new_rect.right > SCREEN_WIDTH or
                new_rect.top < 0 or new_rect.bottom > SCREEN_HEIGHT):
            return False

        # 与地图碰撞 — 检测坦克覆盖的所有格子
        left_col = new_rect.left // CELL_SIZE
        right_col = (new_rect.right - 1) // CELL_SIZE
        top_row = new_rect.top // CELL_SIZE
        bottom_row = (new_rect.bottom - 1) // CELL_SIZE

        for row in range(top_row, bottom_row + 1):
            for col in range(left_col, right_col + 1):
                tile = game_map.get(col, row)
                if tile not in (EMPTY,):
                    return False
        return True

    def shoot(self):
        """发射子弹"""
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        # 子弹出生在坦克前方
        vec = DIR_VEC[self.direction]
        bx = cx + vec[0] * (self.width // 2 + 2)
        by = cy + vec[1] * (self.height // 2 + 2)
        return Bullet(bx, by, self.direction)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, surface):
        if not self.alive:
            return
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        # 车身
        pygame.draw.rect(surface, COLOR_GREEN, rect, border_radius=3)
        pygame.draw.rect(surface, COLOR_DARK_GREEN, rect, 2, border_radius=3)

        # 炮塔
        pygame.draw.circle(surface, COLOR_DARK_GREEN, (cx, cy), 10)

        # 炮管
        if self.direction == "up":
            pygame.draw.rect(surface, COLOR_DARK_GREEN, (cx - 3, self.y - 6, 6, self.height // 2 + 6))
        elif self.direction == "down":
            pygame.draw.rect(surface, COLOR_DARK_GREEN, (cx - 3, self.y + self.height // 2, 6, self.height // 2 + 6))
        elif self.direction == "left":
            pygame.draw.rect(surface, COLOR_DARK_GREEN, (self.x - 6, cy - 3, self.width // 2 + 6, 6))
        elif self.direction == "right":
            pygame.draw.rect(surface, COLOR_DARK_GREEN, (self.x + self.width // 2, cy - 3, self.width // 2 + 6, 6))

        # 履带
        for dx, dy, w, h in [
            (2, 2, 6, self.height - 4),
            (self.width - 8, 2, 6, self.height - 4),
        ]:
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x + dx, self.y + dy, w, h), border_radius=1)


def draw_hud(surface, tank, bullets, game_over=False):
    """显示 HUD 信息"""
    try:
        font = pygame.font.SysFont("simhei", 18)
    except Exception:
        font = pygame.font.Font(None, 18)

    if game_over:
        go_surf = font.render("💀 主将阵亡！游戏结束！按 R 重新开始", True, (255, 80, 80))
        surface.blit(go_surf, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 10))
        return

    info = [
        f"坐标: ({tank.x}, {tank.y})  方向: {tank.direction}",
        f"子弹数: {len(bullets)}",
        "WASD 移动 | J/空格 射击",
    ]
    for i, text in enumerate(info):
        surf = font.render(text, True, (200, 200, 200))
        surface.blit(surf, (10, 10 + i * 22))


def draw_grid(surface):
    """画半透明网格线"""
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("坦克大战")
    clock = pygame.time.Clock()

    # ── 游戏状态 ──
    def reset_game():
        game_map = GameMap()
        tank = Tank(CELL_SIZE * 9, CELL_SIZE * 13)  # 底部中央
        bullets = []
        game_over = False
        return game_map, tank, bullets, game_over

    game_map, tank, bullets, game_over = reset_game()

    # 按键跟踪
    pressed_keys = set()
    KEY_MAP = {
        pygame.K_w: "up", pygame.K_UP: "up",
        pygame.K_s: "down", pygame.K_DOWN: "down",
        pygame.K_a: "left", pygame.K_LEFT: "left",
        pygame.K_d: "right", pygame.K_RIGHT: "right",
    }

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in KEY_MAP:
                    pressed_keys.add(event.key)
                elif event.key in (pygame.K_r,) and game_over:
                    game_map, tank, bullets, game_over = reset_game()
                elif event.key in (pygame.K_j, pygame.K_SPACE):
                    # 射击
                    if not game_over and tank.alive and tank.cooldown == 0:
                        bullets.append(tank.shoot())
                        tank.cooldown = tank.cooldown_max
            elif event.type == pygame.KEYUP:
                pressed_keys.discard(event.key)

        if not game_over:
            # ── 坦克移动 ──
            dx, dy = 0, 0
            active_dir = None
            for key in pressed_keys:
                if key in KEY_MAP:
                    active_dir = KEY_MAP[key]
                    vec = DIR_VEC[active_dir]
                    dx += vec[0]
                    dy += vec[1]
            if active_dir is not None:
                tank.direction = active_dir
                if dx != 0 and dy != 0:
                    dx *= 0.707
                    dy *= 0.707
                dx = round(dx * tank.speed)
                dy = round(dy * tank.speed)
                if tank.can_move_to(dx, dy, game_map):
                    tank.move(dx, dy)

            tank.clamp()
            tank.update()

            # ── 子弹更新 ──
            for b in bullets[:]:
                b.update(game_map)
                if not b.alive:
                    bullets.remove(b)
                    continue
                # 检测子弹是否击中主将
                col, row = pos_to_grid(int(b.x), int(b.y))
                if game_map.get(col, row) == COMMANDER:
                    game_map.set(col, row, EMPTY)
                    game_over = True

        # ── 绘制 ──
        screen.fill(COLOR_BLACK)
        draw_grid(screen)
        game_map.draw(screen)
        tank.draw(screen)
        for b in bullets:
            b.draw(screen)
        draw_hud(screen, tank, bullets, game_over)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

"""坦克大战 - 主入口（格子移动版）"""

import sys
import pygame

from const import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CELL_SIZE, COLS, ROWS,
    EMPTY, WALL, STEEL, WATER, BUNKER, COMMANDER,
    COLOR_BLACK, COLOR_GREEN, COLOR_DARK_GREEN, DIR_VEC,
)
from map import GameMap, pos_to_grid
from bullet import Bullet

MOVE_DELAY = 8  # 长按时每 8 帧移动一格


class Tank:
    """玩家坦克 — 格子移动"""

    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.width = CELL_SIZE - 4
        self.height = CELL_SIZE - 4
        self.direction = "up"
        self.alive = True
        self.shoot_cd = 0
        self.shoot_cd_max = 15
        self.move_timer = 0

    @property
    def x(self):
        return self.col * CELL_SIZE + 2

    @property
    def y(self):
        return self.row * CELL_SIZE + 2

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def can_move_to(self, dcol, drow, game_map):
        nc = self.col + dcol
        nr = self.row + drow
        if nc < 0 or nc >= COLS or nr < 0 or nr >= ROWS:
            return False
        return game_map.get(nc, nr) == EMPTY

    def shoot(self):
        cx = self.col * CELL_SIZE + CELL_SIZE // 2
        cy = self.row * CELL_SIZE + CELL_SIZE // 2
        vec = DIR_VEC[self.direction]
        bx = cx + vec[0] * (CELL_SIZE // 2 + 2)
        by = cy + vec[1] * (CELL_SIZE // 2 + 2)
        return Bullet(bx, by, self.direction)

    def update(self):
        if self.shoot_cd > 0:
            self.shoot_cd -= 1

    def draw(self, surface):
        if not self.alive:
            return
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        pygame.draw.rect(surface, COLOR_GREEN, rect, border_radius=3)
        pygame.draw.rect(surface, COLOR_DARK_GREEN, rect, 2, border_radius=3)
        pygame.draw.circle(surface, COLOR_DARK_GREEN, (cx, cy), 10)

        if self.direction == "up":
            pygame.draw.rect(surface, COLOR_DARK_GREEN, (cx - 3, self.y - 6, 6, self.height // 2 + 6))
        elif self.direction == "down":
            pygame.draw.rect(surface, COLOR_DARK_GREEN, (cx - 3, self.y + self.height // 2, 6, self.height // 2 + 6))
        elif self.direction == "left":
            pygame.draw.rect(surface, COLOR_DARK_GREEN, (self.x - 6, cy - 3, self.width // 2 + 6, 6))
        elif self.direction == "right":
            pygame.draw.rect(surface, COLOR_DARK_GREEN, (self.x + self.width // 2, cy - 3, self.width // 2 + 6, 6))

        for dx, dy, w, h in [
            (2, 2, 6, self.height - 4),
            (self.width - 8, 2, 6, self.height - 4),
        ]:
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x + dx, self.y + dy, w, h), border_radius=1)


def draw_hud(surface, tank, bullets, game_over=False):
    try:
        font = pygame.font.SysFont("simhei", 18)
    except Exception:
        font = pygame.font.Font(None, 18)

    if game_over:
        go_surf = font.render("💀 主将阵亡！游戏结束！按 R 重新开始", True, (255, 80, 80))
        surface.blit(go_surf, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 10))
        return

    info = [
        f"坐标: ({tank.col}, {tank.row})  方向: {tank.direction}",
        f"子弹数: {len(bullets)}",
        "WASD 移动 | J/空格 射击",
    ]
    for i, text in enumerate(info):
        surf = font.render(text, True, (200, 200, 200))
        surface.blit(surf, (10, 10 + i * 22))


def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("坦克大战")
    clock = pygame.time.Clock()

    def reset_game():
        return GameMap(), Tank(19, 28), [], False

    game_map, tank, bullets, game_over = reset_game()

    # 按键映射
    KEY_MAP = {
        pygame.K_w: (0, -1, "up"), pygame.K_UP: (0, -1, "up"),
        pygame.K_s: (0, 1, "down"), pygame.K_DOWN: (0, 1, "down"),
        pygame.K_a: (-1, 0, "left"), pygame.K_LEFT: (-1, 0, "left"),
        pygame.K_d: (1, 0, "right"), pygame.K_RIGHT: (1, 0, "right"),
    }

    held_dirs: dict[int, tuple[int, int, str]] = {}  # key -> (dcol, drow, dir_name)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in KEY_MAP:
                    dcol, drow, dir_name = KEY_MAP[event.key]
                    held_dirs[event.key] = (dcol, drow, dir_name)
                    # 新按键按下 → 立即尝试移动
                    if not game_over and tank.alive and tank.can_move_to(dcol, drow, game_map):
                        tank.direction = dir_name
                        tank.col += dcol
                        tank.row += drow
                        tank.move_timer = MOVE_DELAY
                elif event.key == pygame.K_r and game_over:
                    game_map, tank, bullets, game_over = reset_game()
                elif event.key in (pygame.K_j, pygame.K_SPACE):
                    if not game_over and tank.alive and tank.shoot_cd == 0:
                        bullets.append(tank.shoot())
                        tank.shoot_cd = tank.shoot_cd_max

            elif event.type == pygame.KEYUP:
                held_dirs.pop(event.key, None)

        # ── 更新逻辑 ──
        if not game_over:
            tank.update()

            # 长按自动重复移动
            if held_dirs:
                # 用最后按下的方向
                last_key = list(held_dirs.keys())[-1]
                dcol, drow, dir_name = held_dirs[last_key]
                tank.direction = dir_name

                if tank.move_timer > 0:
                    tank.move_timer -= 1
                else:
                    if tank.can_move_to(dcol, drow, game_map):
                        tank.col += dcol
                        tank.row += drow
                    tank.move_timer = MOVE_DELAY

            # 子弹更新
            for b in bullets[:]:
                b.update(game_map)
                if not b.alive:
                    bullets.remove(b)
                    continue
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

"""坦克大战 - 简单版"""

import pygame
import sys

# ── 游戏配置 ──
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色
COLOR_BLACK = (20, 20, 20)
COLOR_GREEN = (76, 175, 80)
COLOR_DARK_GREEN = (46, 125, 50)
COLOR_SAND = (194, 178, 128)
COLOR_RED = (220, 50, 50)
COLOR_GRAY = (120, 120, 120)


class Tank:
    """玩家坦克"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = 3
        self.direction = "up"  # up / down / left / right

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def clamp(self):
        """限制坦克不出边界"""
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

    def draw(self, surface):
        # 坦克主体（根据方向决定绘制方式）
        rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if self.direction == "up":
            # 车身
            pygame.draw.rect(surface, COLOR_GREEN, rect)
            pygame.draw.rect(surface, COLOR_DARK_GREEN, rect, 2)
            # 炮塔（圆形）
            cx = self.x + self.width // 2
            cy = self.y + self.height // 2
            pygame.draw.circle(surface, COLOR_DARK_GREEN, (cx, cy), 12)
            # 炮管
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (cx - 3, self.y - 8, 6, self.height // 2 + 8))
            # 履带
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x + 2, self.y + 2, 6, self.height - 4))
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x + self.width - 8, self.y + 2, 6, self.height - 4))

        elif self.direction == "down":
            pygame.draw.rect(surface, COLOR_GREEN, rect)
            pygame.draw.rect(surface, COLOR_DARK_GREEN, rect, 2)
            cx = self.x + self.width // 2
            cy = self.y + self.height // 2
            pygame.draw.circle(surface, COLOR_DARK_GREEN, (cx, cy), 12)
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (cx - 3, self.y + self.height // 2, 6, self.height // 2 + 8))
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x + 2, self.y + 2, 6, self.height - 4))
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x + self.width - 8, self.y + 2, 6, self.height - 4))

        elif self.direction == "left":
            pygame.draw.rect(surface, COLOR_GREEN, rect)
            pygame.draw.rect(surface, COLOR_DARK_GREEN, rect, 2)
            cx = self.x + self.width // 2
            cy = self.y + self.height // 2
            pygame.draw.circle(surface, COLOR_DARK_GREEN, (cx, cy), 12)
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x - 8, cy - 3, self.width // 2 + 8, 6))
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x + 2, self.y + 2, self.width - 4, 6))
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x + 2, self.y + self.height - 8, self.width - 4, 6))

        elif self.direction == "right":
            pygame.draw.rect(surface, COLOR_GREEN, rect)
            pygame.draw.rect(surface, COLOR_DARK_GREEN, rect, 2)
            cx = self.x + self.width // 2
            cy = self.y + self.height // 2
            pygame.draw.circle(surface, COLOR_DARK_GREEN, (cx, cy), 12)
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x + self.width // 2, cy - 3, self.width // 2 + 8, 6))
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x + 2, self.y + 2, self.width - 4, 6))
            pygame.draw.rect(surface, COLOR_DARK_GREEN,
                             (self.x + 2, self.y + self.height - 8, self.width - 4, 6))


def draw_grid(surface):
    """画地面网格"""
    grid_size = 40
    for x in range(0, SCREEN_WIDTH, grid_size):
        pygame.draw.line(surface, (50, 50, 50), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, grid_size):
        pygame.draw.line(surface, (50, 50, 50), (0, y), (SCREEN_WIDTH, y))


def draw_hud(surface, tank):
    """显示 HUD 信息"""
    font = pygame.font.SysFont("simhei", 18)
    info = [
        f"位置: ({tank.x}, {tank.y})",
        f"方向: {tank.direction}",
        "WASD / 方向键 移动",
    ]
    for i, text in enumerate(info):
        surf = font.render(text, True, (200, 200, 200))
        surface.blit(surf, (10, 10 + i * 22))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("坦克大战 - 简单版")
    clock = pygame.time.Clock()

    tank = Tank(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 20)

    # 用 set 记录当前按下的移动键，不受无关按键干扰
    pressed_keys = set()
    KEY_MAP = {
        pygame.K_w: "up", pygame.K_UP: "up",
        pygame.K_s: "down", pygame.K_DOWN: "down",
        pygame.K_a: "left", pygame.K_LEFT: "left",
        pygame.K_d: "right", pygame.K_RIGHT: "right",
    }
    DIR_VEC = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

    running = True
    while running:
        # ── 事件处理（KEYDOWN/KEYUP 记录按键状态） ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in KEY_MAP:
                    pressed_keys.add(event.key)
            elif event.type == pygame.KEYUP:
                pressed_keys.discard(event.key)

        # ── 根据当前按下的移动键决定方向和位移 ──
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
            # 归一化斜向移动（防止斜着走更快）
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707
            dx *= tank.speed
            dy *= tank.speed
            tank.move(round(dx), round(dy))
            tank.clamp()

        # ── 绘制 ──
        screen.fill(COLOR_BLACK)
        draw_grid(screen)
        tank.draw(screen)
        draw_hud(screen, tank)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

"""坦克类：基类、玩家坦克、AI 坦克"""

import random
import pygame

from const import (
    CELL_SIZE, COLS, ROWS, EMPTY, COMMANDER,
    COLOR_GREEN, COLOR_DARK_GREEN, COLOR_RED,
    DIR_VEC,
)
from bullet import Bullet


class BaseTank:
    """坦克基类"""

    def __init__(self, col, row, direction="up", team="player"):
        self.col = col
        self.row = row
        self.direction = direction
        self.team = team  # "player" or "ai"
        self.alive = True
        self.shoot_cd = 0
        self.shoot_cd_max = 18
        self.width = CELL_SIZE - 4
        self.height = CELL_SIZE - 4

    @property
    def x(self):
        return self.col * CELL_SIZE + 2

    @property
    def y(self):
        return self.row * CELL_SIZE + 2

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def color(self):
        return COLOR_GREEN if self.team == "player" else COLOR_RED

    @property
    def color_dark(self):
        return COLOR_DARK_GREEN if self.team == "player" else (180, 30, 30)

    def can_move_to(self, dcol, drow, game_map, all_tanks):
        nc = self.col + dcol
        nr = self.row + drow
        if nc < 0 or nc >= COLS or nr < 0 or nr >= ROWS:
            return False
        if not game_map.is_tank_passable(nc, nr):
            return False
        # 与其他坦克碰撞
        new_rect = pygame.Rect(nc * CELL_SIZE + 2, nr * CELL_SIZE + 2,
                               self.width, self.height)
        for t in all_tanks:
            if t is not self and t.alive and t.rect.colliderect(new_rect):
                return False
        return True

    def shoot(self):
        cx = self.col * CELL_SIZE + CELL_SIZE // 2
        cy = self.row * CELL_SIZE + CELL_SIZE // 2
        vec = DIR_VEC[self.direction]
        bx = cx + vec[0] * (CELL_SIZE // 2 + 2)
        by = cy + vec[1] * (CELL_SIZE // 2 + 2)
        return Bullet(bx, by, self.direction, team=self.team)

    def draw(self, surface):
        if not self.alive:
            return
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        pygame.draw.rect(surface, self.color, rect, border_radius=3)
        pygame.draw.rect(surface, self.color_dark, rect, 2, border_radius=3)
        pygame.draw.circle(surface, self.color_dark, (cx, cy), 10)

        if self.direction == "up":
            pygame.draw.rect(surface, self.color_dark,
                             (cx - 3, self.y - 6, 6, self.height // 2 + 6))
        elif self.direction == "down":
            pygame.draw.rect(surface, self.color_dark,
                             (cx - 3, self.y + self.height // 2, 6, self.height // 2 + 6))
        elif self.direction == "left":
            pygame.draw.rect(surface, self.color_dark,
                             (self.x - 6, cy - 3, self.width // 2 + 6, 6))
        elif self.direction == "right":
            pygame.draw.rect(surface, self.color_dark,
                             (self.x + self.width // 2, cy - 3, self.width // 2 + 6, 6))

        for dx, dy, w, h in [
            (2, 2, 6, self.height - 4),
            (self.width - 8, 2, 6, self.height - 4),
        ]:
            pygame.draw.rect(surface, self.color_dark,
                             (self.x + dx, self.y + dy, w, h), border_radius=1)


class PlayerTank(BaseTank):
    """玩家坦克 — 3 条命"""

    def __init__(self, col, row):
        super().__init__(col, row, "up", "player")
        self.lives = 3
        self.invincible = 0       # 无敌帧（重生后）
        self.move_timer = 0
        self.respawn_timer = 0    # 死亡后重生倒计时
        self.spawn_col = col
        self.spawn_row = row

    def update(self):
        if self.shoot_cd > 0:
            self.shoot_cd -= 1
        if self.invincible > 0:
            self.invincible -= 1
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer == 0:
                self._respawn()

    def _respawn(self):
        self.col = self.spawn_col
        self.row = self.spawn_row
        self.alive = True
        self.direction = "up"
        self.invincible = 90  # 1.5 秒无敌

    def die(self):
        self.alive = False
        self.lives -= 1
        if self.lives > 0:
            self.respawn_timer = 60  # 1 秒后重生
        return self.lives  # 返回剩余命数

    def draw(self, surface):
        if not self.alive:
            return
        # 无敌时闪烁
        if self.invincible > 0 and (self.invincible // 4) % 2 == 0:
            return
        super().draw(surface)

    def draw_hud_extra(self, surface, font):
        """绘制生命数"""
        text = f"❤️ × {self.lives}"
        surf = font.render(text, True, (255, 80, 80))
        surface.blit(surf, (COLS * CELL_SIZE - 120, 10))


class AITank(BaseTank):
    """AI 坦克 — 自动移动+射击"""

    def __init__(self, col, row):
        super().__init__(col, row, "down", "ai")
        self.dir_timer = random.randint(20, 60)
        self.shoot_cd_max = random.randint(25, 50)
        self.shoot_cd = random.randint(5, 20)
        self._all_dirs = ["up", "down", "left", "right"]

    def update(self, game_map, all_tanks, bullets):
        if not self.alive:
            return

        if self.shoot_cd > 0:
            self.shoot_cd -= 1

        self.dir_timer -= 1

        # 尝试向前移动
        dcol, drow = DIR_VEC[self.direction]
        if self.can_move_to(dcol, drow, game_map, all_tanks):
            self.col += dcol
            self.row += drow
        else:
            self._pick_new_dir(game_map, all_tanks)

        # 定时随机变向
        if self.dir_timer <= 0:
            self._pick_new_dir(game_map, all_tanks)
            self.dir_timer = random.randint(30, 90)

        # 射击
        if self.shoot_cd == 0:
            self.shoot_cd = self.shoot_cd_max
            bullets.append(self.shoot())

    def _pick_new_dir(self, game_map, all_tanks):
        random.shuffle(self._all_dirs)
        for d in self._all_dirs:
            dcol, drow = DIR_VEC[d]
            if self.can_move_to(dcol, drow, game_map, all_tanks):
                self.direction = d
                return
        self.direction = random.choice(self._all_dirs)

    @staticmethod
    def find_spawn_point(game_map, all_tanks, spawn_points):
        """找一个空的出生点"""
        random.shuffle(spawn_points)
        for col, row in spawn_points:
            if game_map.is_tank_passable(col, row):
                new_rect = pygame.Rect(col * CELL_SIZE + 2, row * CELL_SIZE + 2,
                                       CELL_SIZE - 4, CELL_SIZE - 4)
                blocked = any(
                    t.alive and t.rect.colliderect(new_rect)
                    for t in all_tanks
                )
                if not blocked:
                    return col, row
        return None

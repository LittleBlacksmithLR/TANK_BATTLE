"""子弹实体"""

import pygame
from const import (
    CELL, PLAY_W, PLAY_H,
    WALL, STEEL, BASE,
    DIR_VEC, C_BULLET_P, C_BULLET_E,
)


def _hit_wall_half(direction, x, y):
    """按子弹方向摧毁半格砖墙（经典坦克大战手感）"""
    from const import CELL, DIR_LEFT, DIR_RIGHT
    if direction in (DIR_LEFT, DIR_RIGHT):
        return 0b0101 if (x % CELL) < CELL // 2 else 0b1010
    return 0b0011 if (y % CELL) < CELL // 2 else 0b1100


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=4, team="player", power=0):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.speed = speed
        self.team = team
        self.power = power  # 玩家星级，3 可破钢
        self.alive = True
        self.radius = 3

        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        color = C_BULLET_P if team == "player" else C_BULLET_E
        pygame.draw.circle(self.image, (255, 255, 200), (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius - 1)
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update_move(self, game_map):
        """移动并检测地形，返回 (alive, hit_base)"""
        if not self.alive:
            return False, False

        vec = DIR_VEC[self.direction]
        steps = max(1, self.speed // 2)
        step_px = self.speed / steps
        hit_base = False
        can_break_steel = self.team == "player" and self.power >= 3

        for _ in range(steps):
            self.x += vec[0] * step_px
            self.y += vec[1] * step_px
            self.rect.center = (int(self.x), int(self.y))

            if self.x < 0 or self.x > PLAY_W or self.y < 0 or self.y > PLAY_H:
                self.alive = False
                return False, False

            col, row = int(self.x) // CELL, int(self.y) // CELL
            tile = game_map.get(col, row)

            if tile == WALL and game_map.wall_mask[row][col]:
                game_map.damage_wall(col, row, _hit_wall_half(self.direction, self.x, self.y))
                self.alive = False
                return False, False
            if tile == STEEL:
                if can_break_steel:
                    game_map.set(col, row, EMPTY)
                self.alive = False
                return False, False
            if tile == BASE:
                self.alive = False
                return False, True

        return True, False

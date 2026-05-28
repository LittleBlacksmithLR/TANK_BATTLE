"""子弹"""

import math
import pygame
from const import CELL_SIZE, COLOR_RED, DIR_VEC


class Bullet:
    def __init__(self, x, y, direction, speed=6):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.radius = 4
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def update(self, game_map):
        """移动子弹并检测碰撞"""
        if not self.alive:
            return

        vec = DIR_VEC[self.direction]
        self.x += vec[0] * self.speed
        self.y += vec[1] * self.speed

        # 边界检测
        if (self.x < 0 or self.x > 800 or
                self.y < 0 or self.y > 600):
            self.alive = False
            return

        # 与地图碰撞
        col, row = int(self.x // CELL_SIZE), int(self.y // CELL_SIZE)
        tile = game_map.get(col, row)

        if tile == 1:  # WALL → 击毁
            game_map.set(col, row, 0)
            self.alive = False
        elif tile == 2:  # STEEL → 子弹消失
            self.alive = False
        elif tile == 4:  # BUNKER → 子弹消失
            self.alive = False
        elif tile == 5:  # COMMANDER → 游戏结束（由上层处理）
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        pygame.draw.circle(surface, COLOR_RED,
                           (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 200),
                           (int(self.x), int(self.y)), self.radius - 1)

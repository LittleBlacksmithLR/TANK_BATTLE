"""子弹实体"""

import pygame
from const import (
    CELL, PLAY_W, PLAY_H,
    EMPTY, WALL, STEEL, WATER, BASE, COMMANDER,
    DIR_VEC, C_BULLET_P, C_BULLET_E,
)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=4, team="player"):
        super().__init__()
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.team = team
        self.alive = True
        self.radius = 3

        self.image = pygame.Surface((self.radius * 2, self.radius * 2))
        self.image.set_colorkey((0, 0, 0))
        color = C_BULLET_P if team == "player" else C_BULLET_E
        pygame.draw.circle(self.image, (255, 255, 200), (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius - 1)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, game_map):
        if not self.alive:
            return

        vec = DIR_VEC[self.direction]
        self.x += vec[0] * self.speed
        self.y += vec[1] * self.speed
        self.rect.center = (self.x, self.y)

        # 边界
        if self.x < 0 or self.x > PLAY_W or self.y < 0 or self.y > PLAY_H:
            self.alive = False
            return

        col, row = self.x // CELL, self.y // CELL
        tile = game_map.get(col, row)

        if tile == WALL:
            game_map.set(col, row, EMPTY)
            self.alive = False
        elif tile == STEEL:
            self.alive = False
        elif tile == BASE:
            self.alive = False

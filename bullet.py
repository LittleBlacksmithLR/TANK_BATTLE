"""子弹"""

import pygame
from const import CELL_SIZE, COLOR_RED, DIR_VEC, SCREEN_WIDTH, SCREEN_HEIGHT, EMPTY, WATER


class Bullet:
    def __init__(self, x, y, direction, speed=6, team="player"):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.radius = 4
        self.alive = True
        self.team = team

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def update(self, game_map):
        if not self.alive:
            return

        vec = DIR_VEC[self.direction]
        self.x += vec[0] * self.speed
        self.y += vec[1] * self.speed

        if (self.x < 0 or self.x > SCREEN_WIDTH or
                self.y < 0 or self.y > SCREEN_HEIGHT):
            self.alive = False
            return

        col, row = int(self.x // CELL_SIZE), int(self.y // CELL_SIZE)
        tile = game_map.get(col, row)

        if tile == 1:   # WALL
            game_map.set(col, row, EMPTY)
            self.alive = False
        elif tile == 2:  # STEEL
            self.alive = False
        elif tile == 4:  # BUNKER
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        color = (255, 255, 100) if self.team == "player" else (255, 100, 100)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 200),
                           (int(self.x), int(self.y)), self.radius - 1)

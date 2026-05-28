"""道具（占位，v2.3 实现）"""

import pygame
from const import CELL


class PowerUp(pygame.sprite.Sprite):
    TYPES = ["star", "helmet", "clock", "bomb", "shovel", "tank"]

    def __init__(self, col, row, ptype=None):
        super().__init__()
        self.col = col
        self.row = row
        self.ptype = ptype or "star"
        self.alive = True

        self.image = pygame.Surface((CELL - 4, CELL - 4))
        self.image.fill((255, 255, 0))
        pygame.draw.rect(self.image, (200, 200, 0), (0, 0, CELL - 4, CELL - 4), 2)
        self.rect = self.image.get_rect(topleft=(col * CELL + 2, row * CELL + 2))

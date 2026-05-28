"""道具"""

import math
import random
import pygame
from const import CELL, PU_TYPES, PU_STAR, PU_HELMET, PU_CLOCK, PU_BOMB, PU_SHOVEL, PU_TANK


_COLORS = {
    PU_STAR: ((255, 220, 60), (200, 160, 20)),
    PU_HELMET: ((180, 200, 255), (100, 120, 200)),
    PU_CLOCK: ((200, 180, 255), (120, 100, 180)),
    PU_BOMB: ((255, 100, 80), (180, 40, 30)),
    PU_SHOVEL: ((200, 160, 100), (140, 100, 60)),
    PU_TANK: ((100, 255, 120), (40, 180, 60)),
}


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, col, row, ptype=None):
        super().__init__()
        self.col = col
        self.row = row
        self.ptype = ptype or random.choice(PU_TYPES)
        self.alive = True
        self.lifetime_ms = 0

        s = CELL - 4
        self.image = pygame.Surface((s, s), pygame.SRCALPHA)
        fg, bg = _COLORS.get(self.ptype, ((255, 255, 0), (200, 200, 0)))
        self.image.fill(bg)
        pygame.draw.rect(self.image, fg, (2, 2, s - 4, s - 4), border_radius=2)
        self._draw_icon(fg)
        self.rect = self.image.get_rect(topleft=(col * CELL + 2, row * CELL + 2))

    def _draw_icon(self, color):
        cx, cy = (CELL - 4) // 2, (CELL - 4) // 2
        if self.ptype == PU_STAR:
            pts = []
            for i in range(5):
                a = math.radians(-90 + i * 72)
                pts.append((cx + 6 * math.cos(a), cy + 6 * math.sin(a)))
            pygame.draw.polygon(self.image, color, pts)
        elif self.ptype == PU_HELMET:
            pygame.draw.arc(self.image, color, (cx - 6, cy - 6, 12, 12), 0, 3.14, 2)
        elif self.ptype == PU_CLOCK:
            pygame.draw.circle(self.image, color, (cx, cy), 6, 1)
            pygame.draw.line(self.image, color, (cx, cy), (cx, cy - 4), 1)
        elif self.ptype == PU_BOMB:
            pygame.draw.circle(self.image, color, (cx, cy), 5)
        elif self.ptype == PU_SHOVEL:
            pygame.draw.rect(self.image, color, (cx - 2, cy - 5, 4, 8))
        elif self.ptype == PU_TANK:
            pygame.draw.rect(self.image, color, (cx - 5, cy - 3, 10, 6), border_radius=1)

    def update(self, dt_ms):
        self.lifetime_ms += dt_ms

"""基地/主将 — 被摧毁则游戏结束"""

import pygame
from const import CELL, C_BASE, C_DBASE, C_COMMAND, C_DCOMMAND


class Commander(pygame.sprite.Sprite):
    """主将（不可移动，被子弹击中则所属方失败）"""

    def __init__(self, col, row, team="player"):
        super().__init__()
        self.col = col
        self.row = row
        self.team = team
        self.alive = True

        self.image = pygame.Surface((CELL - 4, CELL - 4))
        self.image.fill(C_BASE)
        pygame.draw.rect(self.image, C_DBASE, (0, 0, CELL - 4, CELL - 4), 2)
        cx, cy = (CELL - 4) // 2, (CELL - 4) // 2
        pygame.draw.circle(self.image, C_COMMAND, (cx, cy), 6)
        pygame.draw.circle(self.image, C_DCOMMAND, (cx, cy), 6, 2)
        pygame.draw.line(self.image, (60, 40, 20), (cx, cy - 6), (cx, cy - 10), 2)
        pts = [(cx, cy - 10), (cx + 6, cy - 7), (cx, cy - 4)]
        pygame.draw.polygon(self.image, C_COMMAND, pts)

        self.rect = self.image.get_rect(topleft=(col * CELL + 2, row * CELL + 2))

    @property
    def grid_rect(self):
        return pygame.Rect(self.col * CELL, self.row * CELL, CELL, CELL)

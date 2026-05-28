"""游戏内 HUD"""

import pygame
from const import PLAY_W, HUD_W, SCREEN_H


class HUD:
    def __init__(self):
        self.font = self._try_font(16)
        self.big_font = self._try_font(22)
        self.small_font = self._try_font(13)

    @staticmethod
    def _try_font(size):
        try:
            return pygame.font.SysFont("simhei", size)
        except Exception:
            return pygame.font.Font(None, size)

    def draw(self, surface, player, ai_total, ai_killed, active_ai, level, score=0, freeze_ms=0):
        pygame.draw.rect(surface, (30, 30, 30), (PLAY_W, 0, HUD_W, SCREEN_H))
        pygame.draw.line(surface, (80, 80, 80), (PLAY_W, 0), (PLAY_W, SCREEN_H), 2)

        x = PLAY_W + 16
        y = 20

        surf = self.big_font.render(f"STAGE {level}", True, (200, 200, 200))
        surface.blit(surf, (x, y))
        y += 36

        self._label(surface, x, y, "SCORE")
        y += 18
        surface.blit(self.font.render(str(score), True, (255, 220, 100)), (x, y))
        y += 32

        self._label(surface, x, y, "LIFE")
        y += 18
        surface.blit(self.font.render("x" + str(player.lives), True, (255, 100, 100)), (x, y))
        y += 28

        self._label(surface, x, y, "STAR")
        y += 18
        stars = "*" * player.stars + "-" * (3 - player.stars)
        surface.blit(self.font.render(stars, True, (255, 220, 80)), (x, y))
        y += 32

        self._label(surface, x, y, "ENEMY")
        y += 18
        remaining = ai_total - ai_killed
        surface.blit(self.font.render(f"{remaining}/{ai_total}", True, (200, 150, 150)), (x, y))
        y += 28

        self._label(surface, x, y, "ACTIVE")
        y += 16
        surface.blit(self.small_font.render(str(active_ai), True, (200, 100, 100)), (x, y))
        y += 28

        if freeze_ms > 0:
            self._label(surface, x, y, "FREEZE")
            y += 16
            surface.blit(self.small_font.render(f"{freeze_ms // 1000}s", True, (150, 200, 255)), (x, y))

    def _label(self, surface, x, y, text):
        surf = self.small_font.render(text, True, (130, 130, 130))
        surface.blit(surf, (x, y))

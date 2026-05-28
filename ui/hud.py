"""游戏内 HUD"""

import pygame
from const import CELL, COLS, ROWS, PLAY_W, PLAY_H, HUD_W, SCREEN_W, SCREEN_H


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

    def draw(self, surface, player, ai_total, ai_killed, active_ai, level):
        # 右侧面板背景
        pygame.draw.rect(surface, (30, 30, 30), (PLAY_W, 0, HUD_W, SCREEN_H))
        pygame.draw.line(surface, (80, 80, 80), (PLAY_W, 0), (PLAY_W, SCREEN_H), 2)

        x = PLAY_W + 16
        y = 20
        gap = 28

        # 关卡
        surf = self.big_font.render(f"STAGE {level}", True, (200, 200, 200))
        surface.blit(surf, (x, y))
        y += 40

        # 生命
        self._draw_label(surface, x, y, "LIFE")
        y += 18
        hearts = "❤️" * player.lives
        surf = self.font.render(hearts, True, (255, 80, 80))
        surface.blit(surf, (x, y))
        y += 36

        # AI 剩余
        self._draw_label(surface, x, y, "ENEMY")
        y += 18
        remaining = ai_total - ai_killed
        surf = self.font.render(f"{remaining}/{ai_total}", True, (200, 150, 150))
        surface.blit(surf, (x, y))
        y += 30

        # 活跃 AI
        self._draw_label(surface, x, y, "ACTIVE")
        y += 16
        surf = self.small_font.render(f"{active_ai}", True, (200, 100, 100))
        surface.blit(surf, (x, y))

    @staticmethod
    def _draw_label(surface, x, y, text):
        try:
            font = pygame.font.SysFont("simhei", 14)
        except Exception:
            font = pygame.font.Font(None, 14)
        surf = font.render(text, True, (130, 130, 130))
        surface.blit(surf, (x, y))

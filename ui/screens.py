"""菜单和结束画面"""

import pygame
from const import SCREEN_W, SCREEN_H, C_BLACK


def _font(size):
    try:
        return pygame.font.SysFont("simhei", size)
    except Exception:
        return pygame.font.Font(None, size)


class TitleScreen:
    def __init__(self):
        self.title_font = _font(48)
        self.font = _font(18)

    def draw(self, surface, flash):
        surface.fill(C_BLACK)
        surf = self.title_font.render("坦克大战", True, (220, 180, 60))
        rect = surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 80))
        surface.blit(surf, rect)

        surf = _font(14).render("v2.5 完整版", True, (100, 100, 100))
        rect = surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 35))
        surface.blit(surf, rect)

        if flash:
            surf = self.font.render("按 ENTER 继续", True, (180, 180, 180))
            rect = surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30))
            surface.blit(surf, rect)

        tips = [
            "WASD / 方向键 — 移动",
            "J / 空格 — 射击",
            "ESC — 暂停",
        ]
        for i, tip in enumerate(tips):
            surf = _font(14).render(tip, True, (100, 100, 100))
            rect = surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 80 + i * 22))
            surface.blit(surf, rect)


class LevelSelectScreen:
    def __init__(self, total_levels):
        self.total = total_levels

    def draw(self, surface, level):
        surface.fill(C_BLACK)
        surf = _font(36).render("选择关卡", True, (200, 200, 200))
        surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 60)))

        surf = _font(48).render(f"STAGE {level}", True, (255, 220, 100))
        surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))

        surf = _font(16).render(f"共 {self.total} 关", True, (120, 120, 120))
        surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 50)))

        surf = _font(16).render("左右键选关  ENTER 开始  ESC 返回", True, (150, 150, 150))
        surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 100)))


class StageClearScreen:
    def draw(self, surface, level):
        surface.fill(C_BLACK)
        surf = _font(42).render(f"STAGE {level} CLEAR!", True, (100, 255, 150))
        surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 20)))
        surf = _font(18).render("按 ENTER 进入下一关", True, (150, 150, 150))
        surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 40)))


class PauseOverlay:
    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        surf = _font(40).render("暂停", True, (240, 240, 240))
        surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 20)))
        surf = _font(16).render("ESC 继续  |  Q 返回标题", True, (180, 180, 180))
        surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30)))


class GameOverScreen:
    def draw(self, surface, won, all_cleared=False):
        surface.fill(C_BLACK)
        if all_cleared:
            text, color = "通关！全部关卡完成", (255, 220, 80)
        elif won:
            text, color = "胜利！", (100, 255, 100)
        else:
            text, color = "失败", (255, 80, 80)

        surf = _font(42).render(text, True, color)
        surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30)))
        surf = _font(18).render("R 重新开始  |  Q 返回标题", True, (150, 150, 150))
        surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30)))

"""菜单和结束画面"""

import pygame
from const import SCREEN_W, SCREEN_H, C_BLACK, C_WHITE, C_GRAY


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

        # 标题
        surf = self.title_font.render("⚔ 坦克大战 ⚔", True, (220, 180, 60))
        rect = surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 80))
        surface.blit(surf, rect)

        # 版本
        surf = _font(14).render("v2.0", True, (100, 100, 100))
        rect = surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 35))
        surface.blit(surf, rect)

        # 闪烁提示
        if flash:
            surf = self.font.render("按 ENTER 开始游戏", True, (180, 180, 180))
            rect = surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30))
            surface.blit(surf, rect)

        # 操作说明
        tips = [
            "WASD / 方向键 — 移动",
            "J / 空格 — 射击",
        ]
        for i, tip in enumerate(tips):
            surf = _font(14).render(tip, True, (100, 100, 100))
            rect = surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 80 + i * 22))
            surface.blit(surf, rect)


class GameOverScreen:
    def draw(self, surface, won):
        surface.fill(C_BLACK)

        if won:
            text = "🎉 胜利！"
            color = (100, 255, 100)
        else:
            text = "💀 失败"
            color = (255, 80, 80)

        surf = _font(48).render(text, True, color)
        rect = surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30))
        surface.blit(surf, rect)

        surf = _font(18).render("按 R 重新开始  |  按 Q 返回标题", True, (150, 150, 150))
        rect = surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30))
        surface.blit(surf, rect)

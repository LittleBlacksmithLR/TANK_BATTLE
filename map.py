"""地图数据与绘制"""

import pygame
from const import (
    CELL_SIZE, COLS, ROWS,
    EMPTY, WALL, STEEL, WATER, BUNKER, COMMANDER,
    COLOR_WALL, COLOR_WALL_DARK, COLOR_STEEL, COLOR_STEEL_DARK,
    COLOR_WATER, COLOR_WATER_LIGHT, COLOR_BUNKER, COLOR_BUNKER_DARK,
    COLOR_COMMANDER, COLOR_COMMANDER_DARK,
)

#  0 = 空地  1 = 墙壁  2 = 钢铁  3 = 水  4 = 碉堡  5 = 主将
MAP_DATA = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0, 1, 1, 0, 2, 2, 0, 1, 1, 0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0],
    [0, 0, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 3, 3, 0, 0, 4, 5, 5, 4, 0, 0, 3, 3, 0, 0, 0, 0],
    [0, 0, 0, 0, 3, 3, 0, 0, 4, 4, 4, 4, 0, 0, 3, 3, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0, 1, 1, 0, 2, 2, 0, 1, 1, 0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


def tile_rect(col, row):
    """返回 (col, row) 对应格子的 pygame.Rect"""
    return pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)


def pos_to_grid(x, y):
    """像素坐标 → 格子坐标 (col, row)"""
    return x // CELL_SIZE, y // CELL_SIZE


class GameMap:
    def __init__(self):
        self.cols = COLS
        self.rows = ROWS
        self.data = [row[:] for row in MAP_DATA]  # 深拷贝

    def get(self, col, row):
        """获取指定格子的类型"""
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.data[row][col]
        return STEEL  # 越界视为钢铁

    def set(self, col, row, tile_type):
        """设置指定格子的类型"""
        if 0 <= col < self.cols and 0 <= row < self.rows:
            self.data[row][col] = tile_type

    def is_tank_passable(self, col, row):
        """坦克能否通过该格子"""
        t = self.get(col, row)
        return t in (EMPTY,)

    def is_bullet_passable(self, col, row):
        """子弹能否穿过该格子"""
        t = self.get(col, row)
        return t in (EMPTY, WATER)

    def draw(self, surface):
        """绘制地图"""
        for row in range(self.rows):
            for col in range(self.cols):
                t = self.data[row][col]
                rect = tile_rect(col, row)
                if t == WALL:
                    self._draw_wall(surface, rect)
                elif t == STEEL:
                    self._draw_steel(surface, rect)
                elif t == WATER:
                    self._draw_water(surface, rect)
                elif t == BUNKER:
                    self._draw_bunker(surface, rect)
                elif t == COMMANDER:
                    self._draw_commander(surface, rect)

    # ── 各种图块的绘制 ──

    def _draw_wall(self, surface, rect):
        pygame.draw.rect(surface, COLOR_WALL, rect)
        pygame.draw.rect(surface, COLOR_WALL_DARK, rect, 2)
        # 砖纹
        for y in range(rect.top, rect.bottom, CELL_SIZE // 2):
            for x in range(rect.left, rect.right, CELL_SIZE // 2):
                offset = 2 if ((y - rect.top) // (CELL_SIZE // 2)) % 2 == 0 else 0
                pygame.draw.line(surface, COLOR_WALL_DARK,
                                 (x + offset, y), (x + offset + CELL_SIZE // 2 - 2, y), 1)

    def _draw_steel(self, surface, rect):
        pygame.draw.rect(surface, COLOR_STEEL, rect)
        pygame.draw.rect(surface, COLOR_STEEL_DARK, rect, 2)
        # 钢纹十字
        cx = rect.centerx
        cy = rect.centery
        pygame.draw.line(surface, COLOR_STEEL_DARK, (rect.left + 4, cy), (rect.right - 4, cy), 2)
        pygame.draw.line(surface, COLOR_STEEL_DARK, (cx, rect.top + 4), (cx, rect.bottom - 4), 2)
        # 铆钉
        for (dx, dy) in [(6, 6), (6, -6), (-6, 6), (-6, -6)]:
            pygame.draw.circle(surface, COLOR_STEEL_DARK, (cx + dx, cy + dy), 3)

    def _draw_water(self, surface, rect):
        pygame.draw.rect(surface, COLOR_WATER, rect)
        # 水波纹
        cx = rect.centerx
        cy = rect.centery
        for i in range(3):
            offset = i * 5
            pygame.draw.arc(surface, COLOR_WATER_LIGHT,
                            (cx - 12 + offset, cy - 4, 16, 8), 0, 3.14, 2)
            pygame.draw.arc(surface, COLOR_WATER_LIGHT,
                            (cx - 8 - offset, cy + 4, 16, 8), 0, 3.14, 2)

    def _draw_bunker(self, surface, rect):
        pygame.draw.rect(surface, COLOR_BUNKER, rect)
        pygame.draw.rect(surface, COLOR_BUNKER_DARK, rect, 2)

    def _draw_commander(self, surface, rect):
        # 先画碉堡底色
        pygame.draw.rect(surface, COLOR_BUNKER, rect)
        pygame.draw.rect(surface, COLOR_BUNKER_DARK, rect, 2)
        # 主将：金色旗帜/标志
        cx, cy = rect.centerx, rect.centery
        pygame.draw.circle(surface, COLOR_COMMANDER, (cx, cy), 8)
        pygame.draw.circle(surface, COLOR_COMMANDER_DARK, (cx, cy), 8, 2)
        # 旗杆
        pygame.draw.line(surface, (100, 80, 50), (cx, cy - 8), (cx, cy - 14), 2)
        # 旗帜
        flag_pts = [(cx, cy - 14), (cx + 8, cy - 11), (cx, cy - 8)]
        pygame.draw.polygon(surface, COLOR_COMMANDER, flag_pts)

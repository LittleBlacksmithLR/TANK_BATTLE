"""地图数据与绘制"""

import pygame
from const import (
    CELL_SIZE, COLS, ROWS,
    EMPTY, WALL, STEEL, WATER, BUNKER, COMMANDER,
    COLOR_WALL, COLOR_WALL_DARK, COLOR_STEEL, COLOR_STEEL_DARK,
    COLOR_WATER, COLOR_WATER_LIGHT, COLOR_BUNKER, COLOR_BUNKER_DARK,
    COLOR_COMMANDER, COLOR_COMMANDER_DARK,
)


def tile_rect(col, row):
    return pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)


def pos_to_grid(x, y):
    return x // CELL_SIZE, y // CELL_SIZE


def _generate_map():
    """程序化生成 40×30 地图"""
    data = [[EMPTY] * COLS for _ in range(ROWS)]

    def place(col, row, tile, w=1, h=1):
        for r in range(row, row + h):
            for c in range(col, col + w):
                if 0 <= r < ROWS and 0 <= c < COLS:
                    data[r][c] = tile

    # ══════════════════════════════════════════
    # 四角砖墙集群（每个集群 6×3）
    # ══════════════════════════════════════════
    # 左上角
    place(1, 2, WALL, 3, 3)
    place(6, 1, WALL, 3, 3)
    place(3, 5, WALL, 2, 1)
    # 右上角
    place(31, 2, WALL, 3, 3)
    place(36, 1, WALL, 3, 3)
    place(35, 5, WALL, 2, 1)
    # 左下角
    place(1, 25, WALL, 3, 3)
    place(6, 26, WALL, 3, 3)
    place(3, 24, WALL, 2, 1)
    # 右下角
    place(31, 25, WALL, 3, 3)
    place(36, 26, WALL, 3, 3)
    place(35, 24, WALL, 2, 1)

    # ══════════════════════════════════════════
    # 两侧钢铁
    # ══════════════════════════════════════════
    place(10, 4, STEEL, 2, 2)
    place(28, 4, STEEL, 2, 2)
    place(10, 24, STEEL, 2, 2)
    place(28, 24, STEEL, 2, 2)

    # 中部两侧钢铁
    place(8, 12, STEEL, 2, 2)
    place(30, 12, STEEL, 2, 2)
    place(8, 16, STEEL, 2, 2)
    place(30, 16, STEEL, 2, 2)

    # ══════════════════════════════════════════
    # 水域 — 横向河 + 纵向河
    # ══════════════════════════════════════════
    # 上横河 (row 7~8)
    place(13, 7, WATER, 14, 2)
    # 下横河 (row 21~22)
    place(13, 21, WATER, 14, 2)
    # 左纵河 (col 12~13)
    place(12, 9, WATER, 2, 12)
    # 右纵河 (col 26~27)
    place(26, 9, WATER, 2, 12)

    # ══════════════════════════════════════════
    # 中央碉堡 (6×6) + 主将
    # ══════════════════════════════════════════
    place(17, 12, BUNKER, 6, 6)
    place(19, 14, COMMANDER, 2, 2)

    # ══════════════════════════════════════════
    # 碉堡周围的附加墙壁路障
    # ══════════════════════════════════════════
    place(16, 11, WALL, 1, 1)
    place(23, 11, WALL, 1, 1)
    place(16, 18, WALL, 1, 1)
    place(23, 18, WALL, 1, 1)
    place(15, 14, WALL, 1, 2)
    place(24, 14, WALL, 1, 2)

    # ══════════════════════════════════════════
    # 散落的小墙块（增加趣味）
    # ══════════════════════════════════════════
    place(14, 11, WALL, 1, 1)
    place(25, 11, WALL, 1, 1)
    place(14, 18, WALL, 1, 1)
    place(25, 18, WALL, 1, 1)

    return data


MAP_DATA = _generate_map()


class GameMap:
    def __init__(self):
        self.cols = COLS
        self.rows = ROWS
        self.data = [row[:] for row in MAP_DATA]

    def get(self, col, row):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.data[row][col]
        return STEEL

    def set(self, col, row, tile_type):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            self.data[row][col] = tile_type

    def is_tank_passable(self, col, row):
        return self.get(col, row) == EMPTY

    def is_bullet_passable(self, col, row):
        t = self.get(col, row)
        return t in (EMPTY, WATER)

    def draw(self, surface):
        for row in range(self.rows):
            for col in range(self.cols):
                t = self.data[row][col]
                if t == EMPTY:
                    continue
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

    # ── 绘制方法 ──

    def _draw_wall(self, surface, rect):
        pygame.draw.rect(surface, COLOR_WALL, rect)
        pygame.draw.rect(surface, COLOR_WALL_DARK, rect, 2)
        hs = CELL_SIZE // 2
        for y in range(rect.top, rect.bottom, hs):
            for x in range(rect.left, rect.right, hs):
                offset = 2 if ((y - rect.top) // hs) % 2 == 0 else 0
                pygame.draw.line(surface, COLOR_WALL_DARK,
                                 (x + offset, y), (x + offset + hs - 2, y), 1)

    def _draw_steel(self, surface, rect):
        pygame.draw.rect(surface, COLOR_STEEL, rect)
        pygame.draw.rect(surface, COLOR_STEEL_DARK, rect, 2)
        cx = rect.centerx
        cy = rect.centery
        pygame.draw.line(surface, COLOR_STEEL_DARK, (rect.left + 4, cy), (rect.right - 4, cy), 2)
        pygame.draw.line(surface, COLOR_STEEL_DARK, (cx, rect.top + 4), (cx, rect.bottom - 4), 2)
        for (dx, dy) in [(6, 6), (6, -6), (-6, 6), (-6, -6)]:
            pygame.draw.circle(surface, COLOR_STEEL_DARK, (cx + dx, cy + dy), 3)

    def _draw_water(self, surface, rect):
        pygame.draw.rect(surface, COLOR_WATER, rect)
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
        pygame.draw.rect(surface, COLOR_BUNKER, rect)
        pygame.draw.rect(surface, COLOR_BUNKER_DARK, rect, 2)
        cx, cy = rect.centerx, rect.centery
        pygame.draw.circle(surface, COLOR_COMMANDER, (cx, cy), 10)
        pygame.draw.circle(surface, COLOR_COMMANDER_DARK, (cx, cy), 10, 2)
        pygame.draw.line(surface, (100, 80, 50), (cx, cy - 10), (cx, cy - 18), 2)
        flag_pts = [(cx, cy - 18), (cx + 10, cy - 14), (cx, cy - 10)]
        pygame.draw.polygon(surface, COLOR_COMMANDER, flag_pts)

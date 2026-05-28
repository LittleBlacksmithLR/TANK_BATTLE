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
    """程序化生成 40×30 地图 — 双阵营布局"""
    data = [[EMPTY] * COLS for _ in range(ROWS)]

    def place(col, row, tile, w=1, h=1):
        for r in range(row, row + h):
            for c in range(col, col + w):
                if 0 <= r < ROWS and 0 <= c < COLS:
                    data[r][c] = tile

    # ══════════════════════════════════════════
    # A 方（AI）基地 — 顶部
    # ══════════════════════════════════════════
    # 外墙
    place(16, 2, WALL, 8, 1)    # 上
    place(16, 2, WALL, 1, 6)    # 左
    place(23, 2, WALL, 1, 6)    # 右
    place(16, 7, WALL, 8, 1)    # 下
    # 底部留缺口 (18, 7)-(19, 7)
    place(16, 7, WALL, 2, 1)    # 下左
    place(22, 7, WALL, 2, 1)    # 下右
    # 内部主将
    place(19, 4, COMMANDER)     # A 方主将

    # ══════════════════════════════════════════
    # B 方（玩家）基地 — 底部
    # ══════════════════════════════════════════
    place(16, 22, WALL, 8, 1)   # 上
    place(16, 22, WALL, 1, 6)   # 左
    place(23, 22, WALL, 1, 6)   # 右
    place(16, 27, WALL, 8, 1)   # 下
    # 顶部留缺口 (18, 22)-(19, 22)
    place(16, 22, WALL, 2, 1)   # 上左
    place(22, 22, WALL, 2, 1)   # 上右
    # 内部主将
    place(19, 24, COMMANDER)    # B 方主将

    # ══════════════════════════════════════════
    # 四角砖墙集群
    # ══════════════════════════════════════════
    # 左上
    place(1, 10, WALL, 3, 3)
    place(6, 9, WALL, 3, 3)
    place(3, 13, WALL, 2, 1)
    # 右上
    place(31, 10, WALL, 3, 3)
    place(36, 9, WALL, 3, 3)
    place(35, 13, WALL, 2, 1)
    # 左下
    place(1, 17, WALL, 3, 3)
    place(6, 18, WALL, 3, 3)
    place(3, 16, WALL, 2, 1)
    # 右下
    place(31, 17, WALL, 3, 3)
    place(36, 18, WALL, 3, 3)
    place(35, 16, WALL, 2, 1)

    # ══════════════════════════════════════════
    # 钢铁壁垒
    # ══════════════════════════════════════════
    place(10, 10, STEEL, 2, 2)
    place(28, 10, STEEL, 2, 2)
    place(10, 18, STEEL, 2, 2)
    place(28, 18, STEEL, 2, 2)
    # 中场两侧
    place(8, 14, STEEL, 2, 2)
    place(30, 14, STEEL, 2, 2)

    # ══════════════════════════════════════════
    # 水域 — 横向分隔河道
    # ══════════════════════════════════════════
    place(13, 11, WATER, 14, 2)

    # ══════════════════════════════════════════
    # 散落路障
    # ══════════════════════════════════════════
    place(14, 14, WALL, 2, 1)
    place(24, 14, WALL, 2, 1)
    place(14, 15, WALL, 2, 1)
    place(24, 15, WALL, 2, 1)

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

    # ── 绘制 ──

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
        cx, cy = rect.centerx, rect.centery
        pygame.draw.line(surface, COLOR_STEEL_DARK, (rect.left + 4, cy), (rect.right - 4, cy), 2)
        pygame.draw.line(surface, COLOR_STEEL_DARK, (cx, rect.top + 4), (cx, rect.bottom - 4), 2)
        for (dx, dy) in [(6, 6), (6, -6), (-6, 6), (-6, -6)]:
            pygame.draw.circle(surface, COLOR_STEEL_DARK, (cx + dx, cy + dy), 3)

    def _draw_water(self, surface, rect):
        pygame.draw.rect(surface, COLOR_WATER, rect)
        cx, cy = rect.centerx, rect.centery
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
        pygame.draw.rect(surface, (200, 180, 150), rect)
        pygame.draw.rect(surface, (160, 140, 110), rect, 2)
        cx, cy = rect.centerx, rect.centery
        pygame.draw.circle(surface, COLOR_COMMANDER, (cx, cy), 10)
        pygame.draw.circle(surface, COLOR_COMMANDER_DARK, (cx, cy), 10, 2)
        pygame.draw.line(surface, (100, 80, 50), (cx, cy - 10), (cx, cy - 16), 2)
        flag_pts = [(cx, cy - 16), (cx + 9, cy - 12), (cx, cy - 8)]
        pygame.draw.polygon(surface, COLOR_COMMANDER, flag_pts)

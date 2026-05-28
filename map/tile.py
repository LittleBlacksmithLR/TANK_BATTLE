"""图块定义与地图类"""

import pygame
from const import (
    CELL, COLS, ROWS, PLAY_W, PLAY_H,
    EMPTY, WALL, STEEL, WATER, BASE, COMMANDER,
    C_WALL, C_DWALL, C_STEEL, C_DSTEEL,
    C_WATER, C_LWATER, C_BASE, C_DBASE,
    C_COMMAND, C_DCOMMAND,
)


def tile_rect(col, row):
    return pygame.Rect(col * CELL, row * CELL, CELL, CELL)


def pos_to_grid(x, y):
    return x // CELL, y // CELL


class GameMap:
    """26×26 地图"""

    def __init__(self, data=None):
        if data:
            self.data = [row[:] for row in data]
        else:
            self.data = [[EMPTY] * COLS for _ in range(ROWS)]

    def get(self, col, row):
        if 0 <= col < COLS and 0 <= row < ROWS:
            return self.data[row][col]
        return STEEL  # 边界视为钢铁

    def set(self, col, row, val):
        if 0 <= col < COLS and 0 <= row < ROWS:
            self.data[row][col] = val

    def is_tank_passable(self, col, row):
        t = self.get(col, row)
        return t == EMPTY

    def clone(self):
        return GameMap(self.data)

    # ── 绘制 ──
    def draw(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
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
                elif t == BASE:
                    self._draw_base(surface, rect)
                elif t == COMMANDER:
                    self._draw_commander(surface, rect)

    _WALL_SURF = None
    _STEEL_SURF = None
    _WATER_SURF = None
    _BASE_SURF = None
    _CMD_SURF = None

    @classmethod
    def _init_surfaces(cls):
        if cls._WALL_SURF is not None:
            return
        s = CELL
        hs = s // 2

        # 砖墙
        w = pygame.Surface((s, s))
        w.fill(C_WALL)
        pygame.draw.rect(w, C_DWALL, (0, 0, s, s), 2)
        for y in range(0, s, hs):
            for x in range(0, s, hs):
                off = 2 if (y // hs) % 2 == 0 else 0
                pygame.draw.line(w, C_DWALL, (x + off, y), (x + off + hs - 2, y), 1)
        cls._WALL_SURF = w

        # 钢铁
        st = pygame.Surface((s, s))
        st.fill(C_STEEL)
        pygame.draw.rect(st, C_DSTEEL, (0, 0, s, s), 2)
        cx, cy = s // 2, s // 2
        pygame.draw.line(st, C_DSTEEL, (4, cy), (s - 4, cy), 2)
        pygame.draw.line(st, C_DSTEEL, (cx, 4), (cx, s - 4), 2)
        for dx, dy in [(6, 6), (6, -6), (-6, 6), (-6, -6)]:
            pygame.draw.circle(st, C_DSTEEL, (cx + dx, cy + dy), 2)
        cls._STEEL_SURF = st

        # 水域
        wa = pygame.Surface((s, s))
        wa.fill(C_WATER)
        cx, cy = s // 2, s // 2
        for i in range(3):
            off = i * 4
            pygame.draw.arc(wa, C_LWATER, (cx - 8 + off, cy - 3, 12, 6), 0, 3.14, 1)
            pygame.draw.arc(wa, C_LWATER, (cx - 5 - off, cy + 3, 12, 6), 0, 3.14, 1)
        cls._WATER_SURF = wa

        # 基地围墙
        b = pygame.Surface((s, s))
        b.fill(C_BASE)
        pygame.draw.rect(b, C_DBASE, (0, 0, s, s), 2)
        cls._BASE_SURF = b

        # 主将
        c = pygame.Surface((s, s))
        c.fill(C_BASE)
        pygame.draw.rect(c, C_DBASE, (0, 0, s, s), 2)
        cx, cy = s // 2, s // 2
        pygame.draw.circle(c, C_COMMAND, (cx, cy), 7)
        pygame.draw.circle(c, C_DCOMMAND, (cx, cy), 7, 2)
        pygame.draw.line(c, (80, 60, 30), (cx, cy - 7), (cx, cy - 12), 2)
        pts = [(cx, cy - 12), (cx + 7, cy - 9), (cx, cy - 6)]
        pygame.draw.polygon(c, C_COMMAND, pts)
        cls._CMD_SURF = c

    def _draw_wall(self, surface, rect):
        self._init_surfaces()
        surface.blit(self._WALL_SURF, rect)

    def _draw_steel(self, surface, rect):
        self._init_surfaces()
        surface.blit(self._STEEL_SURF, rect)

    def _draw_water(self, surface, rect):
        self._init_surfaces()
        surface.blit(self._WATER_SURF, rect)

    def _draw_base(self, surface, rect):
        self._init_surfaces()
        surface.blit(self._BASE_SURF, rect)

    def _draw_commander(self, surface, rect):
        self._init_surfaces()
        surface.blit(self._CMD_SURF, rect)

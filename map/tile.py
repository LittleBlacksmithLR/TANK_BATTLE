"""图块定义与地图类"""

import pygame
from const import (
    CELL, COLS, ROWS,
    EMPTY, WALL, STEEL, WATER, BASE, COMMANDER, ICE, FOREST,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    C_WALL, C_DWALL, C_STEEL, C_DSTEEL,
    C_WATER, C_LWATER, C_ICE, C_DICE,
    C_FOREST, C_DFOREST, C_BASE, C_DBASE,
)


def tile_rect(col, row):
    return pygame.Rect(col * CELL, row * CELL, CELL, CELL)


def pos_to_grid(x, y):
    return x // CELL, y // CELL


# 砖墙四象限 bit: TL=1, TR=2, BL=4, BR=8
def hit_quadrant(x, y):
    lx, ly = x % CELL, y % CELL
    mid = CELL // 2
    if lx < mid:
        return 1 if ly < mid else 4
    return 2 if ly < mid else 8


def hit_wall_half(direction, x, y):
    """按子弹方向摧毁半格砖墙（经典坦克大战手感）"""
    if direction in (DIR_LEFT, DIR_RIGHT):
        return 0b0101 if (x % CELL) < CELL // 2 else 0b1010
    return 0b0011 if (y % CELL) < CELL // 2 else 0b1100


class GameMap:
    """26×26 地图（砖墙半格摧毁、冰面、森林）"""

    def __init__(self, data=None):
        if data:
            self.data = [row[:] for row in data]
        else:
            self.data = [[EMPTY] * COLS for _ in range(ROWS)]
        self.wall_mask = [[0] * COLS for _ in range(ROWS)]
        self._init_wall_masks()
        self._base_backup = None

    def _init_wall_masks(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.data[r][c] == WALL:
                    self.wall_mask[r][c] = 0b1111

    def get(self, col, row):
        if 0 <= col < COLS and 0 <= row < ROWS:
            return self.data[row][col]
        return STEEL

    def set(self, col, row, val):
        if 0 <= col < COLS and 0 <= row < ROWS:
            self.data[row][col] = val
            if val == WALL:
                self.wall_mask[row][col] = 0b1111
            elif val != WALL:
                self.wall_mask[row][col] = 0

    def has_wall(self, col, row):
        return self.get(col, row) == WALL and self.wall_mask[row][col] != 0

    def damage_wall(self, col, row, mask_bits):
        if self.get(col, row) != WALL:
            return False
        self.wall_mask[row][col] &= ~mask_bits
        if self.wall_mask[row][col] == 0:
            self.data[row][col] = EMPTY
        return True

    def is_tank_passable(self, col, row):
        t = self.get(col, row)
        return t in (EMPTY, ICE, FOREST)

    def is_on_ice(self, col, row):
        return self.get(col, row) == ICE

    def blocks_bullet(self, col, row, can_break_steel=False):
        t = self.get(col, row)
        if t == WALL and self.wall_mask[row][col]:
            return True
        if t == STEEL and not can_break_steel:
            return True
        if t == BASE:
            return True
        return False

    def blocks_sight(self, col, row):
        t = self.get(col, row)
        if t == WALL and self.wall_mask[row][col]:
            return True
        if t in (STEEL, WATER):
            return True
        return False

    def has_line_of_sight(self, c1, r1, c2, r2):
        if c1 == c2:
            for r in range(min(r1, r2) + 1, max(r1, r2)):
                if self.blocks_sight(c1, r):
                    return False
            return True
        if r1 == r2:
            for c in range(min(c1, c2) + 1, max(c1, c2)):
                if self.blocks_sight(c, r1):
                    return False
            return True
        return False

    def find_base_walls(self, cmd_col, cmd_row, radius=4):
        tiles = []
        for r in range(max(0, cmd_row - radius), min(ROWS, cmd_row + radius + 1)):
            for c in range(max(0, cmd_col - radius), min(COLS, cmd_col + radius + 1)):
                if self.get(c, r) == WALL:
                    tiles.append((c, r))
        return tiles

    def upgrade_walls_to_steel(self, tiles):
        self._base_backup = []
        for c, r in tiles:
            self._base_backup.append((c, r, self.data[r][c], self.wall_mask[r][c]))
            self.data[r][c] = STEEL
            self.wall_mask[r][c] = 0

    def restore_base_walls(self):
        if not self._base_backup:
            return
        for c, r, tile, mask in self._base_backup:
            self.data[r][c] = tile
            self.wall_mask[r][c] = mask
        self._base_backup = None

    def draw_terrain(self, surface, skip_commander=False):
        for row in range(ROWS):
            for col in range(COLS):
                t = self.data[row][col]
                if t == EMPTY:
                    continue
                if skip_commander and t == COMMANDER:
                    continue
                rect = tile_rect(col, row)
                if t == WALL:
                    self._draw_wall(surface, rect, self.wall_mask[row][col])
                elif t == STEEL:
                    self._draw_steel(surface, rect)
                elif t == WATER:
                    self._draw_water(surface, rect)
                elif t == ICE:
                    self._draw_ice(surface, rect)
                elif t == BASE:
                    self._draw_base(surface, rect)
                elif t == COMMANDER and not skip_commander:
                    self._draw_commander_tile(surface, rect)

    def draw_forest_overlay(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.data[row][col] == FOREST:
                    self._draw_forest(surface, tile_rect(col, row))

    _WALL_SURF = None
    _STEEL_SURF = None
    _WATER_SURF = None
    _ICE_SURF = None
    _FOREST_SURF = None
    _BASE_SURF = None

    @classmethod
    def _init_surfaces(cls):
        if cls._WALL_SURF is not None:
            return
        s, hs = CELL, CELL // 2

        w = pygame.Surface((s, s))
        w.fill(C_WALL)
        pygame.draw.rect(w, C_DWALL, (0, 0, s, s), 2)
        for y in range(0, s, hs):
            for x in range(0, s, hs):
                off = 2 if (y // hs) % 2 == 0 else 0
                pygame.draw.line(w, C_DWALL, (x + off, y), (x + off + hs - 2, y), 1)
        cls._WALL_SURF = w

        st = pygame.Surface((s, s))
        st.fill(C_STEEL)
        pygame.draw.rect(st, C_DSTEEL, (0, 0, s, s), 2)
        cx, cy = s // 2, s // 2
        pygame.draw.line(st, C_DSTEEL, (4, cy), (s - 4, cy), 2)
        pygame.draw.line(st, C_DSTEEL, (cx, 4), (cx, s - 4), 2)
        cls._STEEL_SURF = st

        wa = pygame.Surface((s, s))
        wa.fill(C_WATER)
        cx, cy = s // 2, s // 2
        for i in range(3):
            off = i * 4
            pygame.draw.arc(wa, C_LWATER, (cx - 8 + off, cy - 3, 12, 6), 0, 3.14, 1)
        cls._WATER_SURF = wa

        ic = pygame.Surface((s, s))
        ic.fill(C_ICE)
        pygame.draw.rect(ic, C_DICE, (0, 0, s, s), 1)
        for i in range(0, s, 6):
            pygame.draw.line(ic, C_DICE, (i, 0), (i, s), 1)
        cls._ICE_SURF = ic

        fo = pygame.Surface((s, s), pygame.SRCALPHA)
        fo.fill((*C_FOREST, 200))
        for i in range(4):
            pygame.draw.circle(fo, C_DFOREST, (6 + i * 5, 8 + (i % 2) * 6), 4)
        cls._FOREST_SURF = fo

        b = pygame.Surface((s, s))
        b.fill(C_BASE)
        pygame.draw.rect(b, C_DBASE, (0, 0, s, s), 2)
        cls._BASE_SURF = b

    def _draw_wall(self, surface, rect, mask):
        self._init_surfaces()
        if mask == 0b1111:
            surface.blit(self._WALL_SURF, rect)
            return
        half = CELL // 2
        quads = [
            (0b0001, rect.left, rect.top, half, half),
            (0b0010, rect.left + half, rect.top, half, half),
            (0b0100, rect.left, rect.top + half, half, half),
            (0b1000, rect.left + half, rect.top + half, half, half),
        ]
        for bit, x, y, w, h in quads:
            if mask & bit:
                sub = pygame.Rect(x, y, w, h)
                surface.blit(self._WALL_SURF, sub, pygame.Rect(0 if bit in (1, 4) else half, 0 if bit in (1, 2) else half, w, h))

    def _draw_steel(self, surface, rect):
        self._init_surfaces()
        surface.blit(self._STEEL_SURF, rect)

    def _draw_water(self, surface, rect):
        self._init_surfaces()
        surface.blit(self._WATER_SURF, rect)

    def _draw_ice(self, surface, rect):
        self._init_surfaces()
        surface.blit(self._ICE_SURF, rect)

    def _draw_forest(self, surface, rect):
        self._init_surfaces()
        surface.blit(self._FOREST_SURF, rect)

    def _draw_base(self, surface, rect):
        self._init_surfaces()
        surface.blit(self._BASE_SURF, rect)

    def _draw_commander_tile(self, surface, rect):
        self._draw_base(surface, rect)

    # 兼容旧接口
    def draw(self, surface):
        self.draw_terrain(surface, skip_commander=True)

"""关卡数据：JSON 加载 + 程序化回退"""

import json
import os
import random

from const import COLS, ROWS, EMPTY, WALL, STEEL, WATER, BASE, COMMANDER, ICE, FOREST, TILE_CHARS

_LEVELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "levels")


def _make_grid():
    return [[EMPTY] * COLS for _ in range(ROWS)]


def _place(grid, col, row, tile, w=1, h=1):
    for r in range(row, row + h):
        for c in range(col, col + w):
            if 0 <= r < ROWS and 0 <= c < COLS:
                grid[r][c] = tile


def _place_block(grid, col, row, tile):
    _place(grid, col, row, tile, 2, 2)


def _parse_map_rows(rows):
    g = _make_grid()
    for r, line in enumerate(rows[:ROWS]):
        for c, ch in enumerate(line[:COLS]):
            g[r][c] = TILE_CHARS.get(ch, EMPTY)
    return g


def level_count():
    if not os.path.isdir(_LEVELS_DIR):
        return 2
    return max(1, len([f for f in os.listdir(_LEVELS_DIR) if f.endswith(".json")]))


def _load_json(level_n):
    path = os.path.join(_LEVELS_DIR, f"level{level_n}.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    g = _parse_map_rows(cfg["map_rows"])
    cfg.setdefault("spawn_interval", 90)
    cfg["player_spawn"] = tuple(cfg["player_spawn"])
    cfg["ai_spawns"] = [tuple(p) for p in cfg["ai_spawns"]]
    return g, cfg


def _build_ai_types(cfg):
    if cfg.get("ai_types"):
        types = list(cfg["ai_types"])
        random.shuffle(types)
        return types
    total = cfg["ai_total"]
    types = []
    for _ in range(total):
        r = random.random()
        if r < 0.4:
            types.append("basic")
        elif r < 0.65:
            types.append("fast")
        elif r < 0.85:
            types.append("armor")
        else:
            types.append("elite")
    random.shuffle(types)
    return types


def get_level(n):
    data = _load_json(n)
    if data:
        g, cfg = data
        cfg["ai_types_queue"] = _build_ai_types(cfg)
        return g, cfg

    fallbacks = [_level1, _level2, _level3]
    idx = max(0, min(n - 1, len(fallbacks) - 1))
    g, cfg = fallbacks[idx]()
    cfg["ai_types_queue"] = _build_ai_types(cfg)
    return g, cfg


def _level1():
    g = _make_grid()
    _place(g, 10, 1, WALL, 3, 1)
    _place(g, 10, 1, WALL, 1, 3)
    _place(g, 12, 1, WALL, 1, 3)
    _place(g, 10, 3, WALL, 3, 1)
    _place(g, 11, 2, COMMANDER)
    _place_block(g, 2, 1, WALL)
    _place_block(g, 6, 0, WALL)
    _place_block(g, 18, 0, WALL)
    _place_block(g, 22, 1, WALL)
    _place_block(g, 4, 3, WALL)
    _place_block(g, 20, 3, WALL)
    _place_block(g, 2, 5, STEEL)
    _place_block(g, 22, 5, STEEL)
    _place_block(g, 8, 4, STEEL)
    _place_block(g, 16, 4, STEEL)
    _place(g, 6, 7, WATER, 14, 1)
    _place_block(g, 4, 9, WALL)
    _place_block(g, 20, 9, WALL)
    _place_block(g, 8, 10, WALL)
    _place_block(g, 16, 10, WALL)
    _place_block(g, 12, 9, WALL)
    _place(g, 10, 11, ICE, 6, 1)
    _place(g, 6, 14, WATER, 14, 1)
    _place_block(g, 2, 16, WALL)
    _place_block(g, 22, 16, WALL)
    _place(g, 8, 17, FOREST, 10, 2)
    _place_block(g, 2, 20, STEEL)
    _place_block(g, 22, 20, STEEL)
    _place(g, 10, 21, WALL, 2, 1)
    _place(g, 14, 21, WALL, 2, 1)
    _place(g, 10, 21, WALL, 1, 5)
    _place(g, 15, 21, WALL, 1, 5)
    _place(g, 12, 23, COMMANDER)
    cfg = {
        "level": 1, "ai_total": 20, "ai_max_active": 4, "player_lives": 3,
        "player_spawn": (12, 25),
        "ai_spawns": [(0, 0), (8, 0), (16, 0), (24, 0)],
        "spawn_interval": 90,
    }
    return g, cfg


def _level2():
    g = _make_grid()
    _place(g, 10, 1, WALL, 3, 1)
    _place(g, 10, 1, WALL, 1, 3)
    _place(g, 12, 1, WALL, 1, 3)
    _place(g, 10, 3, WALL, 3, 1)
    _place(g, 11, 2, COMMANDER)
    for bx in range(0, 26, 4):
        for by in range(4, 12, 3):
            _place_block(g, bx, by, WALL)
    _place(g, 0, 10, WATER, 4, 1)
    _place(g, 22, 10, WATER, 4, 1)
    _place(g, 6, 14, WATER, 14, 1)
    _place(g, 0, 16, WATER, 4, 1)
    _place(g, 22, 16, WATER, 4, 1)
    _place(g, 4, 12, ICE, 18, 2)
    _place_block(g, 8, 16, STEEL)
    _place_block(g, 16, 16, STEEL)
    _place(g, 2, 18, FOREST, 8, 3)
    _place(g, 16, 18, FOREST, 8, 3)
    _place(g, 10, 21, WALL, 2, 1)
    _place(g, 14, 21, WALL, 2, 1)
    _place(g, 10, 21, WALL, 1, 5)
    _place(g, 15, 21, WALL, 1, 5)
    _place(g, 12, 23, COMMANDER)
    cfg = {
        "level": 2, "ai_total": 25, "ai_max_active": 5, "player_lives": 3,
        "player_spawn": (12, 25),
        "ai_spawns": [(0, 0), (8, 0), (16, 0), (24, 0)],
        "spawn_interval": 75,
    }
    return g, cfg


def _level3():
    g = _make_grid()
    _place(g, 10, 1, WALL, 3, 1)
    _place(g, 10, 1, WALL, 1, 3)
    _place(g, 12, 1, WALL, 1, 3)
    _place(g, 10, 3, WALL, 3, 1)
    _place(g, 11, 2, COMMANDER)
    _place_block(g, 0, 0, STEEL)
    _place_block(g, 24, 0, STEEL)
    for bx in range(2, 24, 5):
        _place_block(g, bx, 5, WALL)
        _place_block(g, bx, 11, WALL)
        _place_block(g, bx, 17, WALL)
    _place(g, 1, 8, WATER, 24, 1)
    _place(g, 1, 15, WATER, 24, 1)
    _place(g, 6, 9, ICE, 14, 1)
    _place(g, 6, 16, ICE, 14, 1)
    _place(g, 0, 6, FOREST, 26, 2)
    _place(g, 0, 19, FOREST, 26, 2)
    _place(g, 10, 21, WALL, 2, 1)
    _place(g, 14, 21, WALL, 2, 1)
    _place(g, 10, 21, WALL, 1, 5)
    _place(g, 15, 21, WALL, 1, 5)
    _place(g, 12, 23, COMMANDER)
    cfg = {
        "level": 3, "ai_total": 30, "ai_max_active": 6, "player_lives": 3,
        "player_spawn": (12, 25),
        "ai_spawns": [(0, 0), (8, 0), (16, 0), (24, 0)],
        "spawn_interval": 60,
    }
    return g, cfg

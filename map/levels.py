"""关卡数据"""

from const import COLS, ROWS, EMPTY, WALL, STEEL, WATER, BASE, COMMANDER


def _make_grid():
    """创建空网格"""
    return [[EMPTY] * COLS for _ in range(ROWS)]


def _place(grid, col, row, tile, w=1, h=1):
    for r in range(row, row + h):
        for c in range(col, col + w):
            if 0 <= r < ROWS and 0 <= c < COLS:
                grid[r][c] = tile


def _place_block(grid, col, row, tile):
    """放置 2×2 方块"""
    _place(grid, col, row, tile, 2, 2)


# ═══════════════════════════════════════
# 关卡 1
# ═══════════════════════════════════════
def _level1():
    g = _make_grid()

    # ── AI 基地（顶部） ──
    _place(g, 10, 0, WALL, 6, 1)   # 上墙
    _place(g, 10, 0, WALL, 1, 5)   # 左墙
    _place(g, 15, 0, WALL, 1, 5)   # 右墙
    _place(g, 10, 4, WALL, 6, 1)   # 下墙
    _place(g, 12, 2, COMMANDER)    # AI 主将

    # ── 砖墙群（上半场） ──
    _place_block(g, 2, 1, WALL)
    _place_block(g, 6, 0, WALL)
    _place_block(g, 18, 0, WALL)
    _place_block(g, 22, 1, WALL)
    _place_block(g, 4, 3, WALL)
    _place_block(g, 20, 3, WALL)

    # ── 钢铁 ──
    _place_block(g, 2, 5, STEEL)
    _place_block(g, 22, 5, STEEL)
    _place_block(g, 8, 4, STEEL)
    _place_block(g, 16, 4, STEEL)

    # ── 水域 ──
    _place(g, 6, 7, WATER, 14, 1)

    # ── 中场防御墙 ──
    _place_block(g, 4, 9, WALL)
    _place_block(g, 20, 9, WALL)
    _place_block(g, 8, 10, WALL)
    _place_block(g, 16, 10, WALL)
    _place_block(g, 12, 9, WALL)

    # ── 水域（下半场） ──
    _place(g, 6, 14, WATER, 14, 1)

    # ── 砖墙群（下半场） ──
    _place_block(g, 2, 16, WALL)
    _place_block(g, 22, 16, WALL)
    _place_block(g, 4, 18, WALL)
    _place_block(g, 20, 18, WALL)

    # ── 钢铁 ──
    _place_block(g, 2, 20, STEEL)
    _place_block(g, 22, 20, STEEL)
    _place_block(g, 8, 19, STEEL)
    _place_block(g, 16, 19, STEEL)

    # ── 玩家基地（底部） ──
    _place(g, 10, 21, WALL, 6, 1)  # 上墙
    _place(g, 10, 21, WALL, 1, 5)  # 左墙
    _place(g, 15, 21, WALL, 1, 5)  # 右墙
    _place(g, 12, 23, COMMANDER)   # 玩家主将
    # 底部开口为入口（玩家从下方进入）

    cfg = {
        "level": 1,
        "ai_total": 20,
        "ai_max_active": 4,
        "player_lives": 3,
        "player_spawn": (12, 25),
        "ai_spawns": [(0, 0), (8, 0), (16, 0), (24, 0)],
    }
    return g, cfg


# ═══════════════════════════════════════
# 关卡 2（更复杂）
# ═══════════════════════════════════════
def _level2():
    g = _make_grid()

    # ── AI 基地 ──
    _place(g, 10, 0, WALL, 6, 1)
    _place(g, 10, 0, WALL, 1, 5)
    _place(g, 15, 0, WALL, 1, 5)
    _place(g, 10, 4, WALL, 6, 1)
    _place(g, 12, 2, COMMANDER)

    # ── 大量砖墙 ──
    for bx in range(0, 26, 4):
        for by in range(4, 12, 3):
            _place_block(g, bx, by, WALL)

    # ── 水域 ──
    _place(g, 0, 10, WATER, 4, 1)
    _place(g, 22, 10, WATER, 4, 1)
    _place(g, 6, 14, WATER, 14, 1)
    _place(g, 0, 16, WATER, 4, 1)
    _place(g, 22, 16, WATER, 4, 1)

    # ── 钢铁 ──
    _place_block(g, 8, 16, STEEL)
    _place_block(g, 16, 16, STEEL)
    _place_block(g, 10, 18, STEEL)

    # ── 玩家基地 ──
    _place(g, 10, 21, WALL, 6, 1)
    _place(g, 10, 21, WALL, 1, 5)
    _place(g, 15, 21, WALL, 1, 5)
    _place(g, 12, 23, COMMANDER)

    cfg = {
        "level": 2,
        "ai_total": 25,
        "ai_max_active": 5,
        "player_lives": 3,
        "player_spawn": (12, 25),
        "ai_spawns": [(0, 0), (8, 0), (16, 0), (24, 0)],
    }
    return g, cfg


def get_level(n):
    levels = [_level1, _level2]
    idx = max(0, min(n - 1, len(levels) - 1))
    return levels[idx]()

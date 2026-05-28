"""全局常量"""

import pygame

# ── 窗口尺寸 ──
CELL = 24                    # 半格尺寸 (px)
COLS = 26                    # 半格列数
ROWS = 26                    # 半格行数
PLAY_W = COLS * CELL         # 624  游戏区域宽度
PLAY_H = ROWS * CELL         # 624  游戏区域高度
HUD_W = 200                  # HUD 面板宽度
SCREEN_W = PLAY_W + HUD_W    # 832
SCREEN_H = 700               # 窗口高度

FPS = 60

# ── 图块类型 ──
EMPTY = 0
WALL = 1      # 砖墙（可摧毁）
STEEL = 2     # 钢铁（不可摧毁）
WATER = 3     # 水域
BASE = 4      # 基地围墙
COMMANDER = 5 # 主将

# ── 方向 ──
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3
DIR_VEC = {DIR_UP: (0, -1), DIR_DOWN: (0, 1), DIR_LEFT: (-1, 0), DIR_RIGHT: (1, 0)}
DIR_NAMES = {DIR_UP: "up", DIR_DOWN: "down", DIR_LEFT: "left", DIR_RIGHT: "right"}

# ── 调色板 ──
C_BLACK    = (20, 20, 20)
C_WHITE    = (240, 240, 240)
C_GRAY     = (100, 100, 100)
C_DARK     = (40, 40, 40)

C_GREEN    = (70, 170, 70)
C_DGREEN   = (45, 110, 45)
C_RED      = (210, 50, 50)
C_DRED     = (160, 30, 30)
C_YELLOW   = (240, 210, 60)

C_WALL     = (170, 120, 60)
C_DWALL    = (130, 90, 40)
C_STEEL    = (170, 170, 180)
C_DSTEEL   = (120, 120, 130)
C_WATER    = (40, 110, 190)
C_LWATER   = (70, 150, 220)
C_BASE     = (160, 130, 90)
C_DBASE    = (120, 95, 60)
C_COMMAND  = (240, 190, 40)
C_DCOMMAND = (190, 140, 20)
C_BULLET_P = (255, 255, 120)  # 玩家子弹
C_BULLET_E = (255, 120, 120)  # 敌方子弹

# Tank Battle (坦克大战)

## 项目概述
Python + Pygame 的经典 Battle City 风格坦克对战游戏。AI（Claude Code）生成。

## 技术栈
- Python 3.10+
- Pygame 2.x

## 项目结构
```
tank_battle/
├── main.py        # 入口 + 游戏主控（Game 类、状态机、PlayingState）
├── const.py       # 全局常量（尺寸、颜色、图块类型、方向）
├── core/
│   └── state.py   # State 基类 + StateMachine
├── entity/
│   ├── tank.py    # Tank → PlayerTank / EnemyTank
│   ├── bullet.py  # Bullet（Sprite）
│   ├── base.py    # Commander（主将）
│   └── powerup.py # PowerUp（占位）
├── map/
│   ├── tile.py    # GameMap + 预渲染图块 Surface
│   └── levels.py  # 关卡数据（程序化生成）
├── ui/
│   ├── hud.py     # 右侧 HUD 面板
│   └── screens.py # 标题/结束画面
└── docs/
    └── design.md  # 产品设计文档
```

## 运行方式
```bash
pip install pygame
python main.py
```

## 关键约定

### 网格系统
- 26×26 半格地图，CELL=24px
- 图块类型：EMPTY(0) WALL(1) STEEL(2) WATER(3) BASE(4) COMMANDER(5)
- `GameMap.is_tank_passable()` 判断坦克能否通过
- `GameMap.get(col, row)` 获取图块类型（越界返回 STEEL）

### 实体
- 所有实体继承 `pygame.sprite.Sprite`
- 坦克使用 `entity/tank.py` 中的 Tank → PlayerTank / EnemyTank
- 子弹使用 `entity/bullet.py` 中的 Bullet
- 碰撞检测使用 `pygame.sprite.groupcollide()`

### 状态管理
- 状态模式：Title → Playing → GameOver
- 每个 State 实现 `enter/handle_events/update/draw`
- PlayingState.end_reason 触发状态切换（"win"/"lose"/"commander_lost_*"）

### AI 类型
| 类型 | 血量 | 移动间隔 | 说明 |
|------|------|---------|------|
| basic | 1 | 每8帧 | 普通 |
| fast | 1 | 每6帧 | 高射速 |
| armor | 4 | 每12帧 | 重甲 |
| elite | 1 | 每8帧 | 精英（预留掉落） |

### 关卡设计
- 关卡数据在 `map/levels.py` 中程序化生成
- `_make_grid()` → 26×26 空网格
- `_place(g, col, row, tile, w, h)` 放置图块
- `_place_block(g, col, row, tile)` 放置 2×2 块
- 配置字典包含：ai_total, ai_max_active, player_lives, spawn 点

### 基地设计
- AI 基地在顶部：3×3 砖墙围住主将
- 玩家基地在底部：3 面墙 + 底部开口
- 主将用 COMMANDER 图块标记，在 `PlayingState.enter()` 中通过 `_find_commanders()` 定位

### 版本控制
- master 分支，每个功能独立提交
- commit message 中英文混合，描述改动内容

### 添加新功能的步骤
1. 先在 `const.py` 添加常量
2. 在对应模块实现功能逻辑
3. 在 `main.py` 的 PlayingState 中集成
4. 运行 `python main.py` 测试
5. `git add -A && git commit -m "描述" && git push`

## 依赖
- pygame
- 无其他外部依赖

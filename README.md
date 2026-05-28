# 坦克大战

> 基于 Python + Pygame 的经典 Battle City 风格复刻（v2.5 完整玩法版）

## 快速开始

```bash
pip install pygame
python main.py
```

## 操作

| 按键 | 功能 |
|------|------|
| WASD / 方向键 | 移动坦克 |
| J / 空格 | 射击 |
| Enter | 确认 / 开始 |
| 左右方向键 | 选关（关卡选择界面） |
| ESC | 暂停（游戏中） |
| R | 重新开始（结算界面） |
| Q | 返回标题 |

## 已实现功能

- 26×26 地图：砖墙（半格摧毁）、钢铁、水域、冰面、森林
- 玩家星级武器：双发 / 快弹 / 破钢
- 六种道具：星星、头盔、时钟、炸弹、铁铲、加命
- 四种 AI：普通 / 快速 / 重甲 / 精英（含行为状态机）
- JSON 关卡配置（`assets/levels/*.json`）
- 关卡选择、过关画面、暂停、通关结算
- 简易音效

## 项目结构

```
tank_battle/
├── main.py              # 入口
├── const.py             # 常量
├── game/                # 状态机与战斗逻辑
├── entity/              # 坦克、子弹、道具、主将
├── map/                 # 地图与关卡加载
├── ui/                  # HUD 与菜单
├── core/                # 状态机框架、音效
└── assets/levels/       # 关卡 JSON
```

## 关卡配置

编辑 `assets/levels/levelN.json`：

- `map_rows`：26 行，每行 26 字符（`.` 空地 `#` 砖 `S` 钢 `W` 水 `I` 冰 `F` 林 `C` 主将）
- `ai_total` / `ai_max_active` / `player_lives` / `spawn_interval` 等

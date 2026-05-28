"""坦克大战 v2.0 — 主入口 + 游戏循环"""

import sys
import random
import pygame

from const import (
    CELL, COLS, ROWS, PLAY_W, PLAY_H, HUD_W, SCREEN_W, SCREEN_H, FPS,
    EMPTY, WALL, STEEL, WATER, BASE, COMMANDER,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_VEC,
    C_BLACK,
)
from core.state import State, StateMachine
from map.tile import GameMap, pos_to_grid
from map.levels import get_level
from entity.tank import PlayerTank, EnemyTank
from entity.bullet import Bullet
from entity.base import Commander
from ui.hud import HUD
from ui.screens import TitleScreen, GameOverScreen


# ──────────────────────────────────────────
#  PlayingState — 游戏进行中
# ──────────────────────────────────────────
class PlayingState(State):
    def enter(self):
        g = self.game
        level_cfg = g.level_cfg

        self.game_map = GameMap(g.level_data)

        # 玩家
        spawn = level_cfg["player_spawn"]
        self.player = PlayerTank(spawn[0], spawn[1])

        # 主将（从地图中找到两个 COMMANDER，一个在顶部属于 AI，一个在底部属于玩家）
        cmd_positions = self._find_commanders(g.level_data)
        # 按 row 排序：row 小的为 AI 主将，row 大的为玩家主将
        cmd_positions.sort(key=lambda p: p[1])
        self.ai_cmd = None
        self.player_cmd = None
        if len(cmd_positions) >= 2:
            self.ai_cmd = Commander(cmd_positions[0][0], cmd_positions[0][1], "ai")
            self.player_cmd = Commander(cmd_positions[1][0], cmd_positions[1][1], "player")
        elif len(cmd_positions) == 1:
            self.player_cmd = Commander(cmd_positions[0][0], cmd_positions[0][1], "player")

        # 子弹 & 坦克组
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.all_tanks = pygame.sprite.Group()
        self.all_tanks.add(self.player)

        # AI 管理
        self.ai_pool = level_cfg["ai_total"]
        self.ai_killed = 0
        self.ai_max_active = level_cfg["ai_max_active"]
        self.ai_spawn_points = level_cfg["ai_spawns"]
        self.spawn_timer = 60  # 初始延迟

        # AI 坦克类型队列
        self.ai_types = []
        for _ in range(self.ai_pool):
            r = random.random()
            if r < 0.4:
                self.ai_types.append("basic")
            elif r < 0.65:
                self.ai_types.append("fast")
            elif r < 0.85:
                self.ai_types.append("armor")
            else:
                self.ai_types.append("elite")
        random.shuffle(self.ai_types)

        self.end_reason = None  # "win", "lose", "commander_lost"

    def _find_commanders(self, data):
        positions = []
        for r in range(ROWS):
            for c in range(COLS):
                if data[r][c] == COMMANDER:
                    positions.append((c, r))
        return positions

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                # 射击
                if e.key in (pygame.K_j, pygame.K_SPACE):
                    if self.player.alive and self.player.shoot_cd == 0:
                        self.bullets.add(self.player.shoot())
                        self.player.shoot_cd = self.player.shoot_cd_max
                # 暂停
                if e.key == pygame.K_ESCAPE:
                    self.game.state_machine.change("title")

    def update(self, dt):
        if self.end_reason:
            return

        # ── 玩家移动（长按） ──
        if self.player.alive and self.player.respawn_timer == 0:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            dir_map = {
                pygame.K_w: (0, -1, DIR_UP), pygame.K_UP: (0, -1, DIR_UP),
                pygame.K_s: (0, 1, DIR_DOWN), pygame.K_DOWN: (0, 1, DIR_DOWN),
                pygame.K_a: (-1, 0, DIR_LEFT), pygame.K_LEFT: (-1, 0, DIR_LEFT),
                pygame.K_d: (1, 0, DIR_RIGHT), pygame.K_RIGHT: (1, 0, DIR_RIGHT),
            }
            for k, (dc, dr, d) in dir_map.items():
                if keys[k]:
                    dx, dy = dc, dr
                    self.player.set_direction(d)
                    break
            if dx != 0 or dy != 0:
                if self.player.can_move(dx, dy, self.game_map, self.all_tanks):
                    self.player.col += dx
                    self.player.row += dy

        # ── AI 生成 ──
        self._update_spawning()

        # ── AI 行为 ──
        for e in self.enemies:
            if e.alive:
                e.update(self.game_map, self.all_tanks, self.bullets)

        # ── 子弹更新 + 碰撞 ──
        self._update_bullets()

        # ── 玩家重生 ──
        self.player.update()

        # ── 胜利条件 ──
        if self.ai_killed >= self.game.level_cfg["ai_total"] and len(self.enemies) == 0:
            self.end_reason = "win"

    def _update_spawning(self):
        if self.spawn_timer > 0:
            self.spawn_timer -= 1
            return
        if len(self.enemies) >= self.ai_max_active or self.ai_pool <= 0:
            return
        if not self.ai_types:
            return

        # 找个空的出生点
        random.shuffle(self.ai_spawn_points)
        for col, row in self.ai_spawn_points:
            if not self.game_map.is_tank_passable(col, row):
                continue
            test_rect = pygame.Rect(col * CELL + 2, row * CELL + 2, CELL - 4, CELL - 4)
            blocked = any(
                t.alive and t.rect.colliderect(test_rect)
                for t in self.all_tanks
            )
            if not blocked:
                etype = self.ai_types.pop(0)
                enemy = EnemyTank(col, row, etype)
                self.enemies.add(enemy)
                self.all_tanks.add(enemy)
                self.ai_pool -= 1
                self.spawn_timer = 90
                return
        self.spawn_timer = 15

    def _update_bullets(self):
        for b in list(self.bullets):
            if not b.alive:
                self.bullets.remove(b)
                continue

            # 保存移动前的位置，用于判断是否经过 COMMANDER
            old_col, old_row = b.x // CELL, b.y // CELL
            old_tile = self.game_map.get(old_col, old_row)

            b.update(self.game_map)

            if not b.alive:
                self.bullets.remove(b)
                continue

            col, row = b.x // CELL, b.y // CELL

            # 命中主将？（检查当前位置 + 上一帧位置）
            hit_cmd = False
            bullet_center = (b.x, b.y)
            for cmd in [self.ai_cmd, self.player_cmd]:
                if cmd and cmd.alive and cmd.grid_rect.collidepoint(bullet_center):
                    cmd.alive = False
                    hit_cmd = True
                    if cmd.team == "player":
                        self.end_reason = "commander_lost_player"
                    else:
                        self.end_reason = "commander_lost_ai"
                    break

            if hit_cmd:
                self.bullets.remove(b)
                continue

            # 命中坦克？
            hits = pygame.sprite.spritecollide(b, self.all_tanks, False)
            for tank in hits:
                if tank is b or tank.team == b.team:
                    continue
                self.bullets.remove(b)
                if isinstance(tank, PlayerTank):
                    lives = tank.die()
                    if lives <= 0:
                        self.end_reason = "lose"
                else:
                    if tank.hit():
                        self.ai_killed += 1
                break

    def draw(self, surface):
        surface.fill((10, 10, 10))

        # 绘制游戏区域背景
        pygame.draw.rect(surface, C_BLACK, (0, 0, PLAY_W, PLAY_H))

        # 地图
        self.game_map.draw(surface)

        # 子弹
        self.bullets.draw(surface)

        # 坦克
        for t in self.all_tanks:
            if isinstance(t, PlayerTank):
                t.draw(surface)
            else:
                if t.alive:
                    surface.blit(t.image, t.rect)

        # 主将
        for cmd in [self.ai_cmd, self.player_cmd]:
            if cmd and cmd.alive:
                surface.blit(cmd.image, cmd.rect)

        # HUD
        self.game.hud.draw(
            surface, self.player,
            self.game.level_cfg["ai_total"],
            self.ai_killed,
            len(self.enemies),
            self.game.current_level,
        )

    def exit(self):
        pass


# ──────────────────────────────────────────
#  GameOverState
# ──────────────────────────────────────────
class GameOverState(State):
    def enter(self):
        won = self.game.end_reason in ("win", "commander_lost_ai")
        self.won = won
        self.screen = GameOverScreen()

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    self.game.start_game(self.game.current_level)
                elif e.key == pygame.K_q:
                    self.game.state_machine.change("title")

    def draw(self, surface):
        self.screen.draw(surface, self.won)


# ──────────────────────────────────────────
#  TitleState
# ──────────────────────────────────────────
class TitleState(State):
    def enter(self):
        self.screen = TitleScreen()
        self.flash_timer = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                self.game.start_game(1)

    def update(self, dt):
        self.flash_timer = (self.flash_timer + 1) % 60

    def draw(self, surface):
        self.screen.draw(surface, self.flash_timer < 30)


# ──────────────────────────────────────────
#  Game — 主控
# ──────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("坦克大战 v2.0")
        self.clock = pygame.time.Clock()
        self.running = True

        self.hud = HUD()
        self.state_machine = StateMachine()
        self.state_machine.add("title", TitleState(self))
        self.state_machine.change("title")

        self.current_level = 1
        self.level_data = None
        self.level_cfg = None
        self.end_reason = None

    def start_game(self, level):
        self.current_level = level
        self.level_data, self.level_cfg = get_level(level)
        self.state_machine.add("playing", PlayingState(self))
        self.state_machine.change("playing")

    def run(self):
        while self.running:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False

            state = self.state_machine.current
            if state is None:
                break

            state.handle_events(events)
            state.update(self.clock.tick(FPS))

            # 检查 PlayingState 是否结束
            if isinstance(state, PlayingState) and state.end_reason:
                self.end_reason = state.end_reason
                won = state.end_reason in ("win", "commander_lost_ai")
                if won:
                    # 胜利 → 下一关
                    if self.current_level < 2:
                        self.start_game(self.current_level + 1)
                    else:
                        # 已通关
                        self.state_machine.add("gameover", GameOverState(self))
                        self.state_machine.change("gameover")
                else:
                    self.state_machine.add("gameover", GameOverState(self))
                    self.state_machine.change("gameover")
                continue

            state.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()

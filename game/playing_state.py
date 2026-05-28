"""游戏进行中状态"""

import random
import pygame
from const import (
    CELL, COLS, ROWS, PLAY_W, PLAY_H, EMPTY, COMMANDER,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    C_BLACK, MAX_PLAYER_BULLETS, FOREST,
)
from core.state import State
from core.keys import is_restart, is_quit_to_title
from map.tile import GameMap
from map.levels import get_level
from entity.tank import PlayerTank, EnemyTank
from entity.base import Commander
from entity.explosion import Explosion
from game.combat import CombatSystem
from core.audio import AudioManager


class PlayingState(State):
    def __init__(self, game):
        super().__init__(game)
        self.combat = None
        self.audio = None

    def reset(self, level):
        g = self.game
        g.level_data, g.level_cfg = get_level(level)
        level_cfg = g.level_cfg

        self.game_map = GameMap(g.level_data)
        self.audio = AudioManager()
        self.combat = CombatSystem(self)

        spawn = level_cfg["player_spawn"]
        self.player = PlayerTank(spawn[0], spawn[1], lives=level_cfg.get("player_lives", 3))

        cmd_positions = self._find_commanders(g.level_data)
        cmd_positions.sort(key=lambda p: p[1])
        self.ai_cmd = None
        self.player_cmd = None
        if len(cmd_positions) >= 2:
            self.ai_cmd = Commander(cmd_positions[0][0], cmd_positions[0][1], "enemy")
            self.player_cmd = Commander(cmd_positions[1][0], cmd_positions[1][1], "player")
        elif len(cmd_positions) == 1:
            self.player_cmd = Commander(cmd_positions[0][0], cmd_positions[0][1], "player")

        for cmd in (self.ai_cmd, self.player_cmd):
            if cmd:
                self.game_map.set(cmd.col, cmd.row, EMPTY)

        self.player_base_walls = []
        if self.player_cmd:
            self.player_base_walls = self.game_map.find_base_walls(
                self.player_cmd.col, self.player_cmd.row
            )

        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.all_tanks = pygame.sprite.Group()
        self.all_tanks.add(self.player)

        self.ai_remaining = level_cfg["ai_total"]
        self.ai_killed = 0
        self.ai_max_active = level_cfg["ai_max_active"]
        self.ai_spawn_points = level_cfg["ai_spawns"]
        self.ai_types = list(level_cfg.get("ai_types_queue", []))
        self.spawn_timer_ms = 1000
        self.spawn_interval_ms = level_cfg.get("spawn_interval", 90) * (1000 // 60)

        self.end_reason = None
        self._pending_end_reason = None
        self.explosions = []
        self.freeze_ms = 0
        self.shovel_ms = 0
        self.score = getattr(g, "score", 0)

    def enter(self):
        self.reset(self.game.current_level)

    def _find_commanders(self, data):
        positions = []
        for r in range(ROWS):
            for c in range(COLS):
                if data[r][c] == COMMANDER:
                    positions.append((c, r))
        return positions

    def _handle_end_event(self, event):
        """失败/胜利结算过程中也可重开或回标题"""
        if is_restart(event):
            self.end_reason = None
            self._pending_end_reason = None
            self.game.end_reason = None
            self.game.start_game(self.game.current_level)
            return True
        if is_quit_to_title(event):
            self.end_reason = None
            self._pending_end_reason = None
            self.game.end_reason = None
            self.game.state_machine.change("title")
            return True
        return False

    def handle_events(self, events):
        for e in events:
            if self._pending_end_reason or self.end_reason:
                if self._handle_end_event(e):
                    continue
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_j, pygame.K_SPACE):
                    self._player_shoot()
                if e.key == pygame.K_ESCAPE:
                    self.game.state_machine.change("pause")

    def _player_shoot(self):
        if not self.player.alive or not self.player.in_group:
            return
        if self.player.shoot_cd > 0:
            return
        n = sum(1 for b in self.bullets if b.team == "player")
        if n >= MAX_PLAYER_BULLETS:
            return
        for b in self.player.create_bullets():
            if sum(1 for x in self.bullets if x.team == "player") < MAX_PLAYER_BULLETS:
                self.bullets.add(b)
        self.player.shoot_cd = self.player.shoot_cd_max
        self.audio.play("shoot")

    def _player_bullet_count(self):
        return sum(1 for b in self.bullets if b.team == "player")

    def update(self, dt_ms):
        dt_ms = min(dt_ms, 50)
        for exp in list(self.explosions):
            exp.update()
            if exp.done:
                self.explosions.remove(exp)

        if self.end_reason:
            return

        if self._pending_end_reason is not None:
            if self.explosions:
                self.combat.update_bullets(dt_ms)
            else:
                self.end_reason = self._pending_end_reason
            return

        if self.freeze_ms > 0:
            self.freeze_ms = max(0, self.freeze_ms - dt_ms)
        if self.shovel_ms > 0:
            was = self.shovel_ms
            self.shovel_ms = max(0, self.shovel_ms - dt_ms)
            if was > 0 and self.shovel_ms == 0:
                self.game_map.restore_base_walls()

        self._update_player(dt_ms)
        self._update_spawning(dt_ms)

        frozen = self.freeze_ms > 0
        for e in self.enemies:
            if e.alive:
                e.update(
                    self.game_map, self.all_tanks, self.bullets,
                    self.player, self.player_cmd,
                    frozen=frozen, dt_ms=dt_ms,
                )

        self.combat.update_bullets(dt_ms)
        self.combat.update_powerups(dt_ms)
        self.player.update(self.game_map, self.all_tanks, dt_ms)

        if self.ai_killed >= self.game.level_cfg["ai_total"] and len(self.enemies) == 0:
            self._pending_end_reason = "win"
            self.score += 100 * self.game.current_level

    def _update_player(self, dt_ms):
        p = self.player
        if not p.alive or not p.in_group or p.respawn_timer_ms > 0:
            return
        if p.move_cd_ms > 0:
            return

        keys = pygame.key.get_pressed()
        dir_map = {
            pygame.K_w: (0, -1, DIR_UP), pygame.K_UP: (0, -1, DIR_UP),
            pygame.K_s: (0, 1, DIR_DOWN), pygame.K_DOWN: (0, 1, DIR_DOWN),
            pygame.K_a: (-1, 0, DIR_LEFT), pygame.K_LEFT: (-1, 0, DIR_LEFT),
            pygame.K_d: (1, 0, DIR_RIGHT), pygame.K_RIGHT: (1, 0, DIR_RIGHT),
        }
        for k, (dc, dr, d) in dir_map.items():
            if keys[k]:
                p.set_direction(d)
                moved = p.try_move(dc, dr, self.game_map, self.all_tanks)
                if moved:
                    p.slide_on_ice(self.game_map, self.all_tanks)
                    p.move_cd_ms = p.move_cd_max_ms
                break

    def _update_spawning(self, dt_ms):
        if self.spawn_timer_ms > 0:
            self.spawn_timer_ms -= dt_ms
            return
        if len(self.enemies) >= self.ai_max_active or self.ai_remaining <= 0:
            return
        if not self.ai_types:
            return

        random.shuffle(self.ai_spawn_points)
        for col, row in self.ai_spawn_points:
            if not self.game_map.is_tank_passable(col, row):
                continue
            test_rect = pygame.Rect(col * CELL + 2, row * CELL + 2, CELL - 4, CELL - 4)
            blocked = any(
                t.alive and t.in_group and t.rect.colliderect(test_rect)
                for t in self.all_tanks
            )
            if not blocked:
                etype = self.ai_types.pop(0)
                enemy = EnemyTank(col, row, etype)
                self.enemies.add(enemy)
                self.all_tanks.add(enemy)
                self.ai_remaining -= 1
                self.spawn_timer_ms = self.spawn_interval_ms
                return
        self.spawn_timer_ms = 250

    def _in_forest(self, col, row):
        return self.game_map.get(col, row) == FOREST

    def draw(self, surface):
        surface.fill((10, 10, 10))
        pygame.draw.rect(surface, C_BLACK, (0, 0, PLAY_W, PLAY_H))

        self.game_map.draw_terrain(surface, skip_commander=True)

        self.bullets.draw(surface)

        for t in self.all_tanks:
            hide = self._in_forest(t.col, t.row)
            if isinstance(t, PlayerTank):
                t.draw(surface, in_forest=hide)
            elif t.alive:
                t.draw(surface, in_forest=hide)

        for cmd in (self.ai_cmd, self.player_cmd):
            if cmd and cmd.alive:
                surface.blit(cmd.image, cmd.rect)

        self.powerups.draw(surface)

        for exp in self.explosions:
            exp.draw(surface)

        self.game_map.draw_forest_overlay(surface)

        self.game.hud.draw(
            surface, self.player,
            self.game.level_cfg["ai_total"],
            self.ai_killed,
            len(self.enemies),
            self.game.current_level,
            self.score,
            self.freeze_ms,
        )

    def exit(self):
        self.game.score = self.score

"""坦克实体"""

import random
import pygame
from const import (
    CELL, COLS, ROWS,
    EMPTY, WALL, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_VEC,
    C_GREEN, C_DGREEN, C_RED, C_DRED, C_GRAY, C_DARK, C_STEEL, C_DSTEEL,
    C_BLUE, C_DBLUE, DROP_RATES,
    FRAME_MS, INVINCIBLE_SPAWN_MS,
)
from entity.bullet import Bullet

_TANK_W = CELL - 4
_TANK_H = CELL - 4

AI_ROAM = "roam"
AI_ATTACK = "attack"
AI_PUSH = "push"
AI_STUCK = "stuck"


def _dir_to_target(fc, fr, tc, tr):
    dc, dr = tc - fc, tr - fr
    if abs(dc) >= abs(dr):
        return DIR_RIGHT if dc > 0 else DIR_LEFT
    return DIR_DOWN if dr > 0 else DIR_UP


class Tank(pygame.sprite.Sprite):
    def __init__(self, col, row, team="player", direction=DIR_UP):
        super().__init__()
        self.col = col
        self.row = row
        self.team = team
        self.direction = direction
        self.alive = True
        self.shoot_cd = 0
        self.shoot_cd_max = 15
        self.speed = 1
        self.in_group = True

        self.image = pygame.Surface((_TANK_W, _TANK_H), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self._update_image()
        self._update_pos()

    @property
    def px(self):
        return self.col * CELL + 2

    @property
    def py(self):
        return self.row * CELL + 2

    def _update_pos(self):
        self.rect.topleft = (self.px, self.py)

    def set_direction(self, d):
        if d != self.direction:
            self.direction = d
            self._update_image()

    def can_move(self, dcol, drow, game_map, tank_group):
        nc, nr = self.col + dcol, self.row + drow
        if nc < 0 or nc >= COLS or nr < 0 or nr >= ROWS:
            return False
        if not game_map.is_tank_passable(nc, nr):
            return False
        test_rect = pygame.Rect(nc * CELL + 2, nr * CELL + 2, _TANK_W, _TANK_H)
        for t in tank_group:
            if t is not self and t.alive and t.in_group and t.rect.colliderect(test_rect):
                return False
        return True

    def try_move(self, dcol, drow, game_map, tank_group):
        if self.can_move(dcol, drow, game_map, tank_group):
            self.col += dcol
            self.row += drow
            self._update_pos()
            return True
        return False

    def slide_on_ice(self, game_map, tank_group):
        dcol, drow = DIR_VEC[self.direction]
        while self.alive and game_map.is_on_ice(self.col, self.row):
            if not self.try_move(dcol, drow, game_map, tank_group):
                break

    def shoot(self):
        cx = self.col * CELL + CELL // 2
        cy = self.row * CELL + CELL // 2
        vec = DIR_VEC[self.direction]
        bx = cx + vec[0] * (CELL // 2 + 2)
        by = cy + vec[1] * (CELL // 2 + 2)
        return Bullet(bx, by, self.direction, team=self.team)

    def tick_cooldowns(self, dt_ms):
        if self.shoot_cd > 0:
            self.shoot_cd = max(0, self.shoot_cd - dt_ms)

    def update(self, *args, **kwargs):
        self._update_pos()


class PlayerTank(Tank):
    def __init__(self, col, row, lives=3):
        self.lives = lives
        self.stars = 0
        self.invincible_ms = 0
        self.respawn_timer_ms = 0
        self.spawn_col = col
        self.spawn_row = row
        self.move_cd_ms = 0
        self.move_cd_max_ms = 80
        self.shoot_cd_max = 250
        super().__init__(col, row, "player")

    def _update_image(self):
        self.image.fill((0, 0, 0, 0))
        w, h = _TANK_W, _TANK_H
        cx, cy = w // 2, h // 2
        body_color, dark_color = C_GREEN, C_DGREEN
        TRACK_W = 5
        BODY_X, BODY_W = TRACK_W, w - 2 * TRACK_W
        for tx in (0, w - TRACK_W):
            pygame.draw.rect(self.image, (55, 55, 55), (tx, 0, TRACK_W, h), border_radius=1)
        pygame.draw.rect(self.image, body_color, (BODY_X, 2, BODY_W, h - 4), border_radius=2)
        pygame.draw.rect(self.image, dark_color, (BODY_X, 2, BODY_W, h - 4), 1, border_radius=2)
        pygame.draw.circle(self.image, dark_color, (cx, cy), 5)
        pygame.draw.circle(self.image, body_color, (cx, cy), 3)
        BW = 3
        if self.direction == DIR_UP:
            pygame.draw.rect(self.image, dark_color, (cx - BW // 2, 0, BW, cy - 4))
        elif self.direction == DIR_DOWN:
            pygame.draw.rect(self.image, dark_color, (cx - BW // 2, cy + 4, BW, h - cy - 4))
        elif self.direction == DIR_LEFT:
            pygame.draw.rect(self.image, dark_color, (0, cy - BW // 2, cx - 4, BW))
        else:
            pygame.draw.rect(self.image, dark_color, (cx + 4, cy - BW // 2, w - cx - 4, BW))
        if self.stars > 0:
            pygame.draw.circle(self.image, (255, 220, 80), (w - 4, 4), 2)

    def bullet_speed(self):
        return 6 if self.stars >= 2 else 4

    def create_bullets(self):
        bullets = []
        speed = self.bullet_speed()
        power = self.stars

        def _spawn(offset_dc=0, offset_dr=0):
            cx = self.col * CELL + CELL // 2 + offset_dc * 4
            cy = self.row * CELL + CELL // 2 + offset_dr * 4
            vec = DIR_VEC[self.direction]
            bx = cx + vec[0] * (CELL // 2 + 2)
            by = cy + vec[1] * (CELL // 2 + 2)
            bullets.append(Bullet(bx, by, self.direction, speed=speed, team="player", power=power))

        if self.stars >= 1:
            d = self.direction
            if d in (DIR_UP, DIR_DOWN):
                _spawn(-1, 0)
                _spawn(1, 0)
            else:
                _spawn(0, -1)
                _spawn(0, 1)
        else:
            _spawn()
        return bullets

    def tick_cooldowns(self, dt_ms):
        super().tick_cooldowns(dt_ms)
        if self.move_cd_ms > 0:
            self.move_cd_ms = max(0, self.move_cd_ms - dt_ms)
        if self.invincible_ms > 0:
            self.invincible_ms = max(0, self.invincible_ms - dt_ms)

    def update(self, game_map=None, tank_group=None, dt_ms=FRAME_MS):
        super().update()
        self.tick_cooldowns(dt_ms)
        if self.respawn_timer_ms > 0:
            self.respawn_timer_ms = max(0, self.respawn_timer_ms - dt_ms)
            if self.respawn_timer_ms == 0:
                if game_map and tank_group and not self._can_respawn(game_map, tank_group):
                    self.respawn_timer_ms = 200
                    return
                self.col = self.spawn_col
                self.row = self.spawn_row
                self.alive = True
                self.in_group = True
                self.invincible_ms = INVINCIBLE_SPAWN_MS
                self._update_pos()

    def _can_respawn(self, game_map, tank_group):
        if not game_map.is_tank_passable(self.spawn_col, self.spawn_row):
            return False
        test_rect = pygame.Rect(self.spawn_col * CELL + 2, self.spawn_row * CELL + 2, _TANK_W, _TANK_H)
        for t in tank_group:
            if t is not self and t.alive and t.in_group and t.rect.colliderect(test_rect):
                return False
        return True

    def die(self):
        if not self.alive:
            return self.lives
        self.alive = False
        self.in_group = False
        self.lives -= 1
        if self.lives > 0:
            self.respawn_timer_ms = 1000
            self.stars = 0
        return self.lives

    def draw(self, surface, in_forest=False):
        if not self.alive:
            return
        if self.invincible_ms > 0 and (int(self.invincible_ms / 80) % 2) == 0:
            return
        if in_forest:
            surf = self.image.copy()
            surf.set_alpha(90)
            surface.blit(surf, self.rect)
        else:
            surface.blit(self.image, self.rect)


class EnemyTank(Tank):
    def __init__(self, col, row, etype="basic"):
        self.etype = etype
        self.flash_timer = 0  # 必须在 super().__init__ 之前（会调用 _update_image/_body_colors）
        hp_map = {"basic": 1, "fast": 1, "armor": 4, "elite": 1}
        speed_map = {"basic": 1, "fast": 2, "armor": 1, "elite": 1}
        cd_map = {"basic": 500, "fast": 330, "armor": 750, "elite": 420}
        move_ms = {"basic": 160, "fast": 110, "armor": 220, "elite": 160}

        super().__init__(col, row, "enemy", DIR_DOWN)
        self.hp = hp_map.get(etype, 1)
        self.max_hp = self.hp
        self.speed = speed_map.get(etype, 1)
        self.shoot_cd_max = cd_map.get(etype, 500)
        self.shoot_cd = 200
        self.move_interval_ms = move_ms.get(etype, 160)
        self.move_timer_ms = 0
        self.ai_state = AI_ROAM
        self.stuck_frames = 0
        self.last_pos = (col, row)
        self.blocked_timer_ms = 0
        self._update_image()

    def _body_colors(self):
        if self.etype == "basic":
            return C_GRAY, C_DARK
        if self.etype == "fast":
            return C_BLUE, C_DBLUE
        if self.etype == "armor":
            return C_STEEL, C_DSTEEL
        if self.etype == "elite":
            if self.flash_timer < 15:
                return (255, 80, 80), (200, 40, 40)
            return (210, 60, 60), (160, 30, 30)
        return C_RED, C_DRED

    def _update_image(self):
        w, h = _TANK_W, _TANK_H
        cx, cy = w // 2, h // 2
        self.image.fill((0, 0, 0, 0))
        body_color, dark_color = self._body_colors()
        TRACK_W = 5
        BODY_X, BODY_W = TRACK_W, w - 2 * TRACK_W
        for tx in (0, w - TRACK_W):
            pygame.draw.rect(self.image, (55, 55, 55), (tx, 0, TRACK_W, h), border_radius=1)
        pygame.draw.rect(self.image, body_color, (BODY_X, 2, BODY_W, h - 4), border_radius=2)
        pygame.draw.rect(self.image, dark_color, (BODY_X, 2, BODY_W, h - 4), 1, border_radius=2)
        pygame.draw.circle(self.image, dark_color, (cx, cy), 5)
        pygame.draw.circle(self.image, body_color, (cx, cy), 3)
        BW = 3
        if self.direction == DIR_UP:
            pygame.draw.rect(self.image, dark_color, (cx - BW // 2, 0, BW, cy - 4))
        elif self.direction == DIR_DOWN:
            pygame.draw.rect(self.image, dark_color, (cx - BW // 2, cy + 4, BW, h - cy - 4))
        elif self.direction == DIR_LEFT:
            pygame.draw.rect(self.image, dark_color, (0, cy - BW // 2, cx - 4, BW))
        else:
            pygame.draw.rect(self.image, dark_color, (cx + 4, cy - BW // 2, w - cx - 4, BW))
        if self.etype == "elite":
            pygame.draw.circle(self.image, (255, 200, 80), (cx, cy), 2)

    def _tile_ahead(self, game_map):
        dc, dr = DIR_VEC[self.direction]
        nc, nr = self.col + dc * self.speed, self.row + dr * self.speed
        return game_map.get(nc, nr)

    def _try_shoot_wall(self, game_map, bullet_group, max_enemy_bullets, enemy_bullet_count):
        if self._tile_ahead(game_map) == WALL and random.random() < 0.6:
            if self.shoot_cd <= 0 and enemy_bullet_count < max_enemy_bullets:
                self.shoot_cd = self.shoot_cd_max
                bullet_group.add(self.shoot())
                return True
        return False

    def update(self, game_map, tank_group, bullet_group, player, target_cmd, frozen=False, dt_ms=FRAME_MS):
        super().update()
        if not self.alive:
            return None
        if frozen:
            return None

        self.flash_timer = (self.flash_timer + 1) % 30
        if self.etype == "elite":
            self._update_image()

        self.tick_cooldowns(dt_ms)
        old_pos = (self.col, self.row)

        # AI 状态判定
        self.ai_state = AI_ROAM
        if player and player.alive and player.in_group:
            if game_map.has_line_of_sight(self.col, self.row, player.col, player.row):
                self.ai_state = AI_ATTACK
        if self.ai_state != AI_ATTACK and target_cmd and target_cmd.alive:
            if game_map.has_line_of_sight(self.col, self.row, target_cmd.col, target_cmd.row):
                self.ai_state = AI_PUSH

        if self.ai_state == AI_ATTACK:
            self.set_direction(_dir_to_target(self.col, self.row, player.col, player.row))
        elif self.ai_state == AI_PUSH and target_cmd:
            self.set_direction(_dir_to_target(self.col, self.row, target_cmd.col, target_cmd.row))
        elif self.stuck_frames > 30:
            self.ai_state = AI_STUCK
            self._pick_dir(game_map, tank_group, player, target_cmd)
            self.stuck_frames = 0
        else:
            self._pick_dir_weighted(game_map, tank_group, player, target_cmd)

        self.move_timer_ms += dt_ms
        moved = False
        if self.move_timer_ms >= self.move_interval_ms:
            self.move_timer_ms = 0
            dc, dr = DIR_VEC[self.direction]
            if self.try_move(dc * self.speed, dr * self.speed, game_map, tank_group):
                moved = True
                self.slide_on_ice(game_map, tank_group)
            else:
                self.blocked_timer_ms += self.move_interval_ms
                if self.blocked_timer_ms >= 500:
                    self._pick_dir(game_map, tank_group, player, target_cmd)
                    self.blocked_timer_ms = 0
                self._try_shoot_wall(game_map, bullet_group, 999)

        if (self.col, self.row) == old_pos and not moved:
            self.stuck_frames += 1
        else:
            self.stuck_frames = 0

        if self.shoot_cd <= 0 and len([b for b in bullet_group if b.team == "enemy"]) < 12:
            self.shoot_cd = self.shoot_cd_max
            bullet_group.add(self.shoot())

        if not moved:
            self._try_shoot_wall(game_map, bullet_group, 12)

    def _pick_dir(self, game_map, tank_group, player, target_cmd):
        dirs = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]
        random.shuffle(dirs)
        for d in dirs:
            dc, dr = DIR_VEC[d]
            if self.can_move(dc * self.speed, dr * self.speed, game_map, tank_group):
                self.set_direction(d)
                return
        self.set_direction(random.choice(dirs))

    def _pick_dir_weighted(self, game_map, tank_group, player, target_cmd):
        prefs = []
        if player and player.alive:
            prefs.append(_dir_to_target(self.col, self.row, player.col, player.row))
        if target_cmd and target_cmd.alive:
            prefs.append(_dir_to_target(self.col, self.row, target_cmd.col, target_cmd.row))
        prefs.extend([DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT])
        random.shuffle(prefs)
        seen = set()
        for d in prefs:
            if d in seen:
                continue
            seen.add(d)
            dc, dr = DIR_VEC[d]
            if self.can_move(dc * self.speed, dr * self.speed, game_map, tank_group):
                self.set_direction(d)
                return
        self._pick_dir(game_map, tank_group, player, target_cmd)

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface, in_forest=False):
        if not self.alive:
            return
        if in_forest:
            surf = self.image.copy()
            surf.set_alpha(90)
            surface.blit(surf, self.rect)
        else:
            surface.blit(self.image, self.rect)

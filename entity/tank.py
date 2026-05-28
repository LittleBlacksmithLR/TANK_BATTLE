"""坦克实体"""

import pygame
from const import (
    CELL, COLS, ROWS, PLAY_W, PLAY_H,
    EMPTY, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_VEC,
    C_GREEN, C_DGREEN, C_RED, C_DRED,
    C_GRAY, C_DARK, C_STEEL, C_DSTEEL,
)
from entity.bullet import Bullet


_TANK_W = CELL - 4  # 20
_TANK_H = CELL - 4


class Tank(pygame.sprite.Sprite):
    """坦克基类"""

    def __init__(self, col, row, team="player", direction=DIR_UP):
        super().__init__()
        self.col = col       # 网格坐标（半格）
        self.row = row
        self.team = team
        self.direction = direction
        self.alive = True
        self.shoot_cd = 0
        self.shoot_cd_max = 15
        self.speed = 1       # 每次移动步数（半格）

        self.image = pygame.Surface((_TANK_W, _TANK_H))
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

    def _update_image(self):
        """按方向重绘坦克（20×20 精绘版）"""
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        w, h = _TANK_W, _TANK_H
        cx, cy = w // 2, h // 2

        body_color = C_GREEN if self.team == "player" else C_RED
        dark_color = C_DGREEN if self.team == "player" else C_DRED

        TRACK_W = 5
        BODY_X = TRACK_W
        BODY_W = w - 2 * TRACK_W
        BODY_Y = 2
        BODY_H = h - 4

        # ── 履带（左右两侧 + 齿纹横线） ──
        for tx in (0, w - TRACK_W):
            pygame.draw.rect(self.image, (55, 55, 55), (tx, 0, TRACK_W, h), border_radius=1)
            for i in range(0, h, 4):
                pygame.draw.line(self.image, (35, 35, 35), (tx + 1, i), (tx + TRACK_W - 2, i))

        # ── 车身 ──
        pygame.draw.rect(self.image, body_color, (BODY_X, BODY_Y, BODY_W, BODY_H), border_radius=2)
        pygame.draw.rect(self.image, dark_color, (BODY_X, BODY_Y, BODY_W, BODY_H), 1, border_radius=2)

        # ── 炮塔（双层圆） ──
        pygame.draw.circle(self.image, dark_color, (cx, cy), 5)
        pygame.draw.circle(self.image, body_color, (cx, cy), 3)

        # ── 炮管 ──
        BW = 3
        if self.direction == DIR_UP:
            pygame.draw.rect(self.image, dark_color, (cx - BW // 2, 0, BW, cy - 4))
        elif self.direction == DIR_DOWN:
            pygame.draw.rect(self.image, dark_color, (cx - BW // 2, cy + 4, BW, h - cy - 4))
        elif self.direction == DIR_LEFT:
            pygame.draw.rect(self.image, dark_color, (0, cy - BW // 2, cx - 4, BW))
        else:  # RIGHT
            pygame.draw.rect(self.image, dark_color, (cx + 4, cy - BW // 2, w - cx - 4, BW))

    def set_direction(self, d):
        if d != self.direction:
            self.direction = d
            self._update_image()

    def can_move(self, dcol, drow, game_map, tank_group):
        nc = self.col + dcol
        nr = self.row + drow
        if nc < 0 or nc >= COLS or nr < 0 or nr >= ROWS:
            return False
        if not game_map.is_tank_passable(nc, nr):
            return False
        # 和其他坦克碰撞
        test_rect = pygame.Rect(nc * CELL + 2, nr * CELL + 2, _TANK_W, _TANK_H)
        for t in tank_group:
            if t is not self and t.alive and t.rect.colliderect(test_rect):
                return False
        return True

    def shoot(self):
        cx = self.col * CELL + CELL // 2
        cy = self.row * CELL + CELL // 2
        vec = DIR_VEC[self.direction]
        bx = cx + vec[0] * (CELL // 2 + 2)
        by = cy + vec[1] * (CELL // 2 + 2)
        return Bullet(bx, by, self.direction, team=self.team)

    def update(self, *args, **kwargs):
        if self.shoot_cd > 0:
            self.shoot_cd -= 1
        self._update_pos()


class PlayerTank(Tank):
    def __init__(self, col, row):
        super().__init__(col, row, "player")
        self.lives = 3
        self.invincible = 0
        self.respawn_timer = 0
        self.spawn_col = col
        self.spawn_row = row
        self.move_cd = 0
        self.move_cd_max = 4

    def update(self, game_map=None, tank_group=None, *args, **kwargs):
        super().update()
        if self.move_cd > 0:
            self.move_cd -= 1
        if self.invincible > 0:
            self.invincible -= 1
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer == 0:
                # 检查出生点是否被占
                if game_map and tank_group and not self._can_respawn(game_map, tank_group):
                    self.respawn_timer = 10  # 稍后再试
                    return
                self.col = self.spawn_col
                self.row = self.spawn_row
                self.alive = True
                self.invincible = 90

    def _can_respawn(self, game_map, tank_group):
        if not game_map.is_tank_passable(self.spawn_col, self.spawn_row):
            return False
        test_rect = pygame.Rect(self.spawn_col * CELL + 2, self.spawn_row * CELL + 2, _TANK_W, _TANK_H)
        for t in tank_group:
            if t is not self and t.alive and t.rect.colliderect(test_rect):
                return False
        return True

    def die(self):
        self.alive = False
        self.lives -= 1
        if self.lives > 0:
            self.respawn_timer = 60
        return self.lives

    def draw(self, surface):
        if not self.alive:
            return
        if self.invincible > 0 and (self.invincible // 4) % 2 == 0:
            return
        surface.blit(self.image, self.rect)


class EnemyTank(Tank):
    def __init__(self, col, row, etype="basic"):
        self.etype = etype
        hp_map = {"basic": 1, "fast": 1, "armor": 4, "elite": 1}
        speed_map = {"basic": 1, "fast": 1, "armor": 1, "elite": 1}
        cd_map = {"basic": 30, "fast": 20, "armor": 45, "elite": 25}

        super().__init__(col, row, "enemy", DIR_DOWN)
        self.hp = hp_map.get(etype, 1)
        self.max_hp = self.hp
        self.speed = speed_map.get(etype, 1)
        self.shoot_cd_max = cd_map.get(etype, 30)
        self.shoot_cd = 15
        self.dir_timer = 30
        # 移动节拍（0=每帧，1=每2帧...）
        move_cd_map = {"basic": 10, "fast": 7, "armor": 14, "elite": 10}
        self.move_interval = move_cd_map.get(etype, 1)
        self.move_counter = 0

    def _update_image(self):
        w, h = _TANK_W, _TANK_H
        cx, cy = w // 2, h // 2
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        if self.etype == "armor":
            body_color = C_STEEL
            dark_color = C_DSTEEL
        elif self.etype == "elite":
            body_color = (210, 60, 60)
            dark_color = (160, 30, 30)
        else:
            body_color = C_RED
            dark_color = C_DRED

        TRACK_W = 5
        BODY_X = TRACK_W
        BODY_W = w - 2 * TRACK_W
        BODY_Y = 2
        BODY_H = h - 4

        # ── 履带 ──
        for tx in (0, w - TRACK_W):
            pygame.draw.rect(self.image, (55, 55, 55), (tx, 0, TRACK_W, h), border_radius=1)
            for i in range(0, h, 4):
                pygame.draw.line(self.image, (35, 35, 35), (tx + 1, i), (tx + TRACK_W - 2, i))

        # ── 车身 ──
        pygame.draw.rect(self.image, body_color, (BODY_X, BODY_Y, BODY_W, BODY_H), border_radius=2)
        pygame.draw.rect(self.image, dark_color, (BODY_X, BODY_Y, BODY_W, BODY_H), 1, border_radius=2)

        # ── 炮塔 ──
        pygame.draw.circle(self.image, dark_color, (cx, cy), 5)
        pygame.draw.circle(self.image, body_color, (cx, cy), 3)

        # ── 炮管 ──
        BW = 3
        if self.direction == DIR_UP:
            pygame.draw.rect(self.image, dark_color, (cx - BW // 2, 0, BW, cy - 4))
        elif self.direction == DIR_DOWN:
            pygame.draw.rect(self.image, dark_color, (cx - BW // 2, cy + 4, BW, h - cy - 4))
        elif self.direction == DIR_LEFT:
            pygame.draw.rect(self.image, dark_color, (0, cy - BW // 2, cx - 4, BW))
        else:
            pygame.draw.rect(self.image, dark_color, (cx + 4, cy - BW // 2, w - cx - 4, BW))

        # ── 精英标记（金色星点） ──
        if self.etype == "elite":
            pygame.draw.circle(self.image, (255, 200, 80), (cx, cy), 2)

    def update(self, game_map, tank_group, bullet_group):
        super().update()
        if not self.alive:
            return

        self.dir_timer -= 1

        # 节拍控制（降低移动频率）
        if self.move_counter < self.move_interval:
            self.move_counter += 1
        else:
            self.move_counter = 0
            dcol, drow = DIR_VEC[self.direction]
            if self.can_move(dcol * self.speed, drow * self.speed, game_map, tank_group):
                self.col += dcol * self.speed
                self.row += drow * self.speed
            else:
                self._pick_dir(game_map, tank_group)

        # 定时变向
        if self.dir_timer <= 0:
            self._pick_dir(game_map, tank_group)
            self.dir_timer = 30

        # 射击
        if self.shoot_cd == 0:
            self.shoot_cd = self.shoot_cd_max
            bullet_group.add(self.shoot())

    def _pick_dir(self, game_map, tank_group):
        dirs = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]
        import random
        random.shuffle(dirs)
        for d in dirs:
            dc, dr = DIR_VEC[d]
            if self.can_move(dc * self.speed, dr * self.speed, game_map, tank_group):
                self.set_direction(d)
                return
        # 全堵死就随机
        self.set_direction(random.choice(dirs))

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
            return True  # 被消灭
        return False

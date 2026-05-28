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
        """按方向重绘坦克"""
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        w, h = _TANK_W, _TANK_H
        cx, cy = w // 2, h // 2

        color = C_GREEN if self.team == "player" else C_RED
        dcolor = C_DGREEN if self.team == "player" else C_DRED

        # 车身
        pygame.draw.rect(self.image, color, (0, 0, w, h), border_radius=2)
        pygame.draw.rect(self.image, dcolor, (0, 0, w, h), 2, border_radius=2)

        # 炮塔
        r = 7
        pygame.draw.circle(self.image, dcolor, (cx, cy), r)

        # 炮管
        if self.direction == DIR_UP:
            pygame.draw.rect(self.image, dcolor, (cx - 2, 0, 4, cy - r + 2))
        elif self.direction == DIR_DOWN:
            pygame.draw.rect(self.image, dcolor, (cx - 2, cy + r - 2, 4, h - cy - r + 2))
        elif self.direction == DIR_LEFT:
            pygame.draw.rect(self.image, dcolor, (0, cy - 2, cx - r + 2, 4))
        else:  # RIGHT
            pygame.draw.rect(self.image, dcolor, (cx + r - 2, cy - 2, w - cx - r + 2, 4))

        # 履带
        for dx, dy in [(2, 2), (w - 6, 2)]:
            pygame.draw.rect(self.image, dcolor, (dx, dy, 4, h - 4), border_radius=1)

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

    def update(self, *args, **kwargs):
        super().update()
        if self.invincible > 0:
            self.invincible -= 1
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer == 0:
                self.col = self.spawn_col
                self.row = self.spawn_row
                self.alive = True
                self.invincible = 90

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
        # 必须在 super().__init__() 之前设置，因为 _update_image() 会被调用
        self.etype = etype
        hp_map = {"basic": 1, "fast": 1, "armor": 4, "elite": 1}
        speed_map = {"basic": 1, "fast": 2, "armor": 1, "elite": 1}
        cd_map = {"basic": 30, "fast": 20, "armor": 45, "elite": 25}

        super().__init__(col, row, "enemy", DIR_DOWN)
        self.hp = hp_map.get(etype, 1)
        self.max_hp = self.hp
        self.speed = speed_map.get(etype, 1)
        self.shoot_cd_max = cd_map.get(etype, 30)
        self.shoot_cd = 15
        self.dir_timer = 30

    def _update_image(self):
        w, h = _TANK_W, _TANK_H
        cx, cy = w // 2, h // 2
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        color = C_STEEL if self.etype == "armor" else C_RED
        dcolor = C_DSTEEL if self.etype == "armor" else C_DRED
        color2 = C_GRAY if self.etype == "elite" else color

        pygame.draw.rect(self.image, color, (0, 0, w, h), border_radius=2)
        pygame.draw.rect(self.image, dcolor, (0, 0, w, h), 2, border_radius=2)
        pygame.draw.circle(self.image, dcolor, (cx, cy), 7)

        if self.direction == DIR_UP:
            pygame.draw.rect(self.image, dcolor, (cx - 2, 0, 4, cy - 5))
        elif self.direction == DIR_DOWN:
            pygame.draw.rect(self.image, dcolor, (cx - 2, cy + 5, 4, h - cy - 5))
        elif self.direction == DIR_LEFT:
            pygame.draw.rect(self.image, dcolor, (0, cy - 2, cx - 5, 4))
        else:
            pygame.draw.rect(self.image, dcolor, (cx + 5, cy - 2, w - cx - 5, 4))

        for dx, dy in [(2, 2), (w - 6, 2)]:
            pygame.draw.rect(self.image, dcolor, (dx, dy, 4, h - 4), border_radius=1)

        # 精英标记（红色闪烁）
        if self.etype == "elite":
            pygame.draw.circle(self.image, (255, 80, 80), (cx, cy), 3)

    def update(self, game_map, tank_group, bullet_group):
        super().update()
        if not self.alive:
            return

        self.dir_timer -= 1

        # 向前移动
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

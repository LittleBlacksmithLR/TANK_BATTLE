"""战斗与碰撞解析"""

import random
import pygame
from const import CELL, PU_LIFETIME_MS, HELMET_MS, FREEZE_MS, SHOVEL_MS, DROP_RATES, PU_TYPES
from entity.tank import PlayerTank
from entity.explosion import Explosion
from entity.powerup import PowerUp
class CombatSystem:
  def __init__(self, world):
    self.w = world

  def update_bullets(self, dt_ms):
    w = self.w
    for b in list(w.bullets):
      if not b.alive:
        w.bullets.remove(b)
        continue

      prev_x, prev_y = b.x, b.y
      alive, hit_base = b.update_move(w.game_map)
      if hit_base:
        col, row = int(b.x) // CELL, int(b.y) // CELL
        if w.player_cmd and abs(col - w.player_cmd.col) <= 5 and abs(row - w.player_cmd.row) <= 5:
          w._pending_end_reason = "commander_lost_player"
        else:
          w._pending_end_reason = "commander_lost_ai"
        w.explosions.append(Explosion(b.x, b.y, big=True))
        w.bullets.remove(b)
        w.audio.play("alarm")
        continue
      if not alive:
        w.bullets.remove(b)
        continue

      if self._check_commander(b, prev_x, prev_y):
        continue
      if self._check_tanks(b):
        continue

  def _check_commander(self, b, prev_x, prev_y):
    w = self.w
    points = [(b.x, b.y), (prev_x, prev_y), ((b.x + prev_x) / 2, (b.y + prev_y) / 2)]
    for cmd in (w.ai_cmd, w.player_cmd):
      if not cmd or not cmd.alive:
        continue
      if cmd.team == b.team:
        continue
      if any(cmd.grid_rect.collidepoint(p) for p in points):
        cmd.alive = False
        if cmd.team == "player":
          w._pending_end_reason = "commander_lost_player"
        else:
          w._pending_end_reason = "commander_lost_ai"
        w.explosions.append(
          Explosion(cmd.col * CELL + CELL // 2, cmd.row * CELL // 2, big=True)
        )
        w.bullets.remove(b)
        w.audio.play("explode")
        return True
    return False

  def _check_tanks(self, b):
    w = self.w
    hits = pygame.sprite.spritecollide(b, w.all_tanks, False)
    for tank in hits:
      if tank.team == b.team or not tank.alive or not tank.in_group:
        continue
      if isinstance(tank, PlayerTank):
        if tank.invincible_ms > 0 or tank.respawn_timer_ms > 0:
          w.bullets.remove(b)
          return True
        if w._pending_end_reason is not None:
          w.bullets.remove(b)
          return True
      w.bullets.remove(b)
      if isinstance(tank, PlayerTank):
        w.explosions.append(
          Explosion(tank.col * CELL + CELL // 2, tank.row * CELL + CELL // 2)
        )
        lives = tank.die()
        w.audio.play("explode")
        if lives <= 0:
          w._pending_end_reason = "lose"
          w.explosions.append(
            Explosion(tank.col * CELL + CELL // 2, tank.row * CELL + CELL // 2, big=True)
          )
      else:
        destroyed = tank.hit()
        w.audio.play("hit" if not destroyed else "explode")
        if destroyed:
          if random.random() < DROP_RATES.get(tank.etype, 0.1):
            w.powerups.add(PowerUp(tank.col, tank.row, random.choice(PU_TYPES)))
          w.ai_killed += 1
          w.explosions.append(
            Explosion(tank.col * CELL + CELL // 2, tank.row * CELL + CELL // 2)
          )
          w.enemies.remove(tank)
          w.all_tanks.remove(tank)
        else:
          w.explosions.append(
            Explosion(tank.col * CELL + CELL // 2, tank.row * CELL + CELL // 2, small=True)
          )
      return True
    return False

  def update_powerups(self, dt_ms):
    w = self.w
    if not w.player.alive or not w.player.in_group:
      return
    for pu in list(w.powerups):
      pu.lifetime_ms += dt_ms
      if pu.lifetime_ms >= PU_LIFETIME_MS:
        w.powerups.remove(pu)
        continue
      if pu.rect.colliderect(w.player.rect):
        self._apply_powerup(pu)
        w.powerups.remove(pu)
        w.audio.play("powerup")

  def _apply_powerup(self, pu):
    w = self.w
    p = w.player
    t = pu.ptype
    if t == "star":
      p.stars = min(3, p.stars + 1)
      p._update_image()
    elif t == "helmet":
      p.invincible_ms = max(p.invincible_ms, HELMET_MS)
    elif t == "clock":
      w.freeze_ms = max(w.freeze_ms, FREEZE_MS)
    elif t == "bomb":
      for e in list(w.enemies):
        w.ai_killed += 1
        w.explosions.append(
          Explosion(e.col * CELL + CELL // 2, e.row * CELL + CELL // 2)
        )
        w.enemies.remove(e)
        w.all_tanks.remove(e)
    elif t == "shovel":
      w.shovel_ms = max(w.shovel_ms, SHOVEL_MS)
      w.game_map.upgrade_walls_to_steel(w.player_base_walls)
    elif t == "tank":
      p.lives += 1

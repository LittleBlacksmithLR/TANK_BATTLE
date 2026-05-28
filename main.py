"""坦克大战 — 双阵营对战"""

import sys
import pygame

from const import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CELL_SIZE, COLS, ROWS,
    EMPTY, WALL, STEEL, WATER, BUNKER, COMMANDER,
    COLOR_BLACK, DIR_VEC,
)
from map import GameMap, pos_to_grid
from bullet import Bullet
from tank import PlayerTank, AITank


# ── 配置 ──
AI_TOTAL = 10           # AI 坦克总数
AI_MAX_ACTIVE = 3       # 同时活跃 AI 数
AI_SPAWN_POINTS = [     # AI 出生点（顶部）
    (1, 0), (9, 0), (18, 0), (27, 0), (36, 0),
]
MOVE_DELAY = 8          # 长按移动间隔（帧）


def draw_hud(surface, player, ai_killed, ai_tanks, game_state, font):
    """绘制 HUD"""
    if game_state == "playing":
        info = [
            f"[B 方] 坐标: ({player.col}, {player.row}) 方向: {player.direction}",
            f"[A 方] 已消灭: {ai_killed}/{AI_TOTAL} 存活: {len(ai_tanks)}",
            "WASD 移动 | J/空格 射击",
        ]
        for i, text in enumerate(info):
            surf = font.render(text, True, (200, 200, 200))
            surface.blit(surf, (10, 10 + i * 22))
        player.draw_hud_extra(surface, font)

    elif game_state == "player_win":
        surf = font.render("🎉 胜利！你摧毁了所有敌人！按 R 重新开始", True, (100, 255, 100))
        surface.blit(surf, (SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT // 2 - 10))
    elif game_state == "player_lose":
        surf = font.render("💀 失败！按 R 重新开始", True, (255, 80, 80))
        surface.blit(surf, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 10))
    elif game_state == "commander_lost_ai":
        surf = font.render("🎉 胜利！你摧毁了敌方主将！按 R 重新开始", True, (100, 255, 100))
        surface.blit(surf, (SCREEN_WIDTH // 2 - 290, SCREEN_HEIGHT // 2 - 10))
    elif game_state == "commander_lost_player":
        surf = font.render("💀 失败！我方主将被摧毁！按 R 重新开始", True, (255, 80, 80))
        surface.blit(surf, (SCREEN_WIDTH // 2 - 270, SCREEN_HEIGHT // 2 - 10))


def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("坦克大战 — 阵营对战")
    clock = pygame.time.Clock()
    try:
        font = pygame.font.SysFont("simhei", 18)
    except Exception:
        font = pygame.font.Font(None, 18)

    # ══════════════════════════════════════════
    # 游戏状态
    # ══════════════════════════════════════════
    def reset_game():
        gm = GameMap()
        player = PlayerTank(19, 28)
        ai_list = []
        bullets = []
        ai_pool = AI_TOTAL
        ai_killed = 0
        ai_spawn_timer = 30  # 初始延迟
        state = "playing"
        return gm, player, ai_list, bullets, ai_pool, ai_killed, ai_spawn_timer, state

    (game_map, player, ai_tanks, bullets,
     ai_pool, ai_killed, ai_spawn_timer, game_state) = reset_game()

    # 按键映射
    KEY_MAP = {
        pygame.K_w: (0, -1, "up"), pygame.K_UP: (0, -1, "up"),
        pygame.K_s: (0, 1, "down"), pygame.K_DOWN: (0, 1, "down"),
        pygame.K_a: (-1, 0, "left"), pygame.K_LEFT: (-1, 0, "left"),
        pygame.K_d: (1, 0, "right"), pygame.K_RIGHT: (1, 0, "right"),
    }
    held_dirs = {}

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in KEY_MAP:
                    dcol, drow, dir_name = KEY_MAP[event.key]
                    held_dirs[event.key] = (dcol, drow, dir_name)
                    if game_state == "playing" and player.alive and player.respawn_timer == 0:
                        if player.can_move_to(dcol, drow, game_map,
                                              [player] + ai_tanks):
                            player.direction = dir_name
                            player.col += dcol
                            player.row += drow
                            player.move_timer = MOVE_DELAY
                elif event.key == pygame.K_r and game_state != "playing":
                    (game_map, player, ai_tanks, bullets,
                     ai_pool, ai_killed, ai_spawn_timer, game_state) = reset_game()
                elif event.key in (pygame.K_j, pygame.K_SPACE):
                    if (game_state == "playing" and player.alive
                            and player.shoot_cd == 0 and player.respawn_timer == 0):
                        bullets.append(player.shoot())
                        player.shoot_cd = player.shoot_cd_max

            elif event.type == pygame.KEYUP:
                held_dirs.pop(event.key, None)

        # ══════════════════════════════════════
        # 更新逻辑
        # ══════════════════════════════════════
        if game_state == "playing":
            all_tanks = [player] + ai_tanks

            # ── 玩家移动（长按自动重复） ──
            if player.alive and player.respawn_timer == 0:
                player.update()
                if held_dirs:
                    last_key = list(held_dirs.keys())[-1]
                    dcol, drow, dir_name = held_dirs[last_key]
                    player.direction = dir_name
                    if player.move_timer > 0:
                        player.move_timer -= 1
                    else:
                        if player.can_move_to(dcol, drow, game_map, all_tanks):
                            player.col += dcol
                            player.row += drow
                        player.move_timer = MOVE_DELAY
            else:
                player.update()  # 处理重生倒计时

            # ── AI 生成 ──
            if ai_spawn_timer > 0:
                ai_spawn_timer -= 1
            else:
                if len(ai_tanks) < AI_MAX_ACTIVE and ai_pool > 0:
                    spawn = AITank.find_spawn_point(
                        game_map, all_tanks, AI_SPAWN_POINTS)
                    if spawn:
                        col, row = spawn
                        ai_tanks.append(AITank(col, row))
                        ai_pool -= 1
                    ai_spawn_timer = 40

            # ── AI 更新 ──
            for ai in ai_tanks[:]:
                if ai.alive:
                    ai.update(game_map, all_tanks, bullets)
                else:
                    ai_tanks.remove(ai)
                    ai_killed += 1

            # ── 子弹更新 ──
            for b in bullets[:]:
                b.update(game_map)
                if not b.alive:
                    bullets.remove(b)
                    continue

                col, row = pos_to_grid(int(b.x), int(b.y))
                tile = game_map.get(col, row)

                # 子弹击中主将
                if tile == COMMANDER:
                    game_map.set(col, row, EMPTY)
                    # 判断是哪个主将
                    if col in range(18, 21) and row in range(22, 27):
                        game_state = "commander_lost_player"
                    elif col in range(18, 21) and row in range(2, 7):
                        game_state = "commander_lost_ai"
                    bullets.remove(b)
                    continue

                # 子弹击中坦克
                hit_tank = None
                for t in all_tanks:
                    if not t.alive:
                        continue
                    # 友军子弹不伤友军
                    if b.team == t.team:
                        continue
                    if t.rect.colliderect(b.rect):
                        hit_tank = t
                        break

                if hit_tank:
                    bullets.remove(b)
                    if isinstance(hit_tank, PlayerTank):
                        remaining = hit_tank.die()
                        if remaining <= 0:
                            game_state = "player_lose"
                    else:
                        hit_tank.alive = False
                    continue

            # ── 胜利条件 ──
            if ai_killed >= AI_TOTAL and len(ai_tanks) == 0:
                game_state = "player_win"

        # ══════════════════════════════════════
        # 绘制
        # ══════════════════════════════════════
        screen.fill(COLOR_BLACK)
        draw_grid(screen)
        game_map.draw(screen)

        # 绘制 AI 坦克
        for ai in ai_tanks:
            ai.draw(screen)

        # 绘制玩家
        player.draw(screen)

        # 绘制子弹
        for b in bullets:
            b.draw(screen)

        # 绘制 HUD
        draw_hud(screen, player, ai_killed, ai_tanks, game_state, font)

        # 顶部 AI 计数器
        active_ai = len(ai_tanks)
        pool_left = ai_pool
        try:
            counter_font = pygame.font.SysFont("simhei", 16)
        except Exception:
            counter_font = pygame.font.Font(None, 16)
        counter_text = f"A 方: 活跃 {active_ai}/{AI_MAX_ACTIVE}  待命 {pool_left}/{AI_TOTAL}"
        surf2 = counter_font.render(counter_text, True, (200, 150, 150))
        screen.blit(surf2, (SCREEN_WIDTH // 2 - 120, 5))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

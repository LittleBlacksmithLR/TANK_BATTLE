"""菜单 / 选关 / 暂停 / 结算状态"""

import pygame
from const import SCREEN_W, SCREEN_H, C_BLACK
from core.state import State
from core.keys import is_restart, is_quit_to_title
from map.levels import level_count
from ui.screens import (
    TitleScreen, LevelSelectScreen, GameOverScreen,
    StageClearScreen, PauseOverlay,
)


class TitleState(State):
    def enter(self):
        self.screen = TitleScreen()
        self.flash_timer = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                self.game.state_machine.change("level_select")

    def update(self, dt_ms):
        self.flash_timer = (self.flash_timer + dt_ms) % 1000

    def draw(self, surface):
        self.screen.draw(surface, self.flash_timer < 500)


class LevelSelectState(State):
    def enter(self):
        self.screen = LevelSelectScreen(level_count())
        self.level = 1

    def handle_events(self, events):
        n = level_count()
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    self.level = max(1, self.level - 1)
                elif e.key == pygame.K_RIGHT:
                    self.level = min(n, self.level + 1)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.game.start_game(self.level)
                elif e.key == pygame.K_ESCAPE:
                    self.game.state_machine.change("title")

    def draw(self, surface):
        self.screen.draw(surface, self.level)


class PauseState(State):
    def enter(self):
        self.playing = self.game.state_machine._states.get("playing")

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.game.state_machine.change("playing")
                elif e.key == pygame.K_q:
                    self.game.state_machine.change("title")

    def update(self, dt_ms):
        pass

    def draw(self, surface):
        if self.playing:
            self.playing.draw(surface)
        PauseOverlay().draw(surface)


class StageClearState(State):
    def enter(self):
        self.timer_ms = 0
        self.level = self.game.current_level

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                self.game.advance_after_stage_clear()

    def update(self, dt_ms):
        self.timer_ms += dt_ms
        if self.timer_ms > 2500:
            self.game.advance_after_stage_clear()

    def draw(self, surface):
        StageClearScreen().draw(surface, self.level)


class GameOverState(State):
    def enter(self):
        won = self.game.end_reason in ("win", "commander_lost_ai")
        self.won = won
        self.all_cleared = won and self.game.current_level >= level_count()

    def handle_events(self, events):
        for e in events:
            if is_restart(e):
                self.game.end_reason = None
                self.game.start_game(self.game.current_level)
            elif is_quit_to_title(e):
                playing = self.game.state_machine._states.get("playing")
                if playing:
                    playing.end_reason = None
                    playing._pending_end_reason = None
                self.game.end_reason = None
                self.game.state_machine.change("title")

    def draw(self, surface):
        GameOverScreen().draw(surface, self.won, self.all_cleared)

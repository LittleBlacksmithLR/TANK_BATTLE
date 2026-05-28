"""游戏主控"""

import sys
import pygame

from const import SCREEN_W, SCREEN_H, FPS
from core.state import StateMachine
from map.levels import level_count
from game.playing_state import PlayingState
from game.states import TitleState, LevelSelectState, PauseState, StageClearState, GameOverState
from ui.hud import HUD


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("坦克大战 v2.5")
        self.clock = pygame.time.Clock()
        self.running = True

        self.hud = HUD()
        self.score = 0
        self.current_level = 1
        self.level_data = None
        self.level_cfg = None
        self.end_reason = None

        self.state_machine = StateMachine()
        playing = PlayingState(self)
        self.state_machine.add("title", TitleState(self))
        self.state_machine.add("level_select", LevelSelectState(self))
        self.state_machine.add("playing", playing)
        self.state_machine.add("pause", PauseState(self))
        self.state_machine.add("stage_clear", StageClearState(self))
        self.state_machine.add("gameover", GameOverState(self))
        self.state_machine.change("title")

    def start_game(self, level):
        self.current_level = level
        self.end_reason = None
        playing = self.state_machine._states["playing"]
        playing.end_reason = None
        playing._pending_end_reason = None
        playing.reset(level)
        self.state_machine.change("playing")

    def advance_after_stage_clear(self):
        if self.current_level < level_count():
            self.start_game(self.current_level + 1)
        else:
            self.end_reason = "win"
            self.state_machine.change("gameover")

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(FPS)
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False

            state = self.state_machine.current
            if state is None:
                break

            state.handle_events(events)
            state.update(dt_ms)

            state = self.state_machine.current
            if state is None:
                break

            if state.__class__.__name__ == "PlayingState" and getattr(state, "end_reason", None):
                self.end_reason = state.end_reason
                won = state.end_reason in ("win", "commander_lost_ai")
                if won:
                    if self.current_level < level_count():
                        self.state_machine.change("stage_clear")
                        nxt = self.state_machine.current
                        if nxt.__class__.__name__ == "StageClearState":
                            nxt.draw(self.screen)
                            pygame.display.flip()
                    else:
                        self.state_machine.change("gameover")
                        nxt = self.state_machine.current
                        if nxt.__class__.__name__ == "GameOverState":
                            nxt.draw(self.screen)
                            pygame.display.flip()
                else:
                    self.state_machine.change("gameover")
                    nxt = self.state_machine.current
                    if nxt.__class__.__name__ == "GameOverState":
                        nxt.draw(self.screen)
                        pygame.display.flip()
                continue

            state.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

"""状态机——游戏状态管理"""

import pygame


class State:
    """状态基类"""

    def __init__(self, game):
        self.game = game

    def enter(self):
        """进入状态时调用"""
        pass

    def exit(self):
        """离开状态时调用"""
        pass

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class StateMachine:
    """简单的状态机"""

    def __init__(self):
        self._states = {}
        self._current = None

    def add(self, name, state):
        self._states[name] = state

    def change(self, name):
        if self._current:
            self._current.exit()
        self._current = self._states.get(name)
        if self._current:
            self._current.enter()

    @property
    def current(self):
        return self._current

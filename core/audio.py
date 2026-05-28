"""简易音效（程序生成）"""

import math
import array
import pygame


class AudioManager:
    def __init__(self):
        self.enabled = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(22050, -16, 2, 512)
            self._sounds = {
                "shoot": self._beep(440, 40),
                "hit": self._beep(220, 50),
                "explode": self._beep(120, 120),
                "powerup": self._beep(660, 80),
                "alarm": self._beep(180, 200),
            }
        except pygame.error:
            self.enabled = False
            self._sounds = {}

    def _beep(self, freq, ms, vol=0.25):
        rate = 22050
        n = int(rate * ms / 1000)
        buf = array.array("h")
        for i in range(n):
            t = i / rate
            v = int(32767 * vol * math.sin(2 * math.pi * freq * t) * (1 - i / n))
            buf.append(v)
            buf.append(v)
        return pygame.mixer.Sound(buffer=buf)

    def play(self, name):
        if not self.enabled:
            return
        s = self._sounds.get(name)
        if s:
            s.play()

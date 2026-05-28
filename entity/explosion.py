"""爆炸特效"""

import pygame


class Explosion:
    """爆炸动画：膨胀 → 消退"""

    def __init__(self, cx, cy, big=False):
        self.x = cx
        self.y = cy
        self.frame = 0
        self.max_frame = 24 if big else 18
        self.done = False

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frame:
            self.done = True

    def draw(self, surface):
        if self.done:
            return
        p = self.frame / self.max_frame

        # 半径：先膨后缩
        if p < 0.3:
            r = int(3 + (p / 0.3) * 7)
        else:
            r = int(10 - ((p - 0.3) / 0.7) * 8)
        r = max(2, min(r, 11))

        # 从外到内绘制三层色环（暗红 → 橙 → 亮黄）
        layers = [
            ((180, 40, 20), r),
            ((255, 160, 40), max(1, r - 2)),
            ((255, 255, 120), max(1, r - 4)),
        ]
        for color, radius in layers:
            if radius > 0:
                pygame.draw.circle(surface, color, (self.x, self.y), radius)

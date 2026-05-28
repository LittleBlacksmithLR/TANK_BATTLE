"""资源加载（占位，后续替换为 SpriteSheet 贴图）"""

import os
import pygame

_ASSET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")


def load_image(path, size=None):
    full = os.path.join(_ASSET_DIR, "images", path)
    try:
        img = pygame.image.load(full).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except FileNotFoundError:
        return None

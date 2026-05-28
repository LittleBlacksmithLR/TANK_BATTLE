"""资源加载"""

import json
import os
import pygame

_ROOT = os.path.dirname(os.path.dirname(__file__))
_ASSETS = os.path.join(_ROOT, "assets")


def asset_path(*parts):
    return os.path.join(_ASSETS, *parts)


def load_image(path, size=None):
    full = asset_path("images", path)
    try:
        img = pygame.image.load(full).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except FileNotFoundError:
        return None


def load_level_json(n):
    path = asset_path("levels", f"level{n}.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

"""跨键盘布局的按键匹配"""

import pygame


def _name(event):
    try:
        return pygame.key.name(event.key).lower()
    except Exception:
        return ""


def is_restart(event):
    if event.type == pygame.TEXTINPUT:
        return event.text.lower() == "r"
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_r, ord("r"), ord("R")):
            return True
        return _name(event) == "r"
    return False


def is_quit_to_title(event):
    if event.type == pygame.TEXTINPUT:
        return event.text.lower() == "q"
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_q, ord("q"), ord("Q")):
            return True
        return _name(event) == "q"
    return False

from enum import Enum
import pyglet


def init():
    """Initialise defaults / user settings"""
    global caption, window_width, window_height, fullscreen
    caption = 'Pongy'
    window_width = 800
    window_height = 500
    fullscreen = False
    if fullscreen:
        # Get current screen resolution
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()
        window_width = screen.width
        window_height = screen.height


class Player(Enum):
    PLAYER_1 = 1
    PLAYER_2 = 2
    AI = 3


class Direction(Enum):
    LEFT = 1
    RIGHT = 2

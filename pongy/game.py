#!/usr/bin/env python

#import entity
#import ball
#import paddle
import table

import pyglet

class Game(object):
    def __init__(self, caption='Pongy', width=600, height=400, fullscreen=False):
        # Game title
        self.caption = caption

        # Game window dimensions
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

        # Is the game running?
        self.is_running = True

        # Is the game paused?
        self.is_paused = False

        if self.fullscreen:
            self.game_window = pyglet.window.Window(caption=self.caption, fullscreen=self.fullscreen)
        else:
            self.game_window = pyglet.window.Window(caption=self.caption, width=self.width, height=self.height)

        self.game_table = table.Table(self.width, self.height)

    def new_game(self):
        pass

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    def update(self, dt):
        self.game_window.clear()
        self.game_table.draw()
        


if __name__ == '__main__':
    game = Game()
    pyglet.clock.schedule_interval(game.update, 1/120)
    pyglet.app.run()


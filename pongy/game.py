#!/usr/bin/env python

import settings
import entity

import pyglet


class Game(object):
    # Grab settings

    def __init__(self):

        # Is the game running?
        self.is_running = True

        # Is the game paused?
        self.is_paused = False

        if S.fullscreen:
            self.game_window = pyglet.window.Window(caption=S.caption,
                                                    width=S.window_width,
                                                    height=S.window_height,
                                                    fullscreen=S.fullscreen)
        else:
            self.game_window = pyglet.window.Window(caption=S.caption,
                                                    width=S.window_width,
                                                    height=S.window_height)

        self.new_game()

    def new_game(self):
        self.game_table = entity.Table()
        self.paddle_1 = entity.Paddle(1)
        self.paddle_2 = entity.Paddle(2)
        self.ball = entity.Ball()
        self.score_1 = entity.Score(1)
        self.score_1.score = 10
        self.score_2 = entity.Score(2)

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    def draw(self):
        self.game_window.clear()
        self.game_table.draw()
        self.paddle_1.draw()
        self.paddle_2.draw()
        self.ball.draw()
        self.score_1.draw()
        self.score_2.draw()

    def update(self, dt):
        self.ball.update(dt)
        self.ball.check_collision(self.score_1, self.score_2)
        self.draw()


if __name__ == '__main__':
    S = settings.Config()
    game = Game()
    pyglet.clock.schedule_interval(game.update, 1/120)
    pyglet.app.run()

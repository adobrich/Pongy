#!/usr/bin/env python

import settings
import entity

import pyglet


class Game(object):
    def __init__(self):
        """Inits Game with default settings"""
        settings.init()
        if settings.fullscreen:
            self.game_window = pyglet.window.Window(caption=settings.caption,
                                                    width=settings.window_width,
                                                    height=settings.window_height,
                                                    fullscreen=settings.fullscreen)
        else:
            self.game_window = pyglet.window.Window(caption=settings.caption,
                                                    width=settings.window_width,
                                                    height=settings.window_height)
        # List of objects to draw
        self.render_queue = []
        # List of objects to update
        self.update_queue = []

        self.initialise()
        self.new_game()

    def initialise(self):
#        self.update_queue.append(entity.Ball(settings.Direction.RIGHT))
#        self.update_queue.append(entity.Score(settings.window_width * 0.25, settings.window_height))
#        self.update_queue.append(entity.Score(settings.window_width * 0.75, settings.window_height))
        self.game_table = entity.Table(settings.window_width, settings.window_height)
        self.ball = entity.Ball(settings.Direction.RIGHT)
        self.score_1 = entity.Score(settings.window_width * 0.25, settings.window_height)
        self.score_2 = entity.Score(settings.window_width * 0.75, settings.window_height)

    def new_game(self):
        self.paddle_1 = entity.Paddle(settings.Player.PLAYER_1, self.game_table)
        self.paddle_2 = entity.Paddle(settings.Player.PLAYER_2, self.game_table)

    def collision_check(self):
        if self.ball.x <= self.ball.half_width:
            self.score_2.update()
            self.ball.bounce_x()
        elif self.ball.x >= settings.window_width - self.ball.half_width:
            self.score_1.update()
            self.ball.bounce_x()
        elif self.ball.y <= self.ball.half_height or self.ball.y >= settings.window_height - self.ball.half_height:
            self.ball.bounce_y()

    def update(self, dt):
        self.ball.update(dt)
        self.collision_check()
        self.draw()

    def draw(self):
        self.game_window.clear()
        self.game_table.draw()
        self.ball.draw()
        self.score_1.draw()
        self.score_2.draw()
        self.paddle_1.draw()
        self.paddle_2.draw()


if __name__ == '__main__':
    game = Game()
    pyglet.clock.schedule_interval(game.update, 1/120)
    pyglet.app.run()

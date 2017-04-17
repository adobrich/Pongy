#!/usr/bin/env python
import pyglet

from enum import Enum

import entity


class Game(pyglet.window.Window):
    """Initialise and run the Pongy game."""
    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        self.table = entity.Table(self.width, self.height)
        self.ball = entity.Ball(self.width / 2, self.height / 2, 8, 8)
        self.score_one = entity.Score(self.width * 0.25, self.height)
        self.score_two = entity.Score(self.width * 0.75, self.height)
        self.game_over()

    def game_over(self):
        """End game, and bounce the ball around the screen while waiting for
        players to start a new game."""
        self.game_in_progress = False
        self.table.set_demo_mode()
        self.ball.reset(self.width / 2, self.height / 2)

    def new_game(self):
        """Reset score, player/ball positions and start a new game."""
        self.game_in_progress = True
        self.table.set_game_mode()
        self.score_one.reset()
        self.score_two.reset()
        self.ball.reset(self.width / 2, self.height / 2)
        self.paddle_one = entity.Paddle(self.table.gutter_width,
                                        self.height / 2, 8, 50)
        self.paddle_two = entity.Paddle(self.width - self.table.gutter_width,
                                        self.height / 2, 8, 50)


    def update(self, dt):
        """Update game objects and check for collisions."""
        self.ball.move(dt)

        # Check for ball / paddle collision
        if self.game_in_progress:
            # Check win condition
            if self.score_one.score == 11 or self.score_two.score == 11:
                self.game_over()

            # Check lose condition
            if self.has_collided(self.ball, self.table.right):
                self.score_one.increment()
                self.ball.reset(self.width / 2, self.height / 2)
            elif self.has_collided(self.ball, self.table.left):
                self.score_two.increment()
                self.ball.reset(self.width / 2, self.height / 2)

            # Update paddles
            self.paddle_one.update(dt)
            self.paddle_two.update(dt)
            if (self.has_collided(self.paddle_one, self.ball) or
               self.has_collided(self.paddle_two, self.ball)):
                self.ball.paddle_bounce()
            if self.has_collided(self.paddle_one, self.table.top):
                self.paddle_one.stop()
                self.paddle_one.max_y(self.height)
            elif self.has_collided(self.paddle_one, self.table.bottom):
                self.paddle_one.stop()
                self.paddle_one.min_y()

            if self.has_collided(self.paddle_two, self.table.top):
                self.paddle_two.stop()
                self.paddle_two.max_y(self.height)
            elif self.has_collided(self.paddle_two, self.table.bottom):
                self.paddle_two.stop()
                self.paddle_two.min_y()

        # Bounce of top and bottom of screen
        if (self.has_collided(self.ball, self.table.top) or
           self.has_collided(self.ball, self.table.bottom)):
            self.ball.wall_bounce('y')

        # Bounce ball of left and right walls if game is not in progress
        if not self.game_in_progress:
            if (self.has_collided(self.ball, self.table.left) or
               self.has_collided(self.ball, self.table.right)):
                self.ball.wall_bounce('x')

    def on_key_press(self, symbol, modifiers):
        """Keyboard event handler for key press."""
        if symbol == pyglet.window.key.ESCAPE:
            exit(0)
        elif symbol == pyglet.window.key.SPACE:
            if not self.game_in_progress:
                self.new_game()
        if self.game_in_progress:
            if symbol == pyglet.window.key.A:
                self.paddle_one.move_up()
            elif symbol == pyglet.window.key.Z:
                self.paddle_one.move_down()
            elif symbol == pyglet.window.key.UP:
                self.paddle_two.move_up()
            elif symbol == pyglet.window.key.DOWN:
                self.paddle_two.move_down()

    def on_key_release(self, symbol, modifiers):
        """Keyboard event handler for key release."""
        if self.game_in_progress:
            if symbol == pyglet.window.key.A:
                self.paddle_one.stop()
            elif symbol == pyglet.window.key.Z:
                self.paddle_one.stop()
            elif symbol == pyglet.window.key.UP:
                self.paddle_two.stop()
            elif symbol == pyglet.window.key.DOWN:
                self.paddle_two.stop()

    def on_draw(self):
        """Render game objects."""
        self.clear()
        self.table.draw()
        self.score_one.draw()
        self.score_two.draw()
        self.ball.draw()
        # Only draw paddles if game is in progress
        if self.game_in_progress:
            self.paddle_one.draw()
            self.paddle_two.draw()

    def has_collided(self, one, two):
        """Check for collision between two objects using AABB method."""
        self.x_collision = (one.x + one.half_width >= two.x - two.half_width and
                            two.x + two.half_width >= one.x - one.half_width)
        self.y_collision = (one.y + one.half_height >= two.y - two.half_height and
                            two.y + two.half_height >= one.y - one.half_height)
        return self.x_collision and self.y_collision


if __name__ == '__main__':
    game = Game(caption='Pongy', width=800, height=500, fullscreen=False)
    pyglet.clock.schedule_interval(game.update, 1.0 / 60.0)
    pyglet.app.run()

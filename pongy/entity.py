import random
import math

import pyglet


class Drawable(object):
    """Base class for all drawable objects."""
    def __init__(self, x=0, y=0, z=0, rx=0, ry=0, rz=0,
             color=[1.0, 1.0, 1.0, 1.0]):
        # Position
        self.x = x
        self.y = y
        self.z = z

        # Rotation
        self.rx = rx
        self.ry = ry
        self.rz = rz

        self.color = color

    def set_properties(self):
        """Apply position, rotation and color."""
        pyglet.gl.glLoadIdentity()

        pyglet.gl.glTranslatef(self.x, self.y, self.z)

        pyglet.gl.glRotatef(self.rx, 1, 0, 0)
        pyglet.gl.glRotatef(self.ry, 0, 1, 0)
        pyglet.gl.glRotatef(self.rz, 0, 0, 1)

        pyglet.gl.glColor4f(*self.color)


class Rectangle(Drawable):
    """Create a rectangle with provided size and location."""
    def __init__(self, x, y, width, height):
        super(Rectangle, self).__init__(x, y)
        self.half_width = width / 2
        self.half_height = height / 2

    def draw(self):
        """Render rectangle."""
        self.set_properties()
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', (
                             -self.half_width, self.half_height,
                             self.half_width, self.half_height,
                             self.half_width, -self.half_height,
                             -self.half_width, -self.half_height)))


class Table(Drawable):
    """Draw the pongy table; it's just a dashed line down the middle
    of the screen.
    """
    def __init__(self, width, height, gutter_width=100):
        super(Table, self).__init__()
        self.width = width
        self.height = height
        self.gutter_width = gutter_width

        # Dummy objects along table boundaries for collision detection
        self.top = CollisionZone(self.width / 2, self.height + 50, self.width, 100)
        self.bottom = CollisionZone(self.width / 2, -50, self.width, 100)
        self.left = CollisionZone(-50, self.height / 2, 100, self.height)
        self.right = CollisionZone(self.width + 50, self.height / 2, 100, self.height)

        # We want 30 dashed lines to represent the net
        self.dash_count = 30
        self.dash_length = self.height / (self.dash_count * 2)
        self.dash_start = self.dash_length / 2
        self.dash_end = self.dash_length + self.dash_length / 2
        self.dash_width = 2

        self.render_queue = pyglet.graphics.Batch()

        for i in range(self.dash_count):
            self.render_queue.add(2, pyglet.gl.GL_LINES, None, ('v2f', (
                                  self.width / 2, self.dash_start,
                                  self.width / 2, self.dash_end)))
            self.dash_start += 2 * self.dash_length
            self.dash_end += 2 * self.dash_length

    def set_game_mode(self):
        """Move left and right collision zone to allow ball to leave
        the screen."""
        self.left = CollisionZone(-150, self.height / 2, 100, self.height * 2)
        self.right = CollisionZone(self.width + 150, self.height / 2, 100, self.height * 2)

    def set_demo_mode(self):
        """Prevent ball from leaving the screen"""
        self.left = CollisionZone(-50, self.height / 2, 100, self.height)
        self.right = CollisionZone(self.width + 50, self.height / 2, 100, self.height)

    def draw(self):
        """Render table."""
        self.set_properties()
        # Set dash width
        pyglet.gl.glPushAttrib(pyglet.gl.GL_LINE_BIT)
        pyglet.gl.glLineWidth(self.dash_width)
        self.render_queue.draw()
        # Unset dash width
        pyglet.gl.glPopAttrib()


class Ball(Rectangle):
    """Create a ball (square) with provided size and location."""
    def __init__(self, x, y, width=8, height=8):
        super(Ball, self).__init__(x, y, width, height)
        self.x = x
        self.y = y
        self.half_width = width / 2
        self.half_height = height / 2
        self.vel_x = 0
        self.vel_y = 0

    def move(self, dt):
        """Move ball along current vector."""
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

    def wall_bounce(self, direction):
        """Bounce/reflect ball off walls."""
        if direction == 'y':
            self.vel_y *= -1
        else:
            # Only when game is over
            self.vel_x *= -1

    def paddle_bounce(self):
        """Bounce ball off paddle."""
        # TODO: Change this so it will rebound the ball back based on
        # when the ball struck the paddle. Above the center returns the
        # ball with a positive y, below the center returns with a -y.
        # P |/  y=+++
        # A |/  y=++
        # D |/  y=+
        # D |-  y=0
        # L |\  y=-
        # E |\  y=--
        # . |\  y=---
        self.vel_x *= -1


    def reset(self, x, y):
        """Reset ball to (x, y) co-ordinates and serve in random direction."""
        self.x = x
        self.y = y
        self.vel_x = random.randrange(150, 250) * random.choice([-1, 1])
        self.vel_y = random.randrange(50, 150) * random.choice([-1, 1])


class Paddle(Rectangle):
    """Paddle that represents the player."""
    def __init__(self, x, y, width=8, height=50):
        super(Paddle, self).__init__(x, y, width, height)
        self.x = x
        self.y = y
        self.velocity = 0
        self.half_width = width / 2
        self.half_height = height / 2
        self.speed = 450

    def update(self, dt):
        """Update location of paddle."""
        self.y += self.velocity * dt

    def move_up(self):
        """Move paddle up."""
        self.velocity = self.speed

    def move_down(self):
        """Move paddle down."""
        self.velocity = -self.speed
    
    def stop(self):
        """Stop paddle."""
        self.velocity = 0;


class Score(Drawable):
    """Displays the current score."""
    def __init__(self, x, y,
                 score=0, pixel_size=6, grid_width=9, grid_height=8):
        super(Score, self).__init__()
        self.score = score
        self.pixel_size = pixel_size
        self.grid_anchor = ((grid_width / 2) * pixel_size,
                            (grid_height / 2) * pixel_size)
        self.score_grid = []
        # (x, y) location of top left  square relative to the grid anchor
        self.x = x - self.grid_anchor[0]
        self.y = y - self.grid_anchor[1]
        for row in range(grid_height):
            self.score_grid.append([])
            for column in range(grid_width):
                self.score_grid[row].append((self.x, self.y))
                self.x += pixel_size
            self.y -= pixel_size
            self.x = x - self.grid_anchor[0]
        self.update_mask()

    def increment(self):
        """Increase score by one."""
        self.score += 1
        self.update_mask()

    def reset(self):
        """Reset score to zero."""
        self.score = 0
        self.update_mask()

    def update_mask(self):
        """Fetches the bit mask for the provided score value.
        Only values 0 to 11 (inclusive) are available.
        """
        mask = {
                0: [[0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0]],
                1: [[0, 0, 0, 0, 1, 0, 0, 0, 0],
                    [0, 0, 0, 0, 1, 0, 0, 0, 0],
                    [0, 0, 0, 0, 1, 0, 0, 0, 0],
                    [0, 0, 0, 0, 1, 0, 0, 0, 0],
                    [0, 0, 0, 0, 1, 0, 0, 0, 0],
                    [0, 0, 0, 0, 1, 0, 0, 0, 0],
                    [0, 0, 0, 0, 1, 0, 0, 0, 0],
                    [0, 0, 0, 0, 1, 0, 0, 0, 0]],
                2: [[0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0]],
                3: [[0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0]],
                4: [[0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0]],
                5: [[0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0]],
                6: [[0, 0, 0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0]],
                7: [[0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0]],
                8: [[0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0]],
                9: [[0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0]],
                10: [[0, 0, 1, 0, 0, 1, 1, 1, 1],
                     [0, 0, 1, 0, 0, 1, 0, 0, 1],
                     [0, 0, 1, 0, 0, 1, 0, 0, 1],
                     [0, 0, 1, 0, 0, 1, 0, 0, 1],
                     [0, 0, 1, 0, 0, 1, 0, 0, 1],
                     [0, 0, 1, 0, 0, 1, 0, 0, 1],
                     [0, 0, 1, 0, 0, 1, 0, 0, 1],
                     [0, 0, 1, 0, 0, 1, 1, 1, 1]],
                11: [[0, 0, 0, 1, 0, 0, 1, 0, 0],
                     [0, 0, 0, 1, 0, 0, 1, 0, 0],
                     [0, 0, 0, 1, 0, 0, 1, 0, 0],
                     [0, 0, 0, 1, 0, 0, 1, 0, 0],
                     [0, 0, 0, 1, 0, 0, 1, 0, 0],
                     [0, 0, 0, 1, 0, 0, 1, 0, 0],
                     [0, 0, 0, 1, 0, 0, 1, 0, 0],
                     [0, 0, 0, 1, 0, 0, 1, 0, 0]]
               }
        self.render_queue = pyglet.graphics.Batch()
        for pos_row, mask_row in zip(self.score_grid, mask[self.score]):
            for pos, mask in zip(pos_row, mask_row):
                if mask:
                    self.render_queue.add(4, pyglet.gl.GL_QUADS, None, ('v2f', (
                                          pos[0] - self.pixel_size / 2,
                                          pos[1] + self.pixel_size / 2,
                                          pos[0] + self.pixel_size / 2,
                                          pos[1] + self.pixel_size / 2,
                                          pos[0] + self.pixel_size / 2,
                                          pos[1] - self.pixel_size / 2,
                                          pos[0] - self.pixel_size / 2,
                                          pos[1] - self.pixel_size / 2)))

    def draw(self):
        """Batch render the scoreboard."""
        self.render_queue.draw()


class CollisionZone(Drawable):
    """Creates a zone of size width * height centered at (x, y)
    which other objects can collide with. Useful for creating invisible
    boundaries."""
    def __init__(self, x, y, width, height):
        super(CollisionZone, self).__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.half_width = width / 2
        self.half_height = height / 2

import settings

import random

import pyglet


class Drawable(object):
    """Base class for drawable objects."""
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

        self.render_queue = pyglet.graphics.Batch()

    def set_properties(self):
        """Reset matrix then set objects position,
        rotation and colour in preparation for drawing.
        """
        # Reset matrix
        pyglet.gl.glLoadIdentity()

        # Set position
        pyglet.gl.glTranslatef(self.x, self.y, self.z)

        # Set rotation
        pyglet.gl.glRotatef(self.rx, 1, 0, 0)
        pyglet.gl.glRotatef(self.ry, 0, 1, 0)
        pyglet.gl.glRotatef(self.rz, 0, 0, 1)

        pyglet.gl.glColor4f(*self.color)


class Rectangle(Drawable):
    """Create a rectangle with provided size and location."""
    def __init__(self, width, height, x, y):
        """Inits Rectangle with size and (x, y) coordinates."""
        super(Rectangle, self).__init__(x, y)
        self.half_width = width / 2
        self.half_height = height / 2

        self.render_queue.add(4, pyglet.gl.GL_QUADS, None, ('v2f', (
                              -self.half_width, self.half_height,
                              self.half_width, self.half_height,
                              self.half_width, -self.half_height,
                              -self.half_width, -self.half_height)))

    def draw(self):
        """Render rectangle."""
        self.set_properties()
        self.render_queue.draw()


class Table(Drawable):
    """Draw the pongy table; it's just a dashed line down the middle
    of the screen.
    """
    def __init__(self, width=800, height=500, gutter_width=100):
        """Inits Table with default values."""
        super(Table, self).__init__()
        self.width = width
        self.height = height
        self.gutter_width = gutter_width

        # We want 30 dashed lines to represent the net
        self.dash_count = 30
        self.dash_length = self.height / (self.dash_count * 2)
        self.dash_start = self.dash_length / 2
        self.dash_end = self.dash_length + self.dash_length / 2
        self.dash_width = 2

        for i in range(self.dash_count):
            self.render_queue.add(2, pyglet.gl.GL_LINES, None, ('v2f', (
                                  self.width / 2, self.dash_start,
                                  self.width / 2, self.dash_end)))
            self.dash_start += 2 * self.dash_length
            self.dash_end += 2 * self.dash_length

    def draw(self):
        """Render table."""
        self.set_properties()
        # Set dash width
        pyglet.gl.glPushAttrib(pyglet.gl.GL_LINE_BIT)
        pyglet.gl.glLineWidth(self.dash_width)
        self.render_queue.draw()
        # Unset dash width
        pyglet.gl.glPopAttrib()


class Paddle(Rectangle):
    """Paddle that represents the player."""
    def __init__(self, player, table, width=8, height=40):
        """Inits Paddle with default values."""
        if player == settings.Player.PLAYER_1:
            self.x = table.gutter_width
            self.y = table.height / 2
        if player == settings.Player.PLAYER_2 or player == settings.Player.AI:
            self.x = table.width - table.gutter_width
            self.y = table.height / 2
        super(Paddle, self).__init__(width, height, self.x, self.y)
        self.half_width = width / 2
        self.half_height = height / 2
        # Initial velocity
        self.velocity = 0

    def move_up(self):
        self.velocity = 10

    def move_down(self):
        self.velocity = -10

    def stop(self):
        self.velocity = 0


class Ball(Rectangle):
    """Create a ball (square) with provided size and location."""
    def __init__(self, direction, width=8, height=8):
        self.x = settings.window_width / 2
        self.y = settings.window_height / 2
        super(Ball, self).__init__(width, height, self.x, self.y)
        self.direction = direction
        if self.direction == settings.Direction.RIGHT:
            self.vel_x = random.randrange(3, 7)
            self.vel_y = random.randrange(-5, 7)
        else:
            self.vel_x = -random.randrange(3, 7)
            self.vel_y = random.randrange(-5, 7)

    def bounce_x(self):
        self.vel_x *= -1

    def bounce_y(self):
        self.vel_y *= -1

    def update(self, dt):
        self.x += self.vel_x
        self.y += self.vel_y


class Score(Drawable):
    """Displays the current score."""
    def __init__(self, x, y,
                 score=0, pixel_size=6, grid_width=9, grid_height=8):
        super(Score, self).__init__()
        """Inits Score with default values and (x, y) coordinates."""
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
        self.score_render_queue = self.get_mask()

    def update(self):
        self.score += 1
        self.score_render_queue = self.get_mask()

    def get_mask(self):
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
        render_queue = []
        for pos_row, mask_row in zip(self.score_grid, mask[self.score]):
            for pos, mask in zip(pos_row, mask_row):
                if mask:
                    render_queue.append(Rectangle(self.pixel_size,
                                                  self.pixel_size, pos[0], pos[1]))
        return render_queue

    def draw(self):
        """Render scoreboard."""
        for pixel in self.score_render_queue:
            pixel.draw()

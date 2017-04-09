from enum import Enum
import random

import pyglet


class Entity(object):
    """Base class for in-game objects.

    Attributes:
        tx (float): objects x coordinate.
        ty (float): objects y coordinate.
        tz (float): objects z coordinate.
        rx (float): objects x rotation.
        ry (float): objects y rotation.
        rz (float): objects z rotation.
        color (:obj:`list` of `float`): color [r, g, b, a].
    """
    def __init__(self, color=[1.0, 1.0, 1.0, 1.0]):
        # Position
        self.tx = 0
        self.ty = 0
        self.tz = 0

        # Rotation
        self.rx = 0
        self.ry = 0
        self.rz = 0

        self.color = color

    def set_properties(self):
        """Reset matrix then set objects position,
        rotation and colour in preparation for drawing.
        """
        # Reset matrix
        pyglet.gl.glLoadIdentity()

        # Set position
        pyglet.gl.glTranslatef(self.tx, self.ty, self.tz)

        # Set rotation
        pyglet.gl.glRotatef(self.rx, 1, 0, 0)
        pyglet.gl.glRotatef(self.ry, 0, 1, 0)
        pyglet.gl.glRotatef(self.rz, 0, 0, 1)

        pyglet.gl.glColor4f(*self.color)


class Table(Entity):
    """Draw the pongy table; it's just a dashed line down the middle
    of the screen.

    Attributes:
        width (int): table width.
        height (int): table height.
        gutter_width (int): area behind player where ball is out of bounds.
    """
    def __init__(self, width=600, height=400, gutter_width=50):
        """Inits Table with default values."""
        super(Table, self).__init__()
        self.width = width
        self.height = height
        self.gutter_width = gutter_width

    def draw(self):
        """Render table."""
        # TODO: Actually make this a dashed line instead of a solid line.
        self.set_properties()
        pyglet.gl.glPushAttrib(pyglet.gl.GL_LINE_BIT)
        pyglet.gl.glLineWidth(2)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (
                             self.width / 2, 0.0,
                             self.width / 2, self.height)))
        pyglet.gl.glPopAttrib()


class Paddle(Entity):
    """Paddle that represents the player.

    Attributes:
        player = (:obj:`Enum`): one of the three possible values.
        half_height (float): half paddle height.
        half_width (float): half paddle width.
        tx (float): objects x coordinate.
        ty (float): objects y coordinate.
    """
    def __init__(self, player, table, width=8, height=40):
        """Inits Paddle with default values."""
        super(Paddle, self).__init__()
        self.half_width = width / 2
        self.half_height = height / 2
        if player == Player.PLAYER_1:
            self.tx = table.gutter_width
            self.ty = table.height / 2
        if player == Player.PLAYER_2 or player == Player.AI:
            self.tx = table.width - table.gutter_width
            self.ty = table.height / 2

    def draw(self):
        """Render paddle."""
        self.set_properties()
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', (
                             -self.half_width, self.half_height,
                             self.half_width, self.half_height,
                             self.half_width, -self.half_height,
                             -self.half_width, -self.half_height)))


class Ball(Entity):
    """Create a ball (square) with provided size and location.

    Attributes:
        tx (float): squares x coordinate.
        ty (float): squares y coordinate.
        size (int): length of the squares side.
        direction (:obj:`Enum`) direction ball should be served.
        half_size (float): half the length of a squares side.
        vel_x (float): velocity of the ball in the x direction.
        vel_y (float): velocity of the ball in the y direction.
        ball (:obj:`Square`): square representing the ball.
    """
    def __init__(self, size, table):
        super(Ball, self).__init__()
        self.tx = table.width / 2
        self.ty = table.height / 2
        self.direction = Direction.RIGHT
        if self.direction == Direction.RIGHT:
            self.vel_x = random.randrange(120, 240) / 60.0
            self.vel_y = random.randrange(60, 180) / 60.0
        else:
            self.vel_x = -random.randrange(120, 240) / 60.0
            self.vel_y = -random.randrange(60, 180) / 60.0

        self.ball = Square(size, self.tx, self.ty)

    def update(self, dt):
        self.ball.tx += self.vel_x
        self.ball.ty += self.vel_y

    # TODO: complete this
    def check_collision(self):
        pass

    def draw(self):
        self.set_properties()
        self.ball.draw()


class Square(Entity):
    """Create a square with provided size and location.

    Attributes:
        tx (float): squares x coordinate.
        ty (float): squares y coordinate.
        half_size (float): half the length of a squares side.
    """
    def __init__(self, size, x, y):
        """Inits Square with size and (x, y) coordinates."""
        super(Square, self).__init__()
        self.tx = x
        self.ty = y
        self.half_size = size / 2

    def draw(self):
        """Render square."""
        self.set_properties()
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', (
                             -self.half_size, self.half_size,
                             self.half_size, self.half_size,
                             self.half_size, -self.half_size,
                             -self.half_size, -self.half_size)))


class Score(Square):
    """Displays the current score.

    Attributes:
        score (int): current score.
        size (int): pixel size for text.
        grid_anchor (:obj:`tuple`): coordinates for center of score grid.
        score_grid (:obj:`list` of :obj:`tuple`): coordinates of pixels.
    """
    def __init__(self, x, y,
                 score=0, size=6, grid_width=9, grid_height=8):
        """Inits Score with default values and (x, y) coordinates."""
        self.score = score
        self.size = size
        self.grid_anchor = ((grid_width / 2) * size, (grid_height / 2) * size)
        self.score_grid = []
        # (x, y) location of top left  square relative to the grid anchor
        self.x = x - self.grid_anchor[0]
        self.y = y - self.grid_anchor[1]
        for row in range(grid_height):
            self.score_grid.append([])
            for column in range(grid_width):
                self.score_grid[row].append((self.x, self.y))
                self.x += size
            self.y -= size
            self.x = x - self.grid_anchor[0]

    def get_mask(self, score):
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
        return mask[score]

    def draw(self):
        """Render scoreboard."""
        draw_list = []
        for pos_row, mask_row in zip(self.score_grid,
                                     self.get_mask(self.score)):
            for pos, mask in zip(pos_row, mask_row):
                if mask:
                    draw_list.append(Square(self.size, pos[0], pos[1]))
        for item in draw_list:
            item.draw()


# TODO: Remove this testing code when done
#def update(dt):
#    ball.update(dt)
#    draw(dt)
#
#
#def draw(dt):
#    window.clear()
#    table.draw()
#    score_1.draw()
#    score_2.draw()
#    paddle_1.draw()
#    paddle_2.draw()
#    ball.draw()
#
#
#class Player(Enum):
#    PLAYER_1 = 1
#    PLAYER_2 = 2
#    AI = 3
#
#
#class Direction(Enum):
#    LEFT = 1
#    RIGHT = 2
#
#
#window = pyglet.window.Window(caption='Pongy', width=600, height=400)
#table = Table()
#paddle_1 = Paddle(Player.PLAYER_1, table)
#paddle_2 = Paddle(Player.PLAYER_2, table)
#ball = Ball(8, table)
#score_1 = Score(600 * .25, 400)
#score_2 = Score(600 * .75, 400)
#pyglet.clock.schedule_interval(update, 1/120)
#pyglet.app.run()

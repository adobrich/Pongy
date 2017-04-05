import pyglet

class Entity(object):
    """
    Base class for in game objects
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
        """
        Set objects position, rotation and color in preparation for drawing
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

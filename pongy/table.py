from entity import Entity

import pyglet

class Table(Entity):
    """
    Representation of the Pongy table; it's just a white line done the middle
    """
    def __init__(self, width, height):
        super(Table, self).__init__()
        self.width = width
        self.height = height

        # Set origin to center of window
        self.tx = self.width / 2
        self.ty = self.height / 2

    def draw(self):
        # TODO: Change solid line to a dashed line like the original pong
        self.set_properties()
        pyglet.gl.glPushAttrib(pyglet.gl.GL_LINE_BIT)
        pyglet.gl.glLineWidth(2)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                ("v2f", (0.0, -self.height/2, 0.0, self.height)))
        pyglet.gl.glPopAttrib()


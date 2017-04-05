import pyglet
import table

class Pongy(pyglet.window.Window):
    def __init__(self, **kwargs):
        self.width = kwargs.get('width')


"""
class Pongy(pyglet.window.Window):
    def __init__(self, **kwargs):
        super(Pongy, self).__init__(**kwargs)
        if not kwargs.get('fullscreen'):
            self.width = kwargs.get('width', 700)
            self.height = kwargs.get('height', 400)

    def on_draw(self):
        self.clear()
        table.draw_table()

    def update(self, dt):
        pass

game = Pongy(caption='Pongy')
table = table.Table(width=game.width, height=game.height)
"""
game = Pongy(caption='Pongy2', width=50, height=200)
#pyglet.clock.schedule_interval(game.update, 1/120)
pyglet.app.run()

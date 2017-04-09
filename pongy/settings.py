import pyglet


class Config(object):
    # Window settings
    caption = 'Pongy'
    window_width = 600
    window_height = 400
    fullscreen = False

    # Table settings
    gutter_width = 40

    # Score settings
    score_height = 0
    score_width = 0
    score_thickness = 6
    player_1_score_pos_x = 0
    player_1_score_pos_y = 0
    player_2_score_pos_x = 0
    player_2_score_pos_y = 0

    # Player 1 settings
    player_1_pos_x = 0
    player_1_pos_x = 0

    # Player 2 settings
    player_2_pos_x = 0
    player_2_pos_y = 0

    # Paddle settings
    paddle_width = 8
    paddle_height = 70
    paddle_starting_velocity = 2

    # Ball settings
    ball_size = 10
    ball_pos_x = 0
    ball_pos_y = 0
    ball_starting_velocity = 3

    def __init__(self):
        if self.fullscreen:
            # Get current screen resolution
            platform = pyglet.window.get_platform()
            display = platform.get_default_display()
            screen = display.get_default_screen()
            self.window_width = screen.width
            self.window_height = screen.height

        # Score width based on thickness (4 cols)
        self.score_width = self.score_thickness * 4
        # Score height based on thickness (10 rows)
        self.score_height = self.score_thickness * 10

        # Player 1 location based on screen size
        self.player_1_pos_x = self.gutter_width
        self.player_1_pos_y = self.window_height / 2

        # Player 1 score location based on screen size
        self.player_1_score_pos_x = self.window_width / 4
        self.player_1_score_pos_y = self.window_height - 70

        # Player 2 location based on screen size
        self.player_2_pos_x = self.window_width - self.gutter_width
        self.player_2_pos_y = self.window_height / 2

        # Player 2 score location based on screen size
        self.player_2_score_pos_x = self.window_width - self.window_width / 4
        self.player_2_score_pos_y = self.window_height - 70

        # Starting ball position middle of screen
        self.ball_pos_x = self.window_width / 2
        self.ball_pos_y = self.window_height / 2

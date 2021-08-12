import logging

import pygame
import pygame.display

import Driver
import Game
# from Renderer import Renderer
# import LevelLoader

# Full windows size params
WIDTH = 800 # px
HEIGHT = 600 # px

MENU_WIDTH = 160 # px
HUD_HEIGHT = 80 # px

# Game Surface (Board + Peripheral)
GAME_WIDTH = WIDTH - MENU_WIDTH # 800 - 160 = 640
GAME_HEIGHT = HEIGHT - HUD_HEIGHT # 600 - 160 = 440

# Game Board size params (B = G x C)
# Ex: 20 * 16 = 320x320 board pixel size
# Ex: 20 * 20 = 400x400
COLUMNS = 15
ROWS = 15
CELL_SIZE = 30 # px, length & width

BOARD_HEIGHT = (ROWS * CELL_SIZE) + 1 # px, plus one for hangover border
BOARD_WIDTH = (COLUMNS * CELL_SIZE) + 1 # px

if __name__ == '__main__':
    debug = False # TODO: Build-based parameters (os.getenv)?
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    # logging.info("test default log level")
    pygame.init()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen_bounds = screen.get_rect()

    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert()
    game_window = game_surface.get_rect(topright=screen_bounds.topright)

    # Surface for drawing game board
    # game_board = pygame.Surface((BOARD_LENGTH, BOARD_WIDTH)).convert()
    game_board = game_surface.subsurface((GAME_WIDTH // 2) - (BOARD_WIDTH // 2),
        (GAME_HEIGHT // 2) - (BOARD_HEIGHT // 2), BOARD_WIDTH, BOARD_HEIGHT) # NO convert()
    game_board_bounds = game_board.get_rect(center=game_window.center)

    # HUD surface
    hud = pygame.Surface((GAME_WIDTH, HUD_HEIGHT)).convert()
    hud_bounds = hud.get_rect(bottomright=screen_bounds.bottomright)

    # Menu surface
    menu_height = HEIGHT - HUD_HEIGHT
    menu = pygame.Surface((MENU_WIDTH, menu_height)).convert()
    menu_bounds = menu.get_rect(bottomleft=screen_bounds.bottomleft)

    # TODO: Corinthian Window
    game=Game.Game(cell_size=CELL_SIZE,
        game_area=game_window,
        board=game_board_bounds,
        hud=hud_bounds,
        menu=menu_bounds)

    # Initial game load from Driver
    # level_loader = LevelLoader(debug=debug)
    Driver.game_load(1, game)
    Game.menu_load(game, ["end_turn"])

    # Establish dictionary of surfaces for rendering
    Driver.register_surfaces(display=screen,
        game=game_surface, board=game_board, hud=hud, menu=menu)
    
    Driver.game_loop(game=game, debug=debug)

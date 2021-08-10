import logging
from renderers import ShapeRenderer

import pygame
import pygame.draw
import pygame.display
import pygame.font

from Game import Game
from objects import Renderable

COLOR_WHITE = (255, 255, 255)
COLOR_DARK_GRAY = (25, 25, 25)
COLOR_GRAY = (100, 100, 100)
COLOR_LIGHT_GRAY = (130, 130, 130)
COLOR_DARK_GREEN = (0, 50, 0)
COLOR_LIGHT_GREEN = (0, 200, 0)
COLOR_DARK_YELLOW = (50, 50, 0)
COLOR_RED = (200, 0, 0)

DISPLAY_SURFACE = None # type: pygame.Surface
BACKGROUND_SURFACE = None # type: pygame.Surface

HUD_FONT = None # type: pygame.font.Font

def register_display_surface(surface: pygame.Surface):
    global DISPLAY_SURFACE, HUD_FONT
    DISPLAY_SURFACE = surface

    HUD_FONT = pygame.font.Font(None, 16) # Can't instantiate font before initialized

def setup_background_board(surface: pygame.Surface, game: Game):
    global BACKGROUND_SURFACE
    BACKGROUND_SURFACE = surface

    # # Game Board Draw
    # surface.fill(COLOR_DARK_GRAY)

    # Grid Line & Terrain Draw (Full tile draw)
    for tile in game.grid: # tile: Space
        pixel_x = tile.x * game.cell_size
        pixel_y = tile.y * game.cell_size
        # Draw grid lines
        pygame.draw.lines(surface,
            COLOR_RED,
            True,
            [
                (pixel_x, pixel_y),
                (pixel_x + game.cell_size, pixel_y),
                (pixel_x + game.cell_size, pixel_y + game.cell_size),
                (pixel_x, pixel_y + game.cell_size)
            ]
        )

        terrain = game.grid[tile].terrain
        terrain_color = COLOR_DARK_GRAY
        if terrain == "Endzone":
            # Draw something different for the endzone
            terrain_color = COLOR_DARK_GREEN

        pygame.draw.rect(surface,
            terrain_color,
            pygame.Rect(pixel_x + 1, pixel_y + 1,
                game.cell_size - 1, game.cell_size - 1),
            0 # Fill the square
        )

def draw_debug(debug_message: str):
    pygame.display.set_caption(debug_message)

def draw_game(surface: pygame.Surface, game: Game):
    # Game board Border draw
    border_width = 5

    border_top = (game.game_area.height // 2) - (game.board.height // 2) - border_width
    border_left = (game.game_area.width // 2) - (game.board.width // 2) - border_width
    border_bottom = (game.game_area.height // 2) + (game.board.height // 2) + border_width
    border_right = (game.game_area.width // 2) + (game.board.width // 2) + border_width

    pygame.draw.line(surface, COLOR_WHITE, (border_left, border_top), (border_left, border_bottom), border_width)
    pygame.draw.line(surface, COLOR_WHITE, (border_left, border_top), (border_right, border_top), border_width)
    pygame.draw.line(surface, COLOR_WHITE, (border_right, border_top), (border_right, border_bottom), border_width)
    pygame.draw.line(surface, COLOR_WHITE, (border_left, border_bottom), (border_right, border_bottom), border_width)

    # Final blit of Game Surface to screen
    # draw_game_board(RENDER_SURFACES)
    # Game to Screen
    DISPLAY_SURFACE.blit(surface, game.game_area)
    # TODO: Use 'update' for targeted draw, performance
    # pygame.display.update(self.game_window)            

def draw_game_board(surface: pygame.Surface, game: Game):
    # Blit from board copy
    surface.blit(BACKGROUND_SURFACE, (0, 0))
        
    # Selcted movement range fill
    if game.selected_range is not None:
        for space in game.selected_range:
            # logging.info("range space: {0}".format(space))

            pygame.draw.rect(surface,
                COLOR_DARK_YELLOW,
                pygame.Rect((space.x * game.cell_size) + 1, (space.y * game.cell_size) + 1,
                    game.cell_size - 1, game.cell_size - 1),
                0 # Fill the square
            )

    # Grid Selected Fill
    if game.selected_object is not None:
        column = game.selected_object.x // game.cell_size
        row = game.selected_object.y // game.cell_size

        pygame.draw.rect(surface,
            COLOR_LIGHT_GRAY,
            pygame.Rect((column * game.cell_size) + 1, (row * game.cell_size) + 1,
                game.cell_size - 1, game.cell_size - 1),
            0 # Fill the square
        )

    # Projected Path Draw
    if game.selected_path is not None:
        draw_selected_path(surface, game.selected_path, game.cell_size)

    # Mouse Hover Fill
    if game.cursor_in_grid:
        mouse_column = game.game_cursor_x // game.cell_size
        mouse_row = game.game_cursor_y // game.cell_size

        cell_surface = pygame.Surface((game.cell_size, game.cell_size))
        cell_surface.set_alpha(128) # Half transparancy
        cell_surface.fill(COLOR_LIGHT_GRAY)
        surface.blit(cell_surface,
            (mouse_column*game.cell_size, mouse_row*game.cell_size))

    # Game Object rendering
    # for go in game.game_objects:
    for go in {s for s in game.game_objects if isinstance(s, Renderable)}:
        if go.renderer is None:
            # TODO: ObjectRenderer Memoization
            # TODO: Switch/case renderer registration
            # TOOD: Set colors for teams correctly
            object_color = COLOR_WHITE
            if go in game.player_objects: object_color = COLOR_LIGHT_GREEN
            elif go in game.cpu_objects: object_color = COLOR_RED
            go.renderer = ShapeRenderer(color=object_color)
        go.draw(surface)

    # DISPLAY_SURFACE.blit(surface, game.board)

def draw_selected_path(surface: pygame.Surface, path: list, cell_size: int):
    # path.reverse()
    if len(path) > 1:
        # Loop and draw squares based on where it came from and where it is going
        for i, current in enumerate(path):
            # print(i, current)
            following = None
            if i > 0: following = path[i-1]
            previous = None
            if i < (len(path)-1): previous = path[i+1]
            draw_path_space(surface, current, previous, following, cell_size)

def draw_path_space(surface: pygame.Surface, current, previous, following, cell_size: int):
    # Draw in two halves, based on where we're coming from, and where we're going
    current_center = ((current.x * cell_size) + (cell_size // 2), (current.y * cell_size) + (cell_size // 2))
    if previous is not None:
        # Draw half from previous space to current center
        previous_diff = (current.x - previous.x, current.y - previous.y)
        # print(previous_diff)
        previous_center = (current_center[0] - (previous_diff[0] * (cell_size // 2)), current_center[1] - (previous_diff[1] * (cell_size // 2)))
        pygame.draw.line(surface, COLOR_WHITE, previous_center, current_center)

    if following is None:
        # Draw the end target
        pygame.draw.circle(surface,
            COLOR_WHITE,
            current_center,
            3, # radius
            3) # line thickness

def draw_hud(surface: pygame.Surface, game: Game):
    # Hud drawing
    surface.fill(COLOR_DARK_GRAY)
    # Track height for each row drawn
    current_height = 10 # Start 10 px down

    for key, value in game.hud_dictionary.items():
        # string_to_render = key + ": " + value
        string_to_render = "{0}: {1}".format(key, value)
        _, font_height = HUD_FONT.size(string_to_render)
        draw_text(surface, string_to_render, 10, current_height, HUD_FONT)
        current_height += font_height

    DISPLAY_SURFACE.blit(surface, game.hud)
    # pygame.display.update(game.hud)

def draw_menu(surface: pygame.Surface, game: Game):
    # Menu drawing
    # TODO: Only Draw the Menu if it's changed
    surface.fill(COLOR_DARK_GRAY)
    DISPLAY_SURFACE.blit(surface, game.menu)
    # pygame.display.update(game.menu)

def draw_text(surface: pygame.Surface, string: str, x: int, y: int, font: pygame.font.Font):
    text_surface = font.render(string, False, COLOR_WHITE)
    surface.blit(text_surface, (x, y))

def draw_centered_text(surface: pygame.Surface, string: str, x: int, y: int, font: pygame.font.Font):
    text_surface = font.render(string, False, COLOR_WHITE)
    text_rect = text_surface.get_rect(center=(x,y))
    surface.blit(text_surface, text_rect)

# TODO: Move Text Texture drawing to ObjectRenderer type
# def draw_text_texture(surface: pygame.Surface, go: BaseObject, cell_size: int):
#     # Fetch the text texture of the object
#     texture = go.text_texture
#     # Split texture into array of string
#     texture_lines = [row for row in (raw.strip() for raw in texture.splitlines()) if row]
#     # Count number of rows for texture height
#     texture_height = cell_size // len(texture_lines)
#     # Calculate texture width based on relative height size, based on first row
#     # texture_width = cell_size // len(texture_lines[0])

#     texture_font = pygame.font.Font(None, texture_height)
    
#     for i_row, t_row in enumerate(texture_lines):
#         draw_centered_text(
#             surface,
#             t_row,
#             go.x + (cell_size // 2),
#             go.y + (cell_size // 2) + (texture_height * i_row),
#             texture_font
#         )

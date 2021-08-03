import pygame
import pygame.display
import pygame.font

from Game import Game
from objects import BaseObject

# self.font = pygame.font.Font(None, self.cell_height)
COLOR_WHITE = (255, 255, 255)
COLOR_DARK_GRAY = (25, 25, 25)
COLOR_GRAY = (100, 100, 100)
COLOR_LIGHT_GRAY = (130, 130, 130)

DISPLAY_SURFACE = None # type: pygame.Surface
HUD_FONT = None # type: pygame.font.Font

def register_display_surface(surface: pygame.Surface):
    global DISPLAY_SURFACE, HUD_FONT
    DISPLAY_SURFACE = surface

    HUD_FONT = pygame.font.Font(None, 16) # Can't instantiate font before initialized

def draw_debug(debug_message: str):
    pygame.display.set_caption(debug_message)

def draw_game(surface: pygame.Surface, game: Game):
    # Background Fill
    # self.game_surface.fill((50, 50, 50))

    # Game board Border draw
    border_width = 5

    border_top = game.board.top - border_width
    border_left = game.board.left - border_width
    border_bottom = game.board.bottom + border_width
    border_right = game.board.right + border_width

    pygame.draw.line(surface, COLOR_WHITE, (border_left, border_top), (border_left, border_bottom), border_width)
    pygame.draw.line(surface, COLOR_WHITE, (border_left, border_top), (border_right, border_top), border_width)
    pygame.draw.line(surface, COLOR_WHITE, (border_right, border_top), (border_right, border_bottom), border_width)
    pygame.draw.line(surface, COLOR_WHITE, (border_left, border_bottom), (border_right, border_bottom), border_width)

    # Draw the inner game board
    draw_game_board(surface, game)

    # Final blit of Game Surface to screen
    # self.screen.blit(self.game_surface, game.game_area)
    # Game Board to Screen
    DISPLAY_SURFACE.blit(surface, game.board)
    # Use 'update' for targeted draw, performance
    # pygame.display.update(self.game_window)

def draw_game_board(surface: pygame.Surface, game: Game):
    # Game Board Draw TODO: Break out normal draw components
    surface.fill(COLOR_DARK_GRAY)

    # Grid Selected Fill
    if game.selected_object is not None:
        column = game.selected_object.x // game.cell_size
        row = game.selected_object.y // game.cell_size

        cell_surface = pygame.Surface((game.cell_size, game.cell_size))
        cell_surface.fill((COLOR_LIGHT_GRAY))
        surface.blit(cell_surface,
            (column*game.cell_size, row*game.cell_size))

    # Mouse Hover Fill
    if game.cursor_in_grid:
        # 
        mouse_column = game.game_cursor_x // game.cell_size
        mouse_row = game.game_cursor_y // game.cell_size

        cell_surface = pygame.Surface((game.cell_size, game.cell_size))
        cell_surface.fill(COLOR_GRAY)
        surface.blit(cell_surface,
            (mouse_column*game.cell_size, mouse_row*game.cell_size))

    # Projected Path Draw
    if game.selected_path is not None:
        draw_selected_path(surface, game.selected_path, game.cell_size)

    # Grid line draw
    grid_line_color = COLOR_GRAY
    for x in range (1, game.columns):
        pygame.draw.line(surface,
        grid_line_color, (x*game.cell_size, 0), (x*game.cell_size, surface.get_height()))
    for y in range (1, game.rows):
        pygame.draw.line(surface,
        grid_line_color, (0, y*game.cell_size), (surface.get_width(), y*game.cell_size))

    # Game Object - Text Texture rendering
    for go in game.game_objects:
        draw_game_object(surface, go, game.cell_size)
        
def draw_game_object(surface: pygame.Surface, go: BaseObject, cell_size: int):
    # Switch on render_mode
    if go.render_mode == "texture":
        draw_text_texture(surface, go, cell_size)
    elif go.render_mode == "shape":
        draw_object_shape(surface, go, cell_size)

def draw_selected_path(surface: pygame.Surface, path: list, cell_size: int):
    # path.reverse()
    if len(path) > 1:
        # Loop and draw squares based on where it came from and where it is going
        for i, current in enumerate(path):
            previous = None
            if i > 0: previous = path[i-1]
            following = None
            if i < (len(path)-1): following = path[i+1]
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

def draw_text_texture(surface: pygame.Surface, go: BaseObject, cell_size: int):
    # Fetch the text texture of the object
    texture = go.text_texture
    # Split texture into array of string
    texture_lines = [row for row in (raw.strip() for raw in texture.splitlines()) if row]
    # Count number of rows for texture height
    texture_height = cell_size // len(texture_lines)
    # Calculate texture width based on relative height size, based on first row
    # texture_width = cell_size // len(texture_lines[0])

    texture_font = pygame.font.Font(None, texture_height)
    
    for i_row, t_row in enumerate(texture_lines):
        draw_centered_text(
            surface,
            t_row,
            go.x + (cell_size // 2),
            go.y + (cell_size // 2) + (texture_height * i_row),
            texture_font
        )
        # for i_char, t_char in enumerate(t_row):
        #     self.draw_text(
        #         self.game_board,
        #         t_char,
        #         go.x + (texture_width*i_char),
        #         go.y + (texture_height*i_row),
        #         texture_font
        #     )

def draw_object_shape(surface: pygame.Surface, go: BaseObject, cell_size: int):
    # TODO: More than just circle
    pygame.draw.circle(surface,
        COLOR_WHITE,
        (go.x + (cell_size // 2), go.y + (cell_size // 2)),
        10, # radius
        2) # line thickness
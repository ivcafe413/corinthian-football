import logging

import pygame
import pygame.time
import pygame.display

from Game import Game
import Renderer
import LevelLoader

TARGET_FPS=30
LOOP_MS_PF=(1/TARGET_FPS)*1000
FPS_CLOCK = pygame.time.Clock() # TODO: Could DI this?

RENDER_SURFACES = dict()

# class Driver:
#     def __init__(self,
#         game: Game,
#         renderer: Renderer, # TODO: Can flatten out Renderer to more static module
#         # width: int, height: int
#     ):
#         self.game = game # <-- DI
#         self.renderer = renderer # <-- DI

#         self.clock = pygame.time.Clock() 
#         self.

def register_surfaces(**surfaces: pygame.Surface):
    global RENDER_SURFACES
    RENDER_SURFACES = surfaces

def game_loop(game: Game, debug: bool):
    Renderer.register_display_surface(RENDER_SURFACES['display'])
    loop_time_elapsed = 0
    # TODO: check Game Over from game/state
    while not game.game_over:
        loop_time_elapsed += FPS_CLOCK.get_time()

        # while Enough time has passed to tick one frame
        while loop_time_elapsed >= LOOP_MS_PF:
            # TODO: Insert Collision Handler logic here?
            game.handle_events()
            game.update() # TODO: passing in partial MS deltas
            loop_time_elapsed -= LOOP_MS_PF

        # Game is caught up, render current game state
        Renderer.draw_game(RENDER_SURFACES['board'], game) # TODO: passing in partial MS deltas

        if game.hud_change:
            Renderer.draw_hud(RENDER_SURFACES['hud'], game)
            # TODO: pygame.display.update(game.hud)
            game.hud_change = False # Reset

        Renderer.draw_menu(RENDER_SURFACES['menu'], game)

        # Renderer.full_blit(RENDER_SURFACES, "display")

        if(debug):
            fps = FPS_CLOCK.get_fps()
            # pygame.display.set_caption("FPS: {0:2f}".format(fps))
            Renderer.draw_debug("FPS: {0:2f}".format(fps))

        pygame.display.flip()
        # TODO: Reverse the flip and the clock tick?
        # Wait for next frame
        FPS_CLOCK.tick(TARGET_FPS)

def game_load(level: int, game: Game):
    # Logic to load game objects into game state
    # Initial Load - Pull map/objects from file (JSON)
    LevelLoader.load_level(level_id=level, into_game=game)
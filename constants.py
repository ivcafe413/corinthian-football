import os
import pygame

# Setting root path based on THIS FILE being at root level
ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

# Mouse Click integers
BUTTON_LEFT_CLICK = 1
BUTTON_RIGHT_CLICK = 3

# Utilizing pygame custom events
VICTORY_EVENT = pygame.USEREVENT+1

# Cardinal Directions
NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3

# Game State Constants
PLAYER_IDLE = 'player_idle'
PLAYER_SELECTED = 'player_selected'
PLAYER_PATHING = 'player_pathing'
PLAYER_MOVING = 'player_moving'
ENEMY_TURN = 'enemy_turn'
# GAME_STATES = [PLAYER_IDLE, PLAYER_SELECTED, PLAYER_PATHING, PLAYER_MOVING]
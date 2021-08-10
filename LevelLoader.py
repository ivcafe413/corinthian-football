import os
import logging

import json
import importlib

# from dotmap import DotMap

from Game import Game
from Grid import Grid
from objects import BaseObject
from constants import ROOT_PATH

LEVEL_DIRECTORY = os.path.join(ROOT_PATH, 'levels')
MAP_DIRECTORY = os.path.join(ROOT_PATH, "maps")
        
def load_level(level_id: int, into_game: Game):
    #
    level_file = os.path.join(LEVEL_DIRECTORY, str(level_id) + '.json')
    with open(level_file) as f:
        level = json.load(f)

    # Actually load the json object(level dictionary) into the game
    for go in [build_object(go, into_game) for go in level["neutral_objects"]]:
        # no = build_object(go, into_game)
        into_game.neutral_objects.add(go)

    for go in [build_object(go, into_game) for go in level["player_objects"]]:
        # no = build_object(go, into_game)
        into_game.player_objects.add(go)

    for go in [build_object(go, into_game) for go in level["cpu_objects"]]:
        # no = build_object(go, into_game)
        into_game.cpu_objects.add(go)

def build_object(go: dict, into_game: Game) -> BaseObject:
    # 'go' comes in as dictionary object
    # Module and Class of game object is referenced in the json
    module = importlib.import_module(go.pop("object_module"))
    class_ = getattr(module, go.pop("object_class"))

    # BaseObject argument building
    column = go.pop("column")
    row = go.pop("row")
    go["w"] = into_game.cell_size
    go["h"] = into_game.cell_size
    go["x"] = column * into_game.cell_size
    go["y"] = row * into_game.cell_size
    new_object = class_(**go)

    into_game.game_objects.add(new_object) # set uses 'add', list uses 'append'

    # terrain should be loaded by now
    terrain = into_game.grid[column, row].terrain
    into_game.grid[column, row] = new_object, terrain

    logging.info(into_game.grid[column, row])
    return new_object

def load_map(level_id: int, into_grid: Grid):
    map_file = os.path.join(MAP_DIRECTORY, str(level_id) + '.txt')
    with open(map_file) as f:
        for y, map_line in enumerate(f):
            clean_line = map_line.strip()
            for x, map_tile in enumerate(clean_line):
                insert_map_tile(map_tile, x, y, into_grid)

def insert_map_tile(tile: chr, x: int, y: int, into_grid: Grid):
    if tile == 'T':
        terrain = "Endzone"
    elif tile == '_':
        terrain = "Blank"
    else: # Skip invalid tiles for arbitrary shapes
        return

    into_grid[x, y] = None, terrain
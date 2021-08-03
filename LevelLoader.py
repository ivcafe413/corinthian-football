import os
import json
import importlib

from dotmap import DotMap

from Game import Game
from constants import ROOT_PATH

LEVEL_DIRECTORY = os.path.join(ROOT_PATH, 'levels')

# class LevelLoader:
#     def __init__(self, debug: bool):
#         # 
#         self.debug = debug
#         self.
        
def load_level(level_id: int, into_game: Game):
    #
    level_file = os.path.join(LEVEL_DIRECTORY, str(level_id) + '.json')
    with open(level_file) as f:
        level = json.load(f)

    # if(debug):
    #     print(json.dumps(level, indent=2, sort_keys=False))

    # Actually load the json object(level dictionary) into the game
    for go in level["game_objects"]:
        # 'go' comes in as dictionary object
        # DotMap transforms into pythyon object
        dotmap_object = DotMap(go)
        # Module and Class of game object is referenced in the json
        module = importlib.import_module(dotmap_object.object_module)
        class_ = getattr(module, dotmap_object.object_class)

        new_object = class_(dotmap_object)
        # into_game.game_objects.append(new_object)
        into_game.insert_game_object(new_object)

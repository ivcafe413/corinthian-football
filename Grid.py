import logging
import random

from collections import namedtuple
from typing import NamedTuple
from queue import PriorityQueue

from objects import BaseObject

from constants import NORTH, SOUTH, EAST, WEST

Space = namedtuple("Space", ["x", "y"])
# TODO: Big TODO - Re-implement space with z/t value for terrain???
# SpaceMeta = namedtuple("SpaceMeta", ["actor", "terrain"], defaults=[None, "Blank"])
class SpaceMeta(NamedTuple):
    actor: BaseObject
    terrain: str = "Blank"

DIRECTIONS = [NORTH, SOUTH, WEST, EAST] # Maintained order, just cuz
GRID_DIRECTIONS = [Space(0, -1), Space(0, 1), Space(-1, 0), Space(1, 0)]

def grid_direction(direction: int) -> Space:
    return GRID_DIRECTIONS[direction]

def grid_space_add(a: Space, b: Space) -> Space:
    sum_x = a.x + b.x
    sum_y = a.y + b.y
    return Space(sum_x, sum_y)

def grid_space_neighbor(space: Space, direction: int) -> Space:
    return grid_space_add(space, grid_direction(direction))

class Grid(dict):
    def __setitem__(self, key, values):
        x,y = key
        # print(values)
        super().__setitem__(Space(x, y), SpaceMeta(*values))

    def __getitem__(self, key) -> SpaceMeta:
        x,y = key
        return super().__getitem__(Space(x, y))

    def neighbors(self, space: Space):
        # space = Space(coordinates)
        for d in DIRECTIONS:
            neighbor = grid_space_neighbor(space, d)
            if neighbor in self:
                neighbor_object = self[neighbor].actor
                if neighbor_object is None or not neighbor_object.solid: # Can't traverse through solid objects
                    yield neighbor

    def random_neighbor(self, space: Space) -> Space:
        valid_neighbors = list(self.neighbors(space))
        logging.info(valid_neighbors)
        # random.shuffle(valid_neighbors) # TODO: Unnecessary?
        r = random.randint(0, len(valid_neighbors) - 1)
        result = valid_neighbors[r]
        return result

    def cost(self, start: Space, end: Space):
        return 1 # TODO: More complex movement cost

# A* Pathfinding 
def path_find(start: tuple, goal: tuple, graph: Grid):
    """Pathfinding graph algorithm"""
    start = Space(*start)
    goal = Space(*goal)

    frontier = PriorityQueue()
    frontier.put((0, start))

    came_from = dict()
    came_from[start] = None

    cost_so_far = dict()
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()[1]

        if current == goal:
            break

        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + grid_distance(next, goal)
                frontier.put((priority, next))
                came_from[next] = current

    return came_from, cost_so_far

# Dijkstra's Rangefinding
def range_find(start: tuple, range: int, graph: Grid):
    start = Space(*start)

    frontier = PriorityQueue()
    frontier.put((0, start))

    came_from = dict()
    came_from[start] = None

    cost_so_far = dict()
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()[1]
        # No goal/early exit
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if new_cost < range and (next not in cost_so_far or new_cost < cost_so_far[next]):
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier.put((priority, next))
                came_from[next] = current
    return came_from, cost_so_far

def path_reconstruct(start: tuple, goal: tuple, search_result: dict) -> list:
    result_path = list()
    start = Space(*start)
    current = Space(*goal)
    
    while search_result[current] is not None:
        # Add current location to reverse path
        result_path.append(current)
        current = search_result[current]
    # Reached start, add start to path
    result_path.append(start)
    # Reverse the path to generate foward path TODO Optional flag?
    # result_path.reverse()
    return result_path

def grid_distance(a: Space, b: Space):
    # Manhattan distance, square grid
    return abs(a.x - b.x) + abs(a.y - b.y)

# ----- Testing Area -----
def test_hash():
    test_coordinates = (0, 0)
    space_a = Space(test_coordinates)
    space_b = Space(test_coordinates)
    if not hash(space_a) == hash(space_b):
        print("Hash equality NOT working")
    else:
        print("Hash equality working on named tuples")

def test_hash_to_non_named_tuple():
    test_coordinates = (1, 1)
    test_grid_space = Space((1, 1))
    if not hash(test_coordinates) == hash(test_grid_space):
        print("CanNOT compare hashes from named/non-named tuples")
    else:
        print("Can indeed compare hashes of regular and named tuples across")

def test_compare_tuple_named_tuple():
    test_coordinates = (1, 1)
    test_grid_space = Space((1, 1))

    if not test_coordinates == test_grid_space:
        print("CanNOT compare equality from named/non-named tuples")
    else:
        print("Can indeed compare equality of regular and named tuples across")

def test_grid_dict_subclass():
    test_coordinates = (0, 0)
    grid = Grid(1, 1)
    # grid.map[space_a] = 5
    grid[test_coordinates] = 5
    # space_c = Space(0, 0)
    test_get = grid[test_coordinates]
    if not test_get == 5:
        print("Hashtable set/fetch NOT working")
    else:
        print("Hashtable set and get by Space coordinates working")

def test_all():
    test_hash()
    test_grid_dict_subclass()
    test_hash_to_non_named_tuple()
    test_compare_tuple_named_tuple()

if __name__ == "__main__":
    # Run Tests
    test_all()
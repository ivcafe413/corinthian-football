from collections import namedtuple
from queue import PriorityQueue
from constants import NORTH, SOUTH, EAST, WEST

_GridSpace = namedtuple("GridSpace", ["x", "y"])

def GridSpace(coordinates: tuple):
    return _GridSpace(x=coordinates[0], y=coordinates[1])

DIRECTIONS = [NORTH, SOUTH, WEST, EAST] # Maintained order, just cuz
GRID_DIRECTIONS = [GridSpace((0, -1)), GridSpace((0, 1)), GridSpace((-1, 0)), GridSpace((1, 0))]

def grid_direction(direction: int) -> GridSpace:
    return GRID_DIRECTIONS[direction]

def grid_space_add(a: GridSpace, b: GridSpace) -> GridSpace:
    # print("grid_space_add_a: " + str(a))
    # print("grid_space_add_b: " + str(b))

    sum_x = a.x + b.x
    sum_y = a.y + b.y
    return GridSpace((sum_x, sum_y))

def grid_space_neighbor(space: GridSpace, direction: int) -> GridSpace:
    return grid_space_add(space, grid_direction(direction))

class Grid(dict):
    def __setitem__(self, key: tuple, value):
        super().__setitem__(GridSpace(key), value)

    def __getitem__(self, key: tuple):
        return super().__getitem__(GridSpace(key))

    def __init__(self, columns: int, rows: int):
        # 
        self.columns = columns
        self.rows = rows
        for x in range(columns):
            for y in range(rows):
                self[(x, y)] = None

    # def find(self, object):

    def neighbors(self, space: GridSpace):
        # space = GridSpace(coordinates)
        for d in DIRECTIONS:
            neighbor = grid_space_neighbor(space, d)
            if neighbor in self:
                yield neighbor

    def cost(self, start: GridSpace, end: GridSpace):
        return 1 # TODO: More complex movement cost

def path_find(start: tuple, goal: tuple, graph: Grid):
    """Pathfinding graph algorithm"""
    start = GridSpace(start)
    goal = GridSpace(goal)

    # print("pathfind_start: " + str(start))
    # print("pathfind_end: " + str(goal))

    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = dict()
    cost_so_far = dict()
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()[1]

        if current == goal:
            break

        for next in graph.neighbors(current):
            #
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal)
                frontier.put((priority, next))
                came_from[next] = current

    return came_from, cost_so_far

def path_reconstruct(start: tuple, goal: tuple, search_result: dict) -> list:
    result_path = list()
    start = GridSpace(start)
    current = GridSpace(goal)
    
    while search_result[current] is not None:
        # Add current location to reverse path
        result_path.append(current)
        current = search_result[current]
    # Reached start, add start to path
    result_path.append(start)
    # Reverse the path to generate foward path TODO Optional flag?
    # result_path.reverse()
    return result_path

def heuristic(a: GridSpace, b: GridSpace):
    # Manhattan distance, square grid
    return abs(a.x - b.x) + abs(a.y - b.y)

def test_hash():
    test_coordinates = (0, 0)
    space_a = GridSpace(test_coordinates)
    space_b = GridSpace(test_coordinates)
    if not hash(space_a) == hash(space_b):
        print("Hash equality NOT working")
    else:
        print("Hash equality working on named tuples")

def test_hash_to_non_named_tuple():
    test_coordinates = (1, 1)
    test_grid_space = GridSpace((1, 1))
    if not hash(test_coordinates) == hash(test_grid_space):
        print("CanNOT compare hashes from named/non-named tuples")
    else:
        print("Can indeed compare hashes of regular and named tuples across")

def test_compare_tuple_named_tuple():
    test_coordinates = (1, 1)
    test_grid_space = GridSpace((1, 1))

    if not test_coordinates == test_grid_space:
        print("CanNOT compare equality from named/non-named tuples")
    else:
        print("Can indeed compare equality of regular and named tuples across")

def test_grid_dict_subclass():
    test_coordinates = (0, 0)
    grid = Grid(1, 1)
    # grid.map[space_a] = 5
    grid[test_coordinates] = 5
    # space_c = GridSpace(0, 0)
    test_get = grid[test_coordinates]
    if not test_get == 5:
        print("Hashtable set/fetch NOT working")
    else:
        print("Hashtable set and get by GridSpace coordinates working")

def test_all():
    test_hash()
    test_grid_dict_subclass()
    test_hash_to_non_named_tuple()
    test_compare_tuple_named_tuple()

if __name__ == "__main__":
    # Run Tests
    test_all()
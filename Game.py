import sys
import logging
from functools import cache

import pygame
import pygame.mouse
import pygame.event

from Grid import Grid, path_find, path_reconstruct, range_find
from objects import BaseObject, Moveable, Ball
from constants import VICTORY_EVENT, BUTTON_LEFT_CLICK, BUTTON_RIGHT_CLICK
from constants import PLAYER_IDLE, PLAYER_SELECTED, PLAYER_PATHING, PLAYER_MOVING

# State Machine import
from transitions import Machine
from StateMachine import STATES, TRANSITIONS

class Game:
    def __init__(
        self,
        board: pygame.Rect,
        cell_size: int,
        game_area: pygame.Rect,
        hud: pygame.Rect,
        menu: pygame.Rect):
        # 2D rectangular game area
        self.board = board
        
        # self.columns = columns
        # self.rows = rows
        self.cell_size = cell_size

        # UI Areas/Rects
        self.game_area = game_area
        self.hud = hud
        self.menu = menu

        # Full list of game objects the Game is tracking for state
        self.game_objects = set()
        self.player_objects = set()
        self.cpu_objects = set()
        self.neutral_objects = set()

        # Game grid (graph for location/movement/pathfinding)
        self.grid = Grid()

        # Game state variables
        self.selected_object = None # type: BaseObject
        self.selected_path = None # type: list
        self.selected_range = None # type: dict

        self.game_over = False # Win/loss condition

        self.hud_change = True # Need to evaulate HUD on initialization
        self.hud_dictionary = dict()
        self.menu_change = True # Evaluated on initialization
        self.menu_dictionary = {
            "end_turn": "End Turn"
        }
        
        # self.cursor_x = None
        # self.cursor_y = None

        self.cursor_on_board = False
        self.cursor_in_grid = False

        self.keydown_handlers = dict()
        self.keyup_handlers = dict()
        
        # Finite state machine
        self.state_machine = Machine(model=self,
            states=STATES,
            transitions=TRANSITIONS,
            initial=PLAYER_IDLE,
            ignore_invalid_triggers=True
            # prepare_event='what_was_clicked')
        )

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            for handler in self.keydown_handlers[event.key]:
                handler()
        elif event.type == pygame.KEYUP:
            for handler in self.keyup_handlers[event.key]:
                handler()
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_motion_handler()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # logging.info("Clicked: ({0:d}, {1:d})".format(self.cursor_x, self.cursor_y))
            self.mouse_button_handler(event.button)
        elif event.type == VICTORY_EVENT:
            self.game_over = True

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)

    # Memoization
    @cache
    def point_to_space(self, x: int, y: int) -> tuple[int, int]:
        column = x // self.cell_size
        row = y // self.cell_size
        return (column, row)

    @cache
    def space_to_point(self, column: int, row: int) -> tuple[int, int]:
        x = column * self.cell_size
        y = row * self.cell_size
        return (x, y)

    @cache
    def board_collision_check(self, x: int, y: int) -> bool:
        # Calculare relative mouse position to game board and check bounds
        # result = self.board.collidepoint(x, y)
        # logging.info(result)
        return self.board.collidepoint(x, y)

    @cache
    def grid_collision_check(self, x: int, y: int) -> bool:
        column, row = self.point_to_space(x, y)
        return (column, row) in self.grid

    def mouse_motion_handler(self):
        mouse_position = pygame.mouse.get_pos()
        # self.cursor_x = mouse_position[0]
        # self.cursor_y = mouse_position[1]

        # Set board-relative cursor
        self.cursor_on_board = self.board_collision_check(mouse_position[0], mouse_position[1])
        if self.cursor_on_board:
            self.game_cursor_x = mouse_position[0] - self.board.x
            self.game_cursor_y = mouse_position[1] - self.board.y

            self.cursor_in_grid = self.grid_collision_check(self.game_cursor_x, self.game_cursor_y)
        else:
            self.game_cursor_x = None
            self.game_cursor_y = None
            self.cursor_in_grid = False

    def mouse_button_handler(self, button: int):        
        if self.state != PLAYER_MOVING and self.cursor_in_grid:
            logging.info("Clicked in grid: ({0:d}, {1:d})".format(self.game_cursor_x, self.game_cursor_y))
            # Offset absolute cursor position with board position for board cursor position
            # column = self.game_cursor_x // self.cell_size
            # row = self.game_cursor_y // self.cell_size
            column, row = self.point_to_space(self.game_cursor_x, self.game_cursor_y)

            if button == BUTTON_LEFT_CLICK:
                # Select/Deselect actions
                self.left_click(column, row) # State Transition
            elif button == BUTTON_RIGHT_CLICK:
                # Command/Perform actions
                self.right_click(column, row) # State Transition

    # Helpers
    def actor_in_space(self, column, row) -> BaseObject:
        # Find object in this space
        grid_object = self.grid[column, row]
        logging.info("actor_in_space: " + str(grid_object.actor))
        return grid_object.actor

    def terrain_in_space(self, column, row):
        return self.grid[column, row].terrain

    # State Callbacks
    def player_selection_change(self, column=0, row=0):
        # On Grid Object selection/deselection
        # self.selected_object = self.what_was_clicked(column, row) # Object or None

        self.hud_change = True

    def player_deselect_object(self, column=0, row=0):
        self.selected_object = None
        self.selected_path = None # Deselect any selected path
        self.selected_range = None

    def player_select_object(self, column, row):
        clicked_object = self.actor_in_space(column, row) # Object or None
        if clicked_object in self.player_objects:
            self.selected_object = clicked_object
            # Build/display movement range (frontier, breadth-first)
            self.selected_range, _ = range_find((column, row), self.selected_object.movement_range, self.grid)

    def player_select_path(self, column, row):
        # starting_column = self.selected_object.x // self.cell_size
        # starting_row = self.selected_object.y // self.cell_size

        start = self.point_to_space(self.selected_object.x, self.selected_object.y)
        goal = (column, row)

        came_from, _ = path_find(start, goal, self.grid)
        path = path_reconstruct(start, goal, came_from)

        self.selected_path = path
        logging.info(self.selected_path)

    # Transition Conditions
    def selectable_object_clicked(self, column, row):
        grid_object = self.actor_in_space(column, row)
        # print("selectable_object_clicked: " + str(grid_object is not None))
        # True if selectable object, False otherwise
        return grid_object is not None and grid_object.selectable

    def path_selected_twice(self, column, row):
        return self.selected_path[0] == (column, row)

    def valid_goal_selected(self, column, row):
        path_target = self.actor_in_space(column, row)
        # Incorporate Movement Range
        return (column, row) in self.selected_range and (path_target is None or not path_target.solid)

    # Transition Callbacks
    def begin_moving(self, column, row):
        self.can_click = False
        
        start = self.selected_path.pop()
        # goal = 
        self.target_node = self.selected_path[-1] # last

        self.grid[start] = None, self.grid[start].terrain
        # self.end_moving()

    def finalize_move(self):
        goal = self.selected_path[0]
        self.evaluate_goal_arrival(self.selected_object, goal)

        self.target_node = None
        self.selected_object = None
        self.selected_path = None

    def evaluate_goal_arrival(self, actor: Moveable, goal):
        target, terrain = self.grid[goal]
        # TODO: Need to build priority Dict for switch/case on target and terrain
        # Priority 1: Game Enders
        if terrain == "Endzone" and isinstance(actor.carrying, Ball):
            # TODO: Increment points, reset scrimmage
            pygame.event.post(pygame.event.Event(VICTORY_EVENT))
        # Priority 2: Ball events
        elif isinstance(target, Ball):
            if actor.can_carry and not actor.carrying:
                actor.carrying = target
            else:
                # Bounce the ball away, Blood Bowl style
                bounce_space = self.grid.random_neighbor(goal)
                _, bounce_terrain = self.grid[bounce_space]
                target.move_to(*self.space_to_point(*bounce_space))
                self.grid[bounce_space] = target, bounce_terrain
                # TODO: More deterministic bounce

        self.grid[goal] = actor, terrain

    # Game Update call (frame)
    def update(self):
        # Handle moving state
        if self.state == PLAYER_MOVING:
            # target_x = self.target_node.x * self.cell_size
            # target_y = self.target_node.y * self.cell_size
            target = self.space_to_point(*self.target_node)

            if self.selected_object.topleft == target:
                if len(self.selected_path) == 1: # We've arrived
                    self.end_moving()
                else: # There's path nodes left, pop and move on
                    self.selected_path.pop()
                    self.target_node = self.selected_path[-1]
            else:
                self.selected_object.partial_move(*target)

        # Update of all game objects
        for go in self.game_objects:
            go.update()

        # TODO: Need to add DI update logic (collision_handler)

        # HUD Check - TODO: Build a dictionary of hud items to draw
        if self.hud_change:
            # 
            self.hud_dictionary.clear()
            # If object is selected, show object information in HUD
            if self.selected_object:
                fieldlist = self.selected_object.info_list
                for field in fieldlist:
                    self.hud_dictionary[field] = getattr(self.selected_object, field)

        return self.game_over

import sys
import logging

import pygame
import pygame.mouse
import pygame.event

from Grid import Grid, path_find, path_reconstruct
from objects import BaseObject
from constants import VICTORY_EVENT, BUTTON_LEFT_CLICK, BUTTON_RIGHT_CLICK
from constants import PLAYER_IDLE, PLAYER_SELECTED, PLAYER_PATHING, PLAYER_MOVING

# State Machine import
from transitions import Machine
from StateMachine import STATES, TRANSITIONS

class Game:
    def __init__(
        self,
        board: pygame.Rect, columns: int, rows: int, cell_size: int,
        hud: pygame.Rect,
        menu: pygame.Rect):
        # 2D rectangular game area
        self.board = board
        
        self.columns = columns
        self.rows = rows
        self.cell_size = cell_size

        # UI Areas/Rects
        self.hud = hud
        self.menu = menu

        # Full list of game objects the Game is tracking for state
        self.game_objects = list()
        self.grid = Grid(columns, rows)

        # Game state variables
        self.selected_object = None # type: BaseObject
        self.selected_path = None # type: list
        self.can_click = True # type: bool

        self.game_over = False
        self.hud_change = True # Need to evaulate HUD on initialization
        self.hud_dictionary = dict()
        
        self.cursor_x = None
        self.cursor_y = None
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
    
    # @property
    # def selected_object(self):
    #     return self._selected_object

    # # TODO: Roll this into State Machine?
    # @selected_object.setter
    # def selected_object(self, go: BaseObject):
    #     old_selected_object = self._selected_object
    #     self._selected_object = go

    #     if old_selected_object is not go: # compared by hash, yes?
    #         # HUD will change
    #         self.hud_change = True

    def insert_game_object(self, go: BaseObject):
        # TODO: Over coupled?
        self.game_objects.append(go)
        column = go.x // self.cell_size
        row = go.y // self.cell_size
        self.grid[(column, row)] = go

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
            logging.info("Clicked: ({0:d}, {1:d})".format(self.cursor_x, self.cursor_y))
            
            self.mouse_button_handler(event.button)
        elif type == VICTORY_EVENT:
            self.game_over = True

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)

    def grid_collision_check(self):
        # Calculare relative mouse position to game board and check bounds
        return self.cursor_x is not None and self.cursor_y is not None and self.board.collidepoint((self.cursor_x, self.cursor_y))

    def mouse_motion_handler(self):
        mouse_position = pygame.mouse.get_pos()
        self.cursor_x = mouse_position[0]
        self.cursor_y = mouse_position[1]

        # Set board-relative cursor
        self.cursor_in_grid = self.grid_collision_check()
        if self.cursor_in_grid:
            self.game_cursor_x = self.cursor_x - self.board.x
            self.game_cursor_y = self.cursor_y - self.board.y
        else:
            self.game_cursor_x = None
            self.game_cursor_y = None

    def mouse_button_handler(self, button: int):        
        if self.can_click and self.cursor_in_grid:
            logging.info("Clicked in grid: ({0:d}, {1:d})".format(self.game_cursor_x, self.game_cursor_y))
            # Offset absolute cursor position with board position for board cursor position
            column = self.game_cursor_x // self.cell_size
            row = self.game_cursor_y // self.cell_size

            if button == BUTTON_LEFT_CLICK:
                # Select/Deselect actions
                self.left_click(column, row) # State Transition
            elif button == BUTTON_RIGHT_CLICK:
                # Command/Perform actions
                self.right_click(column, row) # State Transition

    # State Callbacks
    def player_selection_change(self, column=0, row=0):
        # On Grid Object selection/deselection
        # self.selected_object = self.what_was_clicked(column, row) # Object or None
        self.selected_path = None # Deselect any selected path
        self.hud_change = True

    def player_deselect_object(self, column=0, row=0):
        self.selected_object = None

    def player_select_object(self, column, row):
        self.selected_object = self.what_was_clicked(column, row) # Object or None

    def player_select_path(self, column, row):
        starting_column = self.selected_object.x // self.cell_size
        starting_row = self.selected_object.y // self.cell_size

        start = (starting_column, starting_row)
        goal = (column, row)

        came_from, _ = path_find(start, goal, self.grid)
        path = path_reconstruct(start, goal, came_from)

        self.selected_path = path
        logging.info(self.selected_path)

    # Transition Conditions
    def selectable_object_clicked(self, column, row):
        grid_object = self.what_was_clicked(column, row)
        # print("selectable_object_clicked: " + str(grid_object is not None))
        # True if selectable object, False otherwise
        return grid_object is not None and grid_object.selectable

    def path_selected_twice(self, column, row):
        return self.selected_path[0] == (column, row)

    def valid_goal_selected(self, column, row):
        path_target = self.what_was_clicked(column, row)
        return path_target is None or not path_target.solid

    def what_was_clicked(self, column, row):
        # Find object in this grid space
        # grid_object = self.grid[(column, row)]
        # print("what_was_clicked: " + str(grid_object))
        return self.grid[(column, row)]

    # Transition Callbacks
    def begin_moving(self, column, row):
        self.can_click = False
        
        start = self.selected_path.pop()
        # goal = 
        self.target_node = self.selected_path[-1] # last

        self.grid[(start.x, start.y)] = None
        # self.end_moving()

    def finalize_move(self):
        goal = self.selected_path[0]
        # TODO: Big todo, don't overwrite objects on the Grid by assignment
        # TODO: Maybe prevent assignment/overwrite of non-empty GridSpaces???
        self.grid[(goal.x, goal.y)] = self.selected_object

        self.target_node = None
        self.selected_object = None
        self.selected_path = None

        self.can_click = True

    # Game Update call (frame)
    def update(self):
        # Handle moving state
        if self.state == PLAYER_MOVING:
            target_x = self.target_node.x * self.cell_size
            target_y = self.target_node.y * self.cell_size
            if self.selected_object.x == target_x and self.selected_object.y == target_y:
                if len(self.selected_path) == 1: # We've arrived
                    self.end_moving()
                else: # There's path nodes left, pop and move on
                    self.selected_path.pop()
                    self.target_node = self.selected_path[-1]
            else:
                self.selected_object.partial_move(target_x, target_y)

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

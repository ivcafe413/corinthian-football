
import sys
import pygame
import pygame.mouse
import pygame.event

# from collections import defaultdict
from transitions import Machine

from Grid import Grid, path_find, path_reconstruct
from objects import BaseObject, Moveable
from constants import VICTORY_EVENT, LEFT_CLICK, RIGHT_CLICK
from constants import PLAYER_IDLE, PLAYER_SELECTED, PLAYER_PATHING, PLAYER_MOVING, GAME_STATES

class Game:
    # Static class properties
    # states = ['player_idle', 'player_selected', 'player_pathing', 'player_moving']
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
        self._selected_object = None # type: BaseObject
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
        self.click_machine = Machine(model=self, states=GAME_STATES, initial=PLAYER_IDLE,
            ignore_invalid_triggers=True
            # prepare_event='what_was_clicked')
        )
        
        # Left Click Transitions
        self.click_machine.add_transition('left_click',
            PLAYER_IDLE, PLAYER_SELECTED, 
            conditions='selectable_object_clicked',
            after='grid_select'
            )
        self.click_machine.add_transition('left_click',
            PLAYER_SELECTED, PLAYER_SELECTED,
            conditions='selectable_object_clicked',
            after='grid_select'
            )
        self.click_machine.add_transition('left_click',
            PLAYER_SELECTED, PLAYER_IDLE,
            after='grid_select'
            )

        self.click_machine.add_transition('left_click',
            PLAYER_PATHING, PLAYER_SELECTED,
            conditions='selectable_object_clicked',
            after='grid_select'
            )
        self.click_machine.add_transition('left_click',
            PLAYER_PATHING, PLAYER_IDLE,
            after='grid_select'
            )

        # Right Click Transitions
        self.click_machine.add_transition('right_click',
            PLAYER_PATHING, PLAYER_MOVING,
            conditions='path_selected_twice',
            after='begin_moving'
            )
        self.click_machine.add_transition('right_click',
            PLAYER_SELECTED, PLAYER_PATHING,
            conditions='valid_goal_selected',
            after='select_path'
            )
        self.click_machine.add_transition('right_click',
            PLAYER_PATHING, PLAYER_PATHING,
            conditions='valid_goal_selected',
            after='select_path'
            )

        # TODO: Roll into Path->Move Transition?
        self.click_machine.add_transition('end_moving',
            PLAYER_MOVING, PLAYER_IDLE,
            after="finalize_move")
    
    @property
    def selected_object(self):
        return self._selected_object

    # TODO: Roll this into State Machine?
    @selected_object.setter
    def selected_object(self, go: BaseObject):
        old_selected_object = self._selected_object
        self._selected_object = go

        if old_selected_object is not go: # compared by hash, yes?
            # HUD will change
            self.hud_change = True

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
            # if debug:
            #     debug_message = "Clicked: ({0:d}, {1:d})"
            #     print(debug_message.format(self.cursor_x, self.cursor_y))
            
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
            # if debug: print("Clicked in grid: ({0:d}, {1:d})".format(self.game_cursor_x, self.game_cursor_y))
            # Offset absolute cursor position with board position for board cursor position
            column = self.game_cursor_x // self.cell_size
            row = self.game_cursor_y // self.cell_size

            if button == LEFT_CLICK:
                # Select/Deselect actions
                self.left_click(column, row) # State Transition
            elif button == RIGHT_CLICK:
                # Command/Perform actions
                self.right_click(column, row) # State Transition

    def what_was_clicked(self, column, row):
        # Find object in this grid space
        # grid_object = self.grid[(column, row)]
        # print("what_was_clicked: " + str(grid_object))
        return self.grid[(column, row)]

    def grid_select(self, column, row):
        # grid_object = self.what_was_clicked(column, row)
        # print("select_object: " + str(grid_object))
        self.selected_object = self.what_was_clicked(column, row) # Object or None
        self.selected_path = None # Deselect any selected path 

    def selectable_object_clicked(self, column, row):
        grid_object = self.what_was_clicked(column, row)
        # print("selectable_object_clicked: " + str(grid_object is not None))
        return (grid_object is not None) # True if Object, False if None?

    def valid_goal_selected(self, column, row):
        return (self.selected_object is not None) and (self.what_was_clicked(column, row) is None)

    def path_selected_twice(self, column, row):
        return self.selected_path[0] == (column, row)

    def select_path(self, column, row):
        if self.selected_object is not None:
            starting_column = self.selected_object.x // self.cell_size
            starting_row = self.selected_object.y // self.cell_size

            start = (starting_column, starting_row)
            goal = (column, row)

            came_from, _ = path_find(start, goal, self.grid)
            path = path_reconstruct(start, goal, came_from)

            self.selected_path = path
            # print(self.selected_path)

    def begin_moving(self, column, row):
        self.can_click = False
        
        start = self.selected_path.pop()
        # goal = 
        self.target_node = self.selected_path[-1] # last
        # self.target_x = goal.x * self.cell_size
        # self.target_y = goal.y * self.cell_size
        # print("about to move_to_space: " + str(goal))
        # self.move_to_space(self.selected_object, goal.x, goal.y)
        self.grid[(start.x, start.y)] = None
        # self.end_moving()

    def finalize_move(self):
        goal = self.selected_path[0]
        self.grid[(goal.x, goal.y)] = self.selected_object

        self.target_node = None
        self.selected_object = None
        self.selected_path = None

        self.can_click = True

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

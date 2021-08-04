# States
from constants import PLAYER_IDLE, PLAYER_SELECTED, PLAYER_PATHING, PLAYER_MOVING
from transitions.core import State

STATES = [
    State(PLAYER_IDLE, on_enter=["player_selection_change", "player_deselect_object"]),
    State(PLAYER_SELECTED, on_enter=["player_selection_change", "player_select_object"]),
    State(PLAYER_PATHING, on_enter="player_select_path"),
    State(PLAYER_MOVING)
]

# Transitions
LEFT_CLICK = "left_click"
RIGHT_CLICK = "right_click"
END_MOVING = "end_moving"

TRANSITIONS = [
    { "trigger": LEFT_CLICK, "source": PLAYER_IDLE, "dest": PLAYER_SELECTED,
        "conditions": "selectable_object_clicked",
        # "after": "grid_select"
    },
    { "trigger": LEFT_CLICK, "source": PLAYER_SELECTED, "dest": PLAYER_SELECTED,
        "conditions": "selectable_object_clicked",
        # "after": "grid_select"
    },
    { "trigger": LEFT_CLICK, "source": PLAYER_PATHING, "dest": PLAYER_SELECTED,
        "conditions": "selectable_object_clicked",
        # "after": "grid_select"
    },
    { "trigger": LEFT_CLICK, "source": PLAYER_SELECTED, "dest": PLAYER_IDLE,
        # "after": "grid_select"
    },
    { "trigger": LEFT_CLICK, "source": PLAYER_PATHING, "dest": PLAYER_IDLE,
        # "after": "grid_select"
    },
    { "trigger": RIGHT_CLICK, "source": PLAYER_PATHING, "dest": PLAYER_MOVING,
        "conditions": "path_selected_twice",
        "after": "begin_moving"
    },
    { "trigger": RIGHT_CLICK, "source": PLAYER_SELECTED, "dest": PLAYER_PATHING,
        "conditions": "valid_goal_selected",
        # "after": "select_path"
    },
    { "trigger": RIGHT_CLICK, "source": PLAYER_PATHING, "dest": PLAYER_PATHING,
        "conditions": "valid_goal_selected",
        # "after": "select_path"
    },
    { "trigger": END_MOVING, "source": PLAYER_MOVING, "dest": PLAYER_IDLE,
        "before": "finalize_move" # Has to happen before on_enter_idle
    }
]
# States
from constants import PLAYER_IDLE, PLAYER_SELECTED, PLAYER_PATHING, PLAYER_MOVING
from constants import ENEMY_TURN
from transitions.core import State

STATES = [
    State(PLAYER_IDLE,
        on_enter=["player_selection_change", "player_deselect_object"]),
    State(PLAYER_SELECTED,
        on_enter=["player_selection_change", "player_select_object"]),
    State(PLAYER_PATHING,
        on_enter="player_select_path"),
    State(PLAYER_MOVING),
    State(ENEMY_TURN,
        on_enter="menu_clear",
        on_exit="menu_reload"
    )
]

# Transitions
LEFT_CLICK = "left_click"
RIGHT_CLICK = "right_click"
END_MOVING = "end_moving"
END_TURN = 'end_turn'

TRANSITIONS = [
    {
        "trigger": LEFT_CLICK,
        "source": PLAYER_IDLE,
        "dest": PLAYER_SELECTED,
        "conditions": "selectable_object_clicked",
    },
    {
        "trigger": LEFT_CLICK,
        "source": PLAYER_SELECTED,
        "dest": PLAYER_SELECTED,
        "conditions": "selectable_object_clicked",
    },
    {
        "trigger": LEFT_CLICK,
        "source": PLAYER_PATHING,
        "dest": PLAYER_SELECTED,
        "conditions": "selectable_object_clicked",
    },
    {
        "trigger": LEFT_CLICK,
        "source": PLAYER_SELECTED,
        "dest": PLAYER_IDLE,
    },
    {
        "trigger": LEFT_CLICK,
        "source": PLAYER_PATHING,
        "dest": PLAYER_IDLE,
    },
    {
        "trigger": RIGHT_CLICK,
        "source": PLAYER_PATHING,
        "dest": PLAYER_MOVING,
        "conditions": "path_selected_twice",
        "after": "begin_moving"
    },
    {
        "trigger": RIGHT_CLICK,
        "source": PLAYER_SELECTED,
        "dest": PLAYER_PATHING,
        "conditions": "valid_goal_selected",
    },
    {
        "trigger": RIGHT_CLICK,
        "source": PLAYER_PATHING,
        "dest": PLAYER_PATHING,
        "conditions": "valid_goal_selected",
    },
    {
        "trigger": END_MOVING,
        "source": PLAYER_MOVING,
        "dest": PLAYER_IDLE,
        "before": "finalize_move" # Has to happen before on_enter_idle
    },
    {
        "trigger": END_TURN,
        "source": [PLAYER_IDLE, PLAYER_SELECTED, PLAYER_PATHING],
        "dest": ENEMY_TURN,
        "after": "begin_policy_evaulation"
    },
    {
        "trigger": END_TURN,
        "source": ENEMY_TURN,
        "dest": PLAYER_IDLE
    }
]
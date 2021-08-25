from StateMachine import TRANSITIONS
from transitions.core import State

EVALUATING_POLICY = "evaluating_policy"
SEARCHING = "searching"
VALUATION = "valuation"
IDLE = "idle"

STATES = [
    State(IDLE),
    State(EVALUATING_POLICY),
    State(SEARCHING),
    State(VALUATION)
]

# Triggers
VALUE_DETERMINED = "value_determined"
POLICY_CHOICE = "policy_choice"
SEARCH_COMPLETE = "search_complete"
BOARD_DECISION = "board_decision"
EXIT_CONDITION_REACHED = "exit_condition_reached"

TRANSITIONS = [
    {
        "trigger": VALUE_DETERMINED,
        "source": VALUATION,
        "dest": EVALUATING_POLICY
    },
    {
        "trigger": POLICY_CHOICE,
        "source": EVALUATING_POLICY,
        "dest": SEARCHING,
    },
    {
        "trigger": SEARCH_COMPLETE,
        "source": SEARCHING,
        "dest": VALUATION
    },
    {
        "trigger": EXIT_CONDITION_REACHED,
        "source": "*", # Any
        "dest": IDLE
    }
]
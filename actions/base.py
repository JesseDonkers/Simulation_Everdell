from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

from shared.context_contracts import PlayCheckContext

if TYPE_CHECKING:
    from class_player import Player

__all__ = ["Action", "ActionContext", "CompositeAction"]


@dataclass
class ActionContext:
    player: "Player"
    game_state: dict[str, Any]
    host_card: Any = None
    played_card: Any = None
    trigger_location: Any = None
    event_location: Any = None
    options: dict[str, Any] = field(default_factory=dict)


class Action:
    # Default timing for effects tied to card play.
    play_timing = "post_place"
    # Whether this action can create city space before the played card is placed.
    creates_city_space_before_place = False
    # Tags describing what this action contributes to a play plan.
    play_tags: tuple[str, ...] = ()
    # Tags that are incompatible with the action.
    play_conflicts: tuple[str, ...] = ()

    def execute(
        self,
        game_state=None,
        *,
        context: ActionContext | None = None,
    ):
        """
        Template method for context-based action execution.
        """
        if context is None:
            if game_state is None:
                raise ValueError("game_state is required when no context is provided")
            active_player = game_state["current_player"]
            context = ActionContext(
                player=active_player,
                game_state=game_state,
            )

        self.execute_action(context)

    def execute_action(self, context: ActionContext):
        raise NotImplementedError

    def can_create_city_space_before_place(self, context: PlayCheckContext) -> bool:
        return self.creates_city_space_before_place


class CompositeAction(Action):
    def __init__(self, listofactions):
        self.actions = listofactions

    def execute_action(self, context: ActionContext):
        for action in self.actions:
            action.execute(context=context)

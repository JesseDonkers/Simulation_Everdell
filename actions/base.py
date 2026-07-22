from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

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


class CompositeAction(Action):
    def __init__(self, listofactions):
        self.actions = listofactions

    def execute_action(self, context: ActionContext):
        for action in self.actions:
            action.execute(context=context)

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from class_player import Player

__all__ = ["Action", "CompositeAction"]


class Action(ABC):
    def execute(self, game_state=None):
        """
        Template method: Gets the current player from game_state,
        then calls execute_action for subclasses to implement.
        """
        player = game_state["current_player"]
        self.execute_action(player, game_state)

    @abstractmethod
    def execute_action(self, player: "Player", game_state=None):
        """Subclasses override this method."""
        raise NotImplementedError


class CompositeAction(Action):
    def __init__(self, listofactions):
        self.actions = listofactions

    def execute_action(self, player: "Player", game_state=None):
        for action in self.actions:
            action.execute_action(player, game_state)

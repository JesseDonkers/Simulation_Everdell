from typing import TYPE_CHECKING

from actions.base import Action
from actions.cards import action_cards_from_meadow_to_hand
from actions.resources import action_resources_by_choice

__all__ = ["action_advance_season"]

if TYPE_CHECKING:
    from class_card import Card
    from class_location import Location
    from class_player import Player


class action_advance_season(Action):
    def _grant_man_vrouw_production_resources(self, player: "Player", game_state=None):
        if not any(card.name == "Boerderij" for card in player.city):
            return

        count_man = sum(1 for card in player.city if card.name == "Man")
        count_vrouw = sum(1 for card in player.city if card.name == "Vrouw")
        nr_pairs = min(count_man, count_vrouw)
        if nr_pairs == 0:
            return

        action_resources_by_choice(
            ["twig", "resin", "pebble", "berry"], nr_pairs
        ).execute_action(player, game_state)

    def execute_action(self, player: "Player", game_state=None):
        seasons = ["winter", "spring", "summer", "autumn"]
        current_season = player.season
        current_index = seasons.index(player.season)

        if current_season == "winter":
            player.workers_add(1)
            card: "Card"
            for card in player.city:
                if card.color == "green" and card.action_on_reactivate:
                    card.action_on_reactivate.execute(game_state)
            self._grant_man_vrouw_production_resources(player, game_state)

        elif current_season == "spring":
            player.workers_add(1)
            action_cards_from_meadow_to_hand(2).execute(game_state)

        elif current_season == "summer":
            player.workers_add(2)
            for card in player.city:
                if card.color == "green" and card.action_on_reactivate:
                    # On season change, execute action_on_reactivate
                    card.action_on_reactivate.execute(game_state)
            self._grant_man_vrouw_production_resources(player, game_state)

        location: "Location"
        for location in game_state["locations"]:
            # Do not return workers placed on permanent locations
            if location.get_player_workers(player) > 0 and not getattr(
                location, "permanent_workers", False
            ):
                location.remove_worker(player)
                player.workers_add(1)

        # Return workers from claimed event locations
        for event in player.events:
            if event.get_player_workers(player) > 0:
                event.remove_worker(player)
                player.workers_add(1)

        player.season = seasons[(current_index + 1)]

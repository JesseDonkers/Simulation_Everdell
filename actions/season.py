from typing import TYPE_CHECKING

from actions.base import Action, ActionContext
from actions.cards import (
    action_cards_from_meadow_to_hand,
    action_reactivate_all_green_cards,
)
from actions.locations import action_activate_worker_location_for_point_token

__all__ = ["action_advance_season"]

if TYPE_CHECKING:
    from class_location import Location
    from class_player import Player


class action_advance_season(Action):
    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        seasons = ["winter", "spring", "summer", "autumn"]
        current_season = player.season
        current_index = seasons.index(player.season)

        if current_season == "winter":
            player.workers_add(1)
            action_reactivate_all_green_cards().execute(context=context)

        elif current_season == "spring":
            player.workers_add(1)
            action_cards_from_meadow_to_hand(2).execute(context=context)

        elif current_season == "summer":
            player.workers_add(2)
            action_reactivate_all_green_cards().execute(context=context)

        location: "Location"
        # Clock Tower: spend a point token to activate a location where a
        # worker is deployed, before workers are brought back.
        for card in player.city:
            if card.name == "Klokkentoren":
                action_activate_worker_location_for_point_token(
                    ["basic", "forest"]
                ).execute(
                    context=ActionContext(
                        player=player,
                        game_state=game_state,
                        host_card=card,
                        options=dict(context.options),
                    )
                )

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

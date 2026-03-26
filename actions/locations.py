from typing import TYPE_CHECKING, Any

from actions.base import Action
from engine.selectors import get_possible_locations

__all__ = [
    "action_add_destination_card_as_location",
    "action_add_destination_if_card_present",
    "action_location_copy_action",
    "action_place_worker",
    "action_remove_destination",
    "action_replace_worker",
]

if TYPE_CHECKING:
    from class_location import Location
    from class_player import Player


def _resolve_worker_placement(
    player: "Player",
    location: "Location",
    game_state=None,
    remove_from_supply=True,
):
    location.add_worker(player)

    if remove_from_supply:
        player.workers_remove(1)

    # If another player uses your open destination location, owner
    # gains 1 token.
    if location.location_type == "destination_card":
        owner = getattr(location, "owner", None)
        if owner is not None and owner != player and location.is_open:
            owner.points_add("token", 1)

    location.action.execute(game_state)


class action_place_worker(Action):
    def execute_action(self, player: "Player", game_state=None):
        preferred_location: "Location"
        possib_loc = get_possible_locations(game_state)

        if len(possib_loc) == 0:
            raise ValueError("No possible locations to place worker")

        preferred_location = player.decide(
            game_state, "location_place_worker", possib_loc
        )
        _resolve_worker_placement(
            player, preferred_location, game_state, remove_from_supply=True
        )


class action_add_destination_card_as_location(Action):
    def __init__(
        self,
        name: str,
        location_type: str,
        maxworkers: int,
        action: Any,
        *,
        is_open: bool = False,
        permanent_workers: bool = False,
    ) -> None:
        self.name = name
        self.location_type = location_type
        self.is_open = is_open
        self.maxworkers = maxworkers
        self.action = action
        self.permanent_workers = permanent_workers

    def execute_action(self, player: "Player", game_state=None):
        from class_location import Location

        locations = game_state["locations"]
        dest_card = Location(
            self.name,
            self.location_type,
            self.maxworkers,
            self.action,
            is_open=self.is_open,
            permanent_workers=self.permanent_workers,
            owner=player,
        )
        locations.append(dest_card)


class action_add_destination_if_card_present(Action):
    """
    Add a destination_card location only if a specified card is present in the
    current player's city.
    """

    def __init__(
        self,
        name: str,
        location_type: str,
        maxworkers: int,
        action: Any,
        check_card_name: str,
        *,
        is_open: bool = False,
        permanent_workers: bool = False,
    ) -> None:
        self.name = name
        self.location_type = location_type
        self.is_open = is_open
        self.maxworkers = maxworkers
        self.action = action
        self.check_card_name = check_card_name
        self.permanent_workers = permanent_workers

    def execute_action(self, player: "Player", game_state=None):
        from class_location import Location

        locations = game_state["locations"]

        # Check if the specified card is in the player's city
        card_in_city = any(
            card.name == self.check_card_name for card in player.city
        )

        if card_in_city:
            dest_card = Location(
                self.name,
                self.location_type,
                self.maxworkers,
                self.action,
                is_open=self.is_open,
                permanent_workers=self.permanent_workers,
                owner=player,
            )
            locations.append(dest_card)


class action_remove_destination(Action):
    """
    Remove a destination location by name.
    Typically used when a card that created the location is discarded.
    """

    def __init__(self, location_name):
        self.location_name = location_name

    def execute_action(self, player: "Player", game_state=None):
        locations = game_state["locations"]
        targets = [loc for loc in locations if loc.name == self.location_name]

        temp_loc = next(
            l for l in locations if l.location_type == "temporary"
        )
        perm_loc = next(
            l for l in locations if l.location_type == "permanent"
        )

        for loc in targets:
            # Choose where to move workers depending on the source location
            if getattr(loc, "permanent_workers", False):
                safe_loc = perm_loc
            else:
                safe_loc = temp_loc

            # Copy items to avoid mutation during iteration
            for p, count in list(loc.workers.items()):
                for _ in range(count):
                    loc.remove_worker(p)
                    safe_loc.add_worker(p)

        # Remove the specified location(s)
        locations[:] = [l for l in locations if l.name != self.location_name]


class action_location_copy_action(Action):
    def __init__(self, possible_types):
        self.possible_types = possible_types

    def execute_action(self, player: "Player", game_state=None):
        locations = game_state["locations"]
        locations_of_type = [
            l for l in locations if l.location_type in self.possible_types
        ]
        loc = player.decide(
            game_state, "location_place_worker", locations_of_type
        )
        loc.action.execute(game_state)


class action_replace_worker(Action):
    def execute_action(self, player: "Player", game_state=None):
        # A worker can only be taken from locations where this player's worker
        # is present and the worker is allowed to be removed.
        removable_locations = [
            loc
            for loc in game_state["locations"]
            if loc.get_player_workers(player) > 0
            and not getattr(loc, "permanent_workers", False)]

        if len(removable_locations) == 0:
            raise ValueError("No placed worker can be removed")

        loc_from = player.decide(
            game_state,
            "location_take_worker",
            removable_locations)
        
        loc_from.remove_worker(player)

        possible_target_locations = [
            loc
            for loc in get_possible_locations(game_state)
            if loc != loc_from        ]

        if len(possible_target_locations) == 0:
            raise ValueError("No possible location to replace worker")

        loc_to = player.decide(
            game_state,
            "location_place_worker",
            possible_target_locations)
        
        _resolve_worker_placement(
            player, loc_to, game_state, remove_from_supply=False
        )

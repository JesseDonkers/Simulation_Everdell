from typing import TYPE_CHECKING

from actions.base import Action
from engine.selectors import get_possible_locations

__all__ = [
    "action_add_destination_card_as_location",
    "action_add_destination_if_card_present",
    "action_location_copy_action",
    "action_place_worker",
    "action_remove_destination",
]

if TYPE_CHECKING:
    from Class_Location import Location
    from Class_Player import Player


class action_place_worker(Action):
    def execute_action(self, player: "Player", game_state=None):
        preferred_location: "Location"
        possib_loc = get_possible_locations(game_state)

        if len(possib_loc) == 0:
            raise ValueError("No possible locations to place worker")

        preferred_location = player.decide(game_state, "location", possib_loc)
        preferred_location.add_worker(player)
        player.workers_remove(1)
        preferred_location.action.execute(game_state)


class action_add_destination_card_as_location(Action):
    def __init__(self, name, type, open, maxworkers, action, permanent_workers=False):
        self.name = name
        self.type = type
        self.open = open
        self.maxworkers = maxworkers
        self.action = action
        self.permanent_workers = permanent_workers

    def execute_action(self, player: "Player", game_state=None):
        from Class_Location import Location

        locations = game_state["locations"]
        dest_card = Location(
            self.name,
            self.type,
            self.open,
            self.maxworkers,
            self.action,
            permanent_workers=self.permanent_workers,
        )
        locations.append(dest_card)


class action_add_destination_if_card_present(Action):
    """
    Add a destination_card location only if a specified card is present in the
    current player's city.
    """

    def __init__(self, name, type, open, maxworkers, action, check_card_name, permanent_workers=False):
        self.name = name
        self.type = type
        self.open = open
        self.maxworkers = maxworkers
        self.action = action
        self.check_card_name = check_card_name
        self.permanent_workers = permanent_workers

    def execute_action(self, player: "Player", game_state=None):
        from Class_Location import Location

        locations = game_state["locations"]

        # Check if the specified card is in the player's city
        card_in_city = any(card.name == self.check_card_name for card in player.city)

        if card_in_city:
            dest_card = Location(
                self.name,
                self.type,
                self.open,
                self.maxworkers,
                self.action,
                permanent_workers=self.permanent_workers,
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

        temp_loc = next(l for l in locations if l.type == "temporary")
        perm_loc = next(l for l in locations if l.type == "permanent")

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
    def __init__(self, possible_locations):
        self.possible_locations = possible_locations

    def execute_action(self, player: "Player", game_state=None):
        locations = game_state["locations"]
        locations_of_type = [l for l in locations if l.type in self.possible_locations]
        loc = player.decide(game_state, "location", locations_of_type)
        loc.action.execute(game_state)

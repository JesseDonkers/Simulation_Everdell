from typing import TYPE_CHECKING

from actions.base import Action

__all__ = [
    "action_points_for_given_resources",
    "action_points_for_payed_resources",
    "action_points_general",
    "actions_points_for_cards_in_city",
    "actions_points_for_resources_event_location",
    "actions_points_for_resources_hand",
    "action_points_for_discarding_cards",
]

if TYPE_CHECKING:
    from class_player import Player
    from class_discard_pile import DiscardPile
    from class_card import Card


class action_points_general(Action):
    def __init__(self, category, points):
        self.category = category
        self.points = points

    def execute_action(self, player: "Player", game_state=None):
        player.points[self.category] += self.points


class action_points_for_given_resources(Action):
    """
    Action that handles three patterns:

    - Fixed choose type
        player chooses which resources to give, fixed points
        (nr_resources=2, points=4)

    - Max fixed type
        Player chooses how many to give (up to max), resource type fixed, and
        points per resource
        (max_nr_resources=2, resource_type='berry', points_per_resource=2)

    - Max choose type
        Player chooses how many resources to give (up to max), resource types
        chosen freely, and points per resource
        (max_nr_resources=3, points_per_resource=2)
    """

    def __init__(
        self,
        nr_resources=None,
        points=None,
        max_nr_resources=None,
        resource_type=None,
        points_per_resource=None,
    ):
        if nr_resources is not None and points is not None:
            self.mode = "fixed_choose_types"
            self.nr_resources = nr_resources
            self.points = points
        elif (
            max_nr_resources is not None
            and resource_type is not None
            and points_per_resource is not None
        ):
            self.mode = "max_fixed_type"
            self.max_nr_resources = max_nr_resources
            self.resource_type = resource_type
            self.points_per_resource = points_per_resource
        elif max_nr_resources is not None and points_per_resource is not None:
            self.mode = "max_choose_types"
            self.max_nr_resources = max_nr_resources
            self.points_per_resource = points_per_resource
        else:
            raise ValueError(
                "Invalid arguments for action_points_for_given_resources"
            )

    def _get_available_resources(self, player: "Player"):
        return {
            resource_type: player.resources.get(resource_type, 0)
            for resource_type in ("twig", "resin", "pebble", "berry")
        }

    def execute_action(self, player: "Player", game_state=None):
        players = game_state["players"]
        eligible_receivers = [
            p for p in players if p != player and not p.finished
        ]
        if len(eligible_receivers) == 0:
            return

        other_player = player.decide(
            game_state, "player_to_receive_resources", eligible_receivers
        )

        if self.mode == "fixed_choose_types":
            available = self._get_available_resources(player)
            actual_nr = min(self.nr_resources, sum(available.values()))
            if actual_nr == 0:
                raise ValueError("No resources can be given away")

            requested_resources = player.decide(
                game_state, "resource_give_away", (actual_nr, available)
            )

            for resource_type in requested_resources:
                player.resources_remove(resource_type, 1)
                other_player.resources_add(resource_type, 1)
            player.points["token"] += self.points

        elif self.mode == "max_fixed_type":
            available = player.resources.get(self.resource_type, 0)
            max_allowed = min(self.max_nr_resources, available)
            requested = player.decide(
                game_state, "nr_resources_to_give_away", max_allowed
            )
            nr_give_away = max(0, min(requested, max_allowed))

            for _ in range(nr_give_away):
                player.resources_remove(self.resource_type, 1)
                player.points["token"] += self.points_per_resource
                other_player.resources_add(self.resource_type, 1)

        else:  # max_choose_types
            available = self._get_available_resources(player)
            max_allowed = min(self.max_nr_resources, sum(available.values()))
            requested = player.decide(
                game_state, "nr_resources_to_give_away", max_allowed
            )
            nr_give_away = max(0, min(requested, max_allowed))
            if nr_give_away == 0:
                return

            requested_resources = player.decide(
                game_state, "resource_give_away", (nr_give_away, available)
            )
            
            for resource_type in requested_resources:
                player.resources_remove(resource_type, 1)
                player.points["token"] += self.points_per_resource
                other_player.resources_add(resource_type, 1)


class action_points_for_payed_resources(Action):
    def __init__(
        self,
        max_nr_resources=None,
        resource_type=None,
        points_per_resource=None,
    ):
        self.max_nr_resources = max_nr_resources
        self.resource_type = resource_type
        self.points_per_resource = points_per_resource

    def execute_action(self, player: "Player", game_state=None):
        available = player.resources.get(self.resource_type, 0)
        max_allowed = min(self.max_nr_resources, available)
        requested = player.decide(
            game_state, "nr_resources_for_points", max_allowed
        )
        nr_give_away = max(0, min(requested, max_allowed))

        for _ in range(nr_give_away):
            player.resources_remove(self.resource_type, 1)
            player.points["token"] += self.points_per_resource


class actions_points_for_resources_hand(Action):
    def __init__(self, resources, point_per_resource):
        self.resources = resources
        self.point_per_resource = point_per_resource

    def execute_action(self, player: "Player", game_state=None):
        for r in self.resources:
            qty = player.resources.get(r, 0)
            for _ in range(qty):
                player.points_add("prosperity", self.point_per_resource)


class actions_points_for_resources_event_location(Action):
    def __init__(self, resources, point_per_resource, location_name=None):
        self.resources = resources
        self.point_per_resource = point_per_resource
        self.location_name = location_name

    def execute_action(self, player: "Player", game_state=None):
        target_location = next(
            (loc for loc in player.events if loc.name == self.location_name),
            None,
        )

        total_resources = sum(
            target_location.resources.get(resource_type, 0)
            for resource_type in self.resources
        )

        player.points_add("event", total_resources * self.point_per_resource)


class actions_points_for_cards_in_city(Action):
    def __init__(self, critter_or_construction, unique, points_per_card):
        self.critter_or_construction = critter_or_construction
        self.unique = unique
        self.points_per_card = points_per_card

    def execute_action(self, player: "Player", game_state=None):
        for card in player.city:
            if (
                card.unique is self.unique
                and type(card).__name__ == self.critter_or_construction
            ):
                player.points_add("prosperity", self.points_per_card)


class action_points_for_discarding_cards(Action):
    def __init__(self, max_nr, points_per_card):
        self.max_nr = max_nr
        self.points_per_card = points_per_card    

    def execute_action(self, player: "Player", game_state=None):
        discardpile: "DiscardPile" = game_state["discardpile"]

        # Player decides how many cards to discard
        max_allowed = min(self.max_nr, len(player.hand))
        nr_discard = player.decide(
            game_state, "nr_cards_discard_hand", max_allowed)

        # Player picks each card to discard
        selectable = player.hand.copy()
        cards_to_discard: list["Card"] = []
        for _ in range(nr_discard):
            card = player.decide(game_state, "card_discard", selectable)
            cards_to_discard.append(card)
            selectable.remove(card)

        player.cards_remove(cards_to_discard, "hand")
        discardpile.add_to_discardpile(cards_to_discard)

        # Gain point per card
        player.points_add("token", 
                          len(cards_to_discard) * self.points_per_card)

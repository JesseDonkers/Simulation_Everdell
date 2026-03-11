from typing import TYPE_CHECKING

from actions.base import Action

__all__ = [
    "action_points_for_given_resources",
    "action_points_for_payed_resources",
    "action_points_general",
    "actions_points_for_cards",
    "actions_points_for_resources_hand",
]

if TYPE_CHECKING:
    from Class_Player import Player


class action_points_general(Action):
    def __init__(self, category, points):
        self.category = category
        self.points = points

    def execute_action(self, player: "Player", game_state=None):
        player.points[self.category] += self.points


class action_points_for_given_resources(Action):
    """
    Action that handles two patterns:

    - Fixed choose type
        player chooses which resources to give, fixed points
        (nr_resources=2, points=4)

    - Max fixed type
        Player chooses how many to give (up to max), resource type fixed, and
        points per resource
        (max_nr_resources=2, resource_type='berry', points_per_resource=2)
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
        else:
            raise ValueError("Invalid arguments for action_points_for_given_resources")

    def execute_action(self, player: "Player", game_state=None):
        other_player = player.decide(game_state, "player_to_receive_resources", None)

        if self.mode == "fixed_choose_types":
            resources = player.decide(game_state, "resource_give_away", self.nr_resources)
            for resource_type in resources:
                player.resources_remove(resource_type, 1)
                other_player.resources_add(resource_type, 1)
            player.points["token"] += self.points

        else:  # max_fixed_type
            nr_and_type = [self.max_nr_resources, self.resource_type]
            nr_give_away = player.decide(game_state, "nr_resources_to_give_away", nr_and_type)

            for _ in range(nr_give_away):
                player.resources_remove(self.resource_type, 1)
                player.points["token"] += self.points_per_resource
                other_player.resources_add(self.resource_type, 1)


class action_points_for_payed_resources(Action):
    def __init__(self, max_nr_resources=None, resource_type=None, points_per_resource=None):
        self.max_nr_resources = max_nr_resources
        self.resource_type = resource_type
        self.points_per_resource = points_per_resource

    def execute_action(self, player: "Player", game_state=None):
        nr_and_type = [self.max_nr_resources, self.resource_type]
        nr_give_away = player.decide(game_state, "nr_resources_to_pay", nr_and_type)

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


class actions_points_for_cards(Action):
    def __init__(self, critter_or_construction, unique, points_per_card):
        self.critter_or_construction = critter_or_construction
        self.unique = unique
        self.points_per_card = points_per_card

    def execute_action(self, player: "Player", game_state=None):
        for card in player.city:
            if card.unique is self.unique and type(card).__name__ == self.critter_or_construction:
                player.points_add("prosperity", self.points_per_card)

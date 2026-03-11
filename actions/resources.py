from typing import TYPE_CHECKING

from actions.base import Action
from engine.selectors import get_critters_constructions_city

__all__ = [
    "action_remove_card_from_city",
    "action_resource_general",
    "action_resource_if_other_card",
    "action_resource_per_other_card",
    "action_resources_building_costs_discard",
    "action_resources_by_choice",
]

if TYPE_CHECKING:
    from Class_Player import Player
    from Class_DiscardPile import DiscardPile


class action_resource_general(Action):
    def __init__(self, resource_type, amount):
        self.resource_type = resource_type
        self.amount = amount

    def execute_action(self, player: "Player", game_state=None):
        player.resources[self.resource_type] += self.amount


class action_resource_per_other_card(Action):
    def __init__(self, cardname, resource_type, amount):
        self.cardname = cardname
        self.resource_type = resource_type
        self.amount = amount

    def execute_action(self, player: "Player", game_state=None):
        for c in player.hand:
            if c.name == self.cardname:
                player.resources[self.resource_type] += self.amount


class action_resource_if_other_card(Action):
    def __init__(self, cardname, resource_type, amount):
        self.cardname = cardname
        self.resource_type = resource_type
        self.amount = amount

    def execute_action(self, player: "Player", game_state=None):
        if any(card.name == self.cardname for card in player.hand):
            player.resources[self.resource_type] += self.amount


class action_resources_by_choice(Action):
    def __init__(self, resources, nr_resources):
        self.resources = resources
        self.nr_resources = nr_resources

    def execute_action(self, player: "Player", game_state=None):
        for _ in range(self.nr_resources):
            choice = player.decide(game_state, "resource_new", self.resources)
            player.resources_add(choice, 1)


class action_resources_building_costs_discard(Action):
    def __init__(self, critter=False, construction=False):
        self.critter = critter
        self.construction = construction

    def execute_action(self, player: "Player", game_state=None):
        critter_construction = [self.critter, self.construction]
        options = get_critters_constructions_city(game_state, critter_construction)
        card = player.decide(game_state, "card_discard", options)
        resources = card.requirements
        for resource, amount in resources.items():
            player.resources_add(resource, amount)

        card.action_on_discard.execute(game_state)


class action_remove_card_from_city(Action):
    def __init__(self, card_name):
        self.card_name = card_name

    def execute_action(self, player: "Player", game_state=None):
        card = next(c for c in player.city if c.name == self.card_name)
        player.cards_remove([card], "city")
        discard_pile: "DiscardPile" = game_state["discardpile"]
        discard_pile.add_to_discardpile([card])

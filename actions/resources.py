from typing import TYPE_CHECKING

from actions.base import Action
from engine.selectors import get_critters_constructions_city

__all__ = [
    "action_resources_for_cards",
    "action_resource_general",
    "action_resource_if_other_card",
    "action_resource_per_other_card",
    "action_resources_building_costs_discard",
    "action_resources_by_choice",
]

if TYPE_CHECKING:
    from class_player import Player
    from class_discard_pile import DiscardPile
    from class_card import Card


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
        for c in player.city:
            if c.name == self.cardname:
                player.resources[self.resource_type] += self.amount


class action_resource_if_other_card(Action):
    def __init__(self, cardname, resource_type, amount):
        self.cardname = cardname
        self.resource_type = resource_type
        self.amount = amount

    def execute_action(self, player: "Player", game_state=None):
        if any(card.name == self.cardname for card in player.city):
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


class action_resources_for_cards(Action):
    """Discard any number of cards from hand;
    gain 1 resource of choice per 2 discarded cards."""

    def execute_action(self, player: "Player", game_state=None):
        discardpile: "DiscardPile" = game_state["discardpile"]

        # Player decides how many cards to discard (0 to len(hand))
        nr_discard = player.decide(game_state, "nr_cards_discard_hand", None)
        nr_discard = (nr_discard // 2) * 2  # Round down to nearest even number

        # Player picks each card to discard
        selectable = player.hand.copy()
        cards_to_discard: list["Card"] = []
        for _ in range(nr_discard):
            card = player.decide(game_state, "card_discard", selectable)
            cards_to_discard.append(card)
            selectable.remove(card)

        player.cards_remove(cards_to_discard, "hand")
        discardpile.add_to_discardpile(cards_to_discard)

        # Gain 1 resource of choice per 2 cards discarded
        resources = ["twig", "resin", "pebble", "berry"]
        for _ in range(nr_discard // 2):
            choice = player.decide(game_state, "resource_new", resources)
            player.resources_add(choice, 1)

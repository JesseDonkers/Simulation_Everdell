from collections.abc import Sequence
from typing import TYPE_CHECKING

from actions.base import Action, ActionContext
from actions.common import resolve_city_card_target
from engine.selectors import get_critters_constructions_city
from shared.context_contracts import PlayCheckContext
from shared.game_types import (
    CardStorageKey,
    CardZone,
    DecisionKind,
    PlayTiming,
    ResourceType,
)

__all__ = [
    "action_resources_for_cards",
    "action_add_resource_to_other_player",
    "action_resource_general",
    "action_resource_if_other_card",
    "action_resource_if_paired_with_other_card",
    "action_resource_per_other_card",
    "action_resources_building_costs_discard",
    "action_resources_by_choice",
    "action_resources_by_choice_for_card_tokens",
    "action_resources_swap",
    "action_resources_to_card_storage_choice",
    "action_take_all_resources_from_card_storage",
    "action_resources_to_location",
]

if TYPE_CHECKING:
    from class_player import Player
    from class_discard_pile import DiscardPile
    from class_card import Card


def _validate_resource_types(resources):
    if any(not isinstance(resource, ResourceType) for resource in resources):
        raise TypeError("resources must contain only ResourceType values")


class action_resource_general(Action):
    def __init__(self, resource_type: ResourceType, amount: int):
        if not isinstance(resource_type, ResourceType):
            raise TypeError("resource_type must be a ResourceType")
        self.resource_type = resource_type
        self.amount = amount

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        player.resources[self.resource_type] += self.amount


class action_add_resource_to_other_player(Action):
    """Add a fixed amount of a resource to another chosen player (Herder)."""

    def __init__(self, resource_type: ResourceType, amount: int):
        _validate_resource_types((resource_type,))
        self.resource_type = resource_type
        self.amount = amount

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        eligible_receivers = [
            p for p in game_state.players if p != player and not p.finished
        ]
        if len(eligible_receivers) == 0:
            return

        other_player = player.decide(
            game_state, DecisionKind.PLAYER_TO_RECEIVE_RESOURCES, eligible_receivers
        )
        other_player.resources_add(self.resource_type, self.amount)


class action_resource_per_other_card(Action):
    def __init__(self, cardname, resource_type: ResourceType, amount: int):
        _validate_resource_types((resource_type,))
        self.cardname = cardname
        self.resource_type = resource_type
        self.amount = amount

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        for c in player.city:
            if c.name == self.cardname:
                player.resources[self.resource_type] += self.amount


class action_resource_if_other_card(Action):
    def __init__(self, cardname, resource_type: ResourceType, amount: int):
        _validate_resource_types((resource_type,))
        self.cardname = cardname
        self.resource_type = resource_type
        self.amount = amount

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        if any(card.name == self.cardname for card in player.city):
            player.resources[self.resource_type] += self.amount


class action_resource_if_paired_with_other_card(Action):
    def __init__(
        self,
        own_card_name,
        paired_card_name,
        required_card_name,
        resources,
        amount=1,
    ):
        self.own_card_name = own_card_name
        self.paired_card_name = paired_card_name
        self.required_card_name = required_card_name
        _validate_resource_types(resources)
        self.resources = resources
        self.amount = amount

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        if not any(card.name == self.required_card_name for card in player.city):
            return

        count_own = sum(1 for card in player.city if card.name == self.own_card_name)
        count_paired = sum(
            1 for card in player.city if card.name == self.paired_card_name
        )
        # On-play this action is executed after the card is added to city.
        # The just-played card is paired iff paired cards are at least as many.
        if count_paired < count_own:
            return

        action_resources_by_choice(self.resources, self.amount).execute(context=context)


class action_resources_by_choice(Action):
    def __init__(self, resources: Sequence[ResourceType], nr_resources: int):
        _validate_resource_types(resources)
        self.resources = resources
        self.nr_resources = nr_resources

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        for _ in range(self.nr_resources):
            choice = player.decide(game_state, DecisionKind.RESOURCE_NEW, self.resources)
            player.resources_add(choice, 1)


class action_resources_by_choice_for_card_tokens(Action):
    def __init__(self, card_name, resources: list[ResourceType]):
        _validate_resource_types(resources)
        self.card_name = card_name
        self.resources = resources

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        target_card = next(
            (card for card in player.city if card.name == self.card_name), None
        )
        if target_card is None:
            return

        nr_tokens = target_card.card_storage.get(CardStorageKey.POINT_TOKENS, 0)
        action_resources_by_choice(self.resources, nr_tokens).execute(context=context)


class action_resources_swap(Action):
    def __init__(self, nr_resources):
        self.nr_resources = nr_resources

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        available = {
            resource: amount
            for resource, amount in player.resources.items()
            if amount > 0
        }
        max_allowed = min(self.nr_resources, sum(available.values()))
        nr_swaps = player.decide(game_state, DecisionKind.NR_RESOURCES_SWAP, max_allowed)

        for _ in range(nr_swaps):
            selectable_resources = [
                resource for resource, amount in available.items() if amount > 0
            ]
            choice_discard = player.decide(
                game_state, DecisionKind.RESOURCE_DISCARD, selectable_resources
            )
            player.resources_remove(choice_discard, 1)
            available[choice_discard] -= 1

            resource_options = [ResourceType.TWIG, ResourceType.RESIN, ResourceType.PEBBLE, ResourceType.BERRY]
            choice_add = player.decide(game_state, DecisionKind.RESOURCE_NEW, resource_options)
            player.resources_add(choice_add, 1)


class action_resources_building_costs_discard(Action):
    play_timing = PlayTiming.PRE_PLACE

    def __init__(self, critter=False, construction=False):
        self.critter = critter
        self.construction = construction
        self.creates_city_space_before_place = critter or construction

    def can_create_city_space_before_place(self, context: PlayCheckContext) -> bool:
        if not self.creates_city_space_before_place:
            return False
        options = get_critters_constructions_city(
            context.game_state, [self.critter, self.construction]
        )
        return len(options) > 0

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        critter_construction = [self.critter, self.construction]
        options = get_critters_constructions_city(game_state, critter_construction)
        if len(options) == 0:
            # Nothing left to discard (e.g. a discount payment already
            # consumed the only eligible city card); nothing to gain.
            return
        card = player.decide(game_state, DecisionKind.CARD_DISCARD, options)
        resources = card.costs
        for resource, amount in resources.items():
            player.resources_add(resource, amount)

        if card.action_on_discard is not None:
            card.action_on_discard.execute(
                context=ActionContext(
                    player=player,
                    game_state=game_state,
                    host_card=card,
                )
            )


class action_resources_for_cards(Action):
    """Discard hand cards for chosen resource per configured card count."""

    def __init__(self, max_discard=None, cards_per_resource=2):
        self.max_discard = max_discard
        self.cards_per_resource = cards_per_resource

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        discardpile: "DiscardPile" = game_state.discardpile

        max_discard = len(player.hand)
        if self.max_discard is not None:
            max_discard = min(self.max_discard, max_discard)

        nr_discard = player.decide(game_state, DecisionKind.NR_CARDS_DISCARD_HAND, max_discard)
        nr_discard = max(0, min(nr_discard, max_discard))
        nr_discard = (nr_discard // self.cards_per_resource) * self.cards_per_resource

        # Player picks each card to discard
        selectable = player.hand.copy()
        cards_to_discard: list["Card"] = []
        for _ in range(nr_discard):
            card = player.decide(game_state, DecisionKind.CARD_DISCARD, selectable)
            cards_to_discard.append(card)
            selectable.remove(card)

        player.cards_remove(cards_to_discard, CardZone.HAND)
        discardpile.add_to_discardpile(cards_to_discard)

        resources = [ResourceType.TWIG, ResourceType.RESIN, ResourceType.PEBBLE, ResourceType.BERRY]
        for _ in range(nr_discard // self.cards_per_resource):
            choice = player.decide(game_state, DecisionKind.RESOURCE_NEW, resources)
            player.resources_add(choice, 1)


class action_resources_to_location(Action):
    def __init__(
        self,
        location_name: str,
        resources: list[ResourceType],
        max_nr_resources: int,
        points_per_resource: int | dict[ResourceType, int],
    ):
        _validate_resource_types(resources)
        if isinstance(points_per_resource, dict):
            _validate_resource_types(points_per_resource)
        self.location_name = location_name
        self.resources = resources
        self.max_nr_resources = max_nr_resources
        self.points_per_resource = points_per_resource

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        event_location = context.event_location
        target_location = event_location
        if target_location is None:
            target_location = next(
                (loc for loc in player.events if loc.name == self.location_name),
                None,
            )
        if target_location is None:
            raise ValueError(
                f"Location '{self.location_name}' not found in player events"
            )

        available = {
            resource_type: player.resources.get(resource_type, 0)
            for resource_type in self.resources
        }
        allocation = player.decide(
            game_state,
            DecisionKind.RESOURCES_TO_LOCATION,
            {
                "available": available,
                "max_nr_resources": self.max_nr_resources,
                "points_per_resource": self.points_per_resource,
            },
        )
        remaining = self.max_nr_resources
        for resource_type in self.resources:
            amount = max(
                0,
                min(
                    allocation.get(resource_type, 0),
                    available[resource_type],
                    remaining,
                ),
            )
            if amount == 0:
                continue
            player.resources_remove(resource_type, amount)
            target_location.resources_add(resource_type, amount)
            remaining -= amount


class action_resources_to_card_storage_choice(Action):
    def __init__(self, card_name: str, resources: dict[ResourceType, int]):
        self.card_name = card_name
        if not isinstance(resources, dict):
            raise TypeError(
                "action_resources_to_card_storage_choice expects a dict of "
                "resource -> amount"
            )
        _validate_resource_types(resources)
        if any(type(amount) is not int or amount < 0 for amount in resources.values()):
            raise ValueError("Stored resource amounts must be non-negative integers")
        self.resource_amounts = dict(resources)

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        context_card = context.host_card
        context_card_id = getattr(context_card, "card_id", None)
        target_card = resolve_city_card_target(
            player,
            self,
            card=context_card,
            card_id=context_card_id,
            card_name=self.card_name,
            game_state=game_state,
        )

        if len(self.resource_amounts) == 0:
            return

        storage = target_card.card_storage[CardStorageKey.RESOURCES]
        options = list(self.resource_amounts.keys())
        choice = player.decide(game_state, DecisionKind.RESOURCE_NEW, options)
        amount = self.resource_amounts.get(choice, 0)
        storage[choice] = storage.get(choice, 0) + amount


class action_take_all_resources_from_card_storage(Action):
    def __init__(self, card_name):
        self.card_name = card_name

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        context_card = context.host_card
        context_card_id = getattr(context_card, "card_id", None)
        target_card = resolve_city_card_target(
            player,
            self,
            card=context_card,
            card_id=context_card_id,
            card_name=self.card_name,
        )

        storage = target_card.card_storage[CardStorageKey.RESOURCES]
        for resource, amount in list(storage.items()):
            if amount <= 0:
                continue
            player.resources_add(resource, amount)
            storage[resource] = 0

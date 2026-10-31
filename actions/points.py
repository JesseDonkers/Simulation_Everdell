from typing import TYPE_CHECKING

from actions.base import Action, ActionContext
from shared.game_types import (
    CardStorageKey,
    CardColor,
    CardZone,
    CityAssetType,
    DecisionKind,
    PointCategory,
    LocationType,
    ResourcePointMode,
    ResourceType,
)

__all__ = [
    "action_place_point_tokens_on_card",
    "action_points_for_given_resources",
    "action_points_for_payed_resources",
    "action_points_for_tokens_on_card",
    "action_points_general",
    "action_points_for_cards_in_city",
    "action_points_for_city_assets",
    "action_points_for_color_in_city",
    "action_points_for_resources_event_location",
    "action_points_for_cards_in_event_location",
    "action_points_for_resources_hand",
    "action_points_for_discarding_cards",
    "action_points_for_events",
]


if TYPE_CHECKING:
    from class_player import Player
    from class_discard_pile import DiscardPile
    from class_card import Card


class action_place_point_tokens_on_card(Action):
    def __init__(self, nr_points):
        self.nr_points = nr_points

    def execute_action(self, context: ActionContext):
        context.host_card.card_storage[CardStorageKey.POINT_TOKENS] += self.nr_points


class action_points_for_tokens_on_card(Action):
    """Gain 1 token point for each point token on a named card in own city (Herder/Kapel)."""

    def __init__(
        self,
        card_name: str,
        points_per_token: int = 1,
        category: PointCategory = PointCategory.TOKEN,
    ):
        if not isinstance(category, PointCategory):
            raise TypeError("category must be a PointCategory")
        self.card_name = card_name
        self.points_per_token = points_per_token
        self.category = category

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        target_card = next(
            (
                city_card
                for city_card in player.city
                if city_card.name == self.card_name
            ),
            None,
        )
        if target_card is None:
            return

        nr_tokens = target_card.card_storage.get(CardStorageKey.POINT_TOKENS, 0)
        if nr_tokens > 0:
            player.points_add(self.category, nr_tokens * self.points_per_token)


class action_points_general(Action):
    def __init__(self, category: PointCategory, points: int):
        if not isinstance(category, PointCategory):
            raise TypeError("category must be a PointCategory")
        self.category = category
        self.points = points

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
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
            self.mode = ResourcePointMode.FIXED_CHOOSE_TYPES
            self.nr_resources = nr_resources
            self.points = points
        elif (
            max_nr_resources is not None
            and resource_type is not None
            and points_per_resource is not None
        ):
            if not isinstance(resource_type, ResourceType):
                raise TypeError("resource_type must be a ResourceType")
            self.mode = ResourcePointMode.MAX_FIXED_TYPE
            self.max_nr_resources = max_nr_resources
            self.resource_type = resource_type
            self.points_per_resource = points_per_resource
        elif max_nr_resources is not None and points_per_resource is not None:
            self.mode = ResourcePointMode.MAX_CHOOSE_TYPES
            self.max_nr_resources = max_nr_resources
            self.points_per_resource = points_per_resource
        else:
            raise ValueError("Invalid arguments for action_points_for_given_resources")

    def _get_available_resources(self, player: "Player"):
        return {
            resource_type: player.resources.get(resource_type, 0)
            for resource_type in (ResourceType.TWIG, ResourceType.RESIN, ResourceType.PEBBLE, ResourceType.BERRY)
        }

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        players = game_state.players
        eligible_receivers = [p for p in players if p != player and not p.finished]
        if len(eligible_receivers) == 0:
            return

        other_player = player.decide(
            game_state, DecisionKind.PLAYER_TO_RECEIVE_RESOURCES, eligible_receivers
        )

        if self.mode == ResourcePointMode.FIXED_CHOOSE_TYPES:
            available = self._get_available_resources(player)
            actual_nr = min(self.nr_resources, sum(available.values()))
            if actual_nr == 0:
                raise ValueError("No resources can be given away")

            requested_resources = player.decide(
                game_state, DecisionKind.RESOURCE_GIVE_AWAY, (actual_nr, available)
            )

            for resource_type in requested_resources:
                player.resources_remove(resource_type, 1)
                other_player.resources_add(resource_type, 1)
            player.points[PointCategory.TOKEN] += self.points

        elif self.mode == ResourcePointMode.MAX_FIXED_TYPE:
            available = player.resources.get(self.resource_type, 0)
            max_allowed = min(self.max_nr_resources, available)
            requested = player.decide(
                game_state, DecisionKind.NR_RESOURCES_FOR_POINTS, max_allowed
            )
            nr_give_away = max(0, min(requested, max_allowed))

            for _ in range(nr_give_away):
                player.resources_remove(self.resource_type, 1)
                player.points[PointCategory.TOKEN] += self.points_per_resource
                other_player.resources_add(self.resource_type, 1)

        else:  # max_choose_types
            available = self._get_available_resources(player)
            max_allowed = min(self.max_nr_resources, sum(available.values()))
            requested = player.decide(
                game_state, DecisionKind.NR_RESOURCES_FOR_POINTS, max_allowed
            )
            nr_give_away = max(0, min(requested, max_allowed))
            if nr_give_away == 0:
                return

            requested_resources = player.decide(
                game_state, DecisionKind.RESOURCE_GIVE_AWAY, (nr_give_away, available)
            )

            for resource_type in requested_resources:
                player.resources_remove(resource_type, 1)
                player.points[PointCategory.TOKEN] += self.points_per_resource
                other_player.resources_add(resource_type, 1)


class action_points_for_payed_resources(Action):
    def __init__(
        self,
        max_nr_resources=None,
        resource_type=None,
        points_per_resource=None,
    ):
        if not isinstance(resource_type, ResourceType):
            raise TypeError("resource_type must be a ResourceType")
        self.max_nr_resources = max_nr_resources
        self.resource_type = resource_type
        self.points_per_resource = points_per_resource

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        available = player.resources.get(self.resource_type, 0)
        max_allowed = min(self.max_nr_resources, available)
        requested = player.decide(game_state, DecisionKind.NR_RESOURCES_FOR_POINTS, max_allowed)
        nr_give_away = max(0, min(requested, max_allowed))

        for _ in range(nr_give_away):
            player.resources_remove(self.resource_type, 1)
            player.points[PointCategory.TOKEN] += self.points_per_resource


class action_points_for_resources_hand(Action):
    def __init__(self, resources, point_per_resource):
        if any(not isinstance(resource, ResourceType) for resource in resources):
            raise TypeError("resources must contain only ResourceType values")
        self.resources = resources
        self.point_per_resource = point_per_resource

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        for r in self.resources:
            qty = player.resources.get(r, 0)
            for _ in range(qty):
                player.points_add(PointCategory.PROSPERITY, self.point_per_resource)


class action_points_for_resources_event_location(Action):
    def __init__(self, resources, point_per_resource, location_name=None):
        if any(not isinstance(resource, ResourceType) for resource in resources):
            raise TypeError("resources must contain only ResourceType values")
        self.resources = resources
        self.point_per_resource = point_per_resource
        self.location_name = location_name

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        event_location = context.event_location
        target_location = event_location
        if target_location is None:
            target_location = next(
                (loc for loc in player.events if loc.name == self.location_name),
                None,
            )

        if target_location is None:
            raise ValueError(
                f"Event location '{self.location_name}' not found in player's events"
            )

        if isinstance(self.point_per_resource, dict):
            points = sum(
                target_location.resources.get(resource_type, 0)
                * self.point_per_resource.get(resource_type, 0)
                for resource_type in self.resources
            )
        else:
            total_resources = sum(
                target_location.resources.get(resource_type, 0)
                for resource_type in self.resources
            )
            points = total_resources * self.point_per_resource

        player.points_add(PointCategory.EVENT, points)


class action_points_for_cards_in_event_location(Action):
    def __init__(self, points_per_card=1):
        self.points_per_card = points_per_card

    def execute_action(self, context: ActionContext):
        event_location = context.event_location
        if event_location is None:
            raise ValueError("An event location is required to score stored cards")

        nr_cards = len(event_location.card_storage[CardStorageKey.CARDS])
        context.player.points_add(PointCategory.EVENT, nr_cards * self.points_per_card)


class action_points_for_cards_in_city(Action):
    def __init__(self, critter_or_construction, unique, points_per_card):
        self.critter_or_construction = critter_or_construction
        self.unique = unique
        self.points_per_card = points_per_card

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        for card in player.city:
            if (
                card.unique is self.unique
                and type(card).__name__ == self.critter_or_construction
            ):
                player.points_add(PointCategory.PROSPERITY, self.points_per_card)


class action_points_for_city_assets(Action):
    """Award event points for a countable feature of cards in the player's city."""

    def __init__(
        self,
        asset_type: CityAssetType,
        points_per_asset: int,
        *,
        card_name: str | None = None,
        paired_card_names: tuple[str, str] | None = None,
    ):
        if not isinstance(asset_type, CityAssetType):
            raise TypeError("asset_type must be a CityAssetType")
        if asset_type not in set(CityAssetType):
            raise ValueError(f"Unsupported city asset type: {asset_type}")
        if asset_type in {CityAssetType.DESTINATION_WORKERS, CityAssetType.STORED_CARDS} and card_name is None:
            raise ValueError(f"{asset_type} requires a card_name")
        if asset_type == CityAssetType.CARD_PAIRS and paired_card_names is None:
            raise ValueError("card_pairs requires paired_card_names")

        self.asset_type = asset_type
        self.points_per_asset = points_per_asset
        self.card_name = card_name
        self.paired_card_names = paired_card_names

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player

        if self.asset_type == CityAssetType.CARD_PAIRS:
            assert self.paired_card_names is not None
            first_name, second_name = self.paired_card_names
            first_count = sum(1 for card in player.city if card.name == first_name)
            second_count = sum(1 for card in player.city if card.name == second_name)
            count = min(first_count, second_count)
        else:
            assert self.card_name is not None
            city_cards = [card for card in player.city if card.name == self.card_name]

            if self.asset_type == CityAssetType.STORED_CARDS:
                count = sum(
                    len(card.card_storage.get(CardStorageKey.CARDS, [])) for card in city_cards
                )
            else:
                source_card_ids = {
                    getattr(card, "card_id", None) for card in city_cards
                }
                count = sum(
                    location.get_player_workers(player)
                    for location in context.game_state.locations
                    if location.location_type == LocationType.DESTINATION_CARD
                    and location.source_card_id in source_card_ids
                )

        if count:
            player.points_add(PointCategory.EVENT, count * self.points_per_asset)


class action_points_for_color_in_city(Action):
    def __init__(self, color: CardColor, points_per_card: int):
        if not isinstance(color, CardColor):
            raise TypeError("color must be a CardColor")
        self.color = color
        self.points_per_card = points_per_card

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        count = sum(1 for card in player.city if card.color == self.color)
        total_points = count * self.points_per_card
        if total_points > 0:
            player.points_add(PointCategory.PROSPERITY, total_points)


class action_points_for_discarding_cards(Action):
    def __init__(self, max_nr, points_per_card):
        self.max_nr = max_nr
        self.points_per_card = points_per_card

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        discardpile: "DiscardPile" = game_state.discardpile

        # Player decides how many cards to discard
        max_allowed = min(self.max_nr, len(player.hand))
        nr_discard = player.decide(game_state, DecisionKind.NR_CARDS_DISCARD_HAND, max_allowed)

        # Player picks each card to discard
        selectable = player.hand.copy()
        cards_to_discard: list["Card"] = []
        for _ in range(nr_discard):
            card = player.decide(game_state, DecisionKind.CARD_DISCARD, selectable)
            cards_to_discard.append(card)
            selectable.remove(card)

        player.cards_remove(cards_to_discard, CardZone.HAND)
        discardpile.add_to_discardpile(cards_to_discard)

        # Gain point per card
        player.points_add(PointCategory.TOKEN, len(cards_to_discard) * self.points_per_card)


class action_points_for_events(Action):
    def __init__(self, points_per_basic_event, points_for_special_event):
        self.points_per_basic_event = points_per_basic_event
        self.points_for_special_event = points_for_special_event

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        basic_events = sum(
            1 for event in player.events if event.location_type == LocationType.BASIC_EVENT
        )
        special_events = sum(
            1 for event in player.events if event.location_type == LocationType.SPECIAL_EVENT
        )

        total_points = (
            basic_events * self.points_per_basic_event
            + special_events * self.points_for_special_event
        )
        if total_points > 0:
            player.points_add(PointCategory.PROSPERITY, total_points)

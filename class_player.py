from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from shared.game_types import (
    CardZone,
    DecisionKind,
    PointCategory,
    ResourceType,
    Season,
)

if TYPE_CHECKING:
    from class_card import Card
    from class_location import Location
    from shared.game_state import GameState


@dataclass(eq=False)
class Player:
    index: int = 0
    strategy: Any = None
    hand: list[Card] = field(default_factory=list)
    city: list[Card] = field(default_factory=list)
    workers: int = 0
    season: Season = Season.WINTER
    points: dict[PointCategory, int] = field(
        default_factory=lambda: {category: 0 for category in PointCategory}
    )
    resources: dict[ResourceType, int] = field(
        default_factory=lambda: {resource: 0 for resource in ResourceType}
    )
    finished: bool = False
    events: list[Location] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.season, Season):
            raise TypeError("season must be a Season")
        if any(not isinstance(resource, ResourceType) for resource in self.resources):
            raise TypeError("Player resources must use ResourceType keys")
        if set(self.resources) != set(ResourceType):
            raise ValueError("Player resources must define every ResourceType")
        if any(
            type(amount) is not int or amount < 0 for amount in self.resources.values()
        ):
            raise ValueError("Player resource amounts must be non-negative integers")

    def __str__(self):
        a = str("Index: " + str(self.index))
        b = str("Strategy: " + str(self.strategy))
        c = str("Hand: " + str(self.hand))
        d = str("City: " + str(self.city))
        e = str("Workers: " + str(self.workers))
        f = str("Season: " + str(self.season))
        g = str("Points: " + str(self.points))
        h = str("Resources: " + str(self.resources))
        i = str("Finished: " + str(self.finished))
        j = str("Events: " + str(self.events))

        return (
            a
            + "\n"
            + b
            + "\n"
            + c
            + "\n"
            + d
            + "\n"
            + e
            + "\n"
            + f
            + "\n"
            + g
            + "\n"
            + h
            + "\n"
            + i
            + "\n"
            + j
        )

    # Function to add cards to the player"s hand or city
    def _cards_in_zone(self, zone: CardZone) -> list[Card]:
        if not isinstance(zone, CardZone):
            raise TypeError("zone must be a CardZone")
        if zone == CardZone.HAND:
            return self.hand
        if zone == CardZone.CITY:
            return self.city
        raise ValueError(f"Unsupported player card zone: {zone}")

    def cards_add(self, listofcards: list[Card], handorcity: CardZone) -> list[Card]:
        target = self._cards_in_zone(handorcity)
        target.extend(listofcards)
        return target

    def _city_spaces_occupied_for_cards(self, cards: list[Card]) -> int:
        total = 0
        grouped_cards = defaultdict(list)

        for card in cards:
            cost = max(0, int(getattr(card, "city_space_cost", 1)))
            group = getattr(card, "city_space_group", None)

            if group is None:
                total += cost
            else:
                if not isinstance(group, list):
                    raise ValueError(
                        f"Card '{card.name}' has city_space_group with unsupported type {type(group).__name__}; expected list"
                    )

                members = tuple(sorted(str(name) for name in group))
                grouped_cards[members].append(card)

        for members, group_cards in grouped_cards.items():
            counts = [
                sum(1 for c in group_cards if c.name == member) for member in members
            ]
            total += max(counts) if len(counts) > 0 else 0

        return total

    def city_spaces_occupied(self) -> int:
        return self._city_spaces_occupied_for_cards(self.city)

    def card_fits_in_city(self, card: Card) -> bool:
        return self._city_spaces_occupied_for_cards(self.city + [card]) <= 15

    # Function to remove cards from the player"s hand or city
    def cards_remove(self, listofcards: list[Card], handorcity: CardZone) -> list[Card]:
        target = self._cards_in_zone(handorcity)
        for card in listofcards:
            target.remove(card)
        return target

    # Function to check the open spaces in hand or city
    def cards_get_open_spaces(self, handorcity: CardZone) -> int:
        target = self._cards_in_zone(handorcity)
        if handorcity == CardZone.HAND:
            return 8 - len(target)  # Max hand size is 8
        else:
            return 15 - self.city_spaces_occupied()  # Max city size is 15

    # Function to add workers
    def workers_add(self, amount: int) -> int:
        self.workers += amount
        return self.workers

    # Function to remove workers
    def workers_remove(self, amount: int) -> int:
        self.workers -= amount
        return self.workers

    # Function to add resources to a specific category
    def resources_add(
        self, resource: ResourceType, amount: int
    ) -> dict[ResourceType, int]:
        if not isinstance(resource, ResourceType):
            raise TypeError(f"Expected ResourceType, got {type(resource).__name__}")
        self.resources[resource] += amount
        return self.resources

    # Function to remove resources from a specific category
    def resources_remove(
        self, resource: ResourceType, amount: int
    ) -> dict[ResourceType, int]:
        if not isinstance(resource, ResourceType):
            raise TypeError(f"Expected ResourceType, got {type(resource).__name__}")
        self.resources[resource] -= amount
        return self.resources

    # Calculate the total remaining resources of the player
    def resources_total(self) -> int:
        return sum(self.resources.values())

    # Function to add points to a specific category
    def points_add(
        self, category: PointCategory, points: int
    ) -> dict[PointCategory, int]:
        if not isinstance(category, PointCategory):
            raise TypeError("category must be a PointCategory")
        self.points[category] += points
        return self.points

    # Function to remove points from a specific category
    def points_remove(
        self, category: PointCategory, points: int
    ) -> dict[PointCategory, int]:
        if not isinstance(category, PointCategory):
            raise TypeError("category must be a PointCategory")
        self.points[category] -= points
        return self.points

    # Calculate the total points of the player
    def points_total(self) -> int:
        return sum(self.points.values())

    # Function to make a decision based on the strategy and game state
    def decide(
        self, game_state: GameState, decision_kind: DecisionKind, options: Any
    ) -> Any:
        return self.strategy.decide(game_state, decision_kind, options)

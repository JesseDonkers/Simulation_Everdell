import unittest
from typing import Any, cast

from actions.resources import action_resource_general
from class_card import Card
from class_location import Location
from class_player import Player
from class_strategy import Strategy
from shared.game_types import (
    CardColor,
    CardZone,
    DecisionKind,
    LocationType,
    PointCategory,
    ResourceType,
    Season,
)


class DomainTypeTests(unittest.TestCase):
    def test_player_rejects_string_resource_keys(self):
        with self.assertRaises(TypeError):
            Player(
                resources=cast(
                    Any,
                    {"twig": 0, "resin": 0, "pebble": 0, "berry": 0},
                )
            )

    def test_player_rejects_string_zones(self):
        with self.assertRaises(TypeError):
            Player().cards_add([], cast(Any, "hand"))

    def test_player_rejects_string_seasons(self):
        with self.assertRaises(TypeError):
            Player(season=cast(Any, "winter"))

    def test_location_rejects_string_types(self):
        with self.assertRaises(TypeError):
            Location("Test Location", cast(Any, "basic"), 1, None)

    def test_player_rejects_string_point_categories(self):
        with self.assertRaises(TypeError):
            Player().points_add(cast(Any, "token"), 1)

    def test_card_rejects_string_resource_keys(self):
        with self.assertRaises(TypeError):
            Card(
                "Test Card",
                CardColor.PURPLE,
                cast(Any, {"twig": 0, "resin": 0, "pebble": 0, "berry": 0}),
                1,
                False,
                0,
            )

    def test_card_rejects_blank_names(self):
        with self.assertRaises(ValueError):
            Card(
                " ",
                CardColor.PURPLE,
                {resource: 0 for resource in ResourceType},
                1,
                False,
                0,
            )

    def test_card_rejects_string_color(self):
        with self.assertRaises(TypeError):
            Card(
                "Test Card",
                cast(Any, "purple"),
                {resource: 0 for resource in ResourceType},
                1,
                False,
                0,
            )

    def test_resource_action_rejects_string_resource_names(self):
        with self.assertRaises(TypeError):
            action_resource_general(cast(Any, "twig"), 1)

    def test_strategy_rejects_string_decision_kinds(self):
        with self.assertRaises(TypeError):
            Strategy().decide(None, cast(Any, "move"), [])

    def test_enum_resource_costs_are_preserved(self):
        card = Card(
            "Test Card",
            CardColor.PURPLE,
            {resource: 0 for resource in ResourceType},
            1,
            False,
            0,
        )
        self.assertEqual(card.costs[ResourceType.TWIG], 0)
        self.assertIs(card.color, CardColor.PURPLE)
        self.assertIs(Player().season, Season.WINTER)
        self.assertEqual(LocationType.BASIC.value, "basic")
        self.assertEqual(PointCategory.TOKEN.value, "token")
        self.assertEqual(Player().cards_get_open_spaces(CardZone.HAND), 8)
        self.assertEqual(DecisionKind.MOVE.value, "move")


if __name__ == "__main__":
    unittest.main()

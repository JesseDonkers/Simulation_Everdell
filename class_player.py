from collections import defaultdict
from typing import Any


class Player:
    def __init__(self):
        self.index = 0
        self.strategy: Any = None
        self.hand = []  # Initiate a hand without cards
        self.city = []  # Initiate an empty city without cards
        self.workers = 0  # Initiate the number of workers to zero
        self.season = "winter"  # A player starts in winter
        self.points = dict(card=0, token=0, prosperity=0, journey=0, event=0)
        self.resources = dict(twig=0, resin=0, pebble=0, berry=0)
        self.finished = False  # Track if the player has finished their game
        self.events = []  # Event locations claimed by this player

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
    def cards_add(self, listofcards, handorcity):
        target = self.hand if handorcity == "hand" else self.city
        target.extend(listofcards)
        return target

    def _city_spaces_occupied_for_cards(self, cards):
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

    def city_spaces_occupied(self):
        return self._city_spaces_occupied_for_cards(self.city)

    def card_fits_in_city(self, card):
        return self._city_spaces_occupied_for_cards(self.city + [card]) <= 15

    # Function to remove cards from the player"s hand or city
    def cards_remove(self, listofcards, handorcity):
        target = self.hand if handorcity == "hand" else self.city
        for card in listofcards:
            target.remove(card)
        return target

    # Function to check the open spaces in hand or city
    def cards_get_open_spaces(self, handorcity):
        target = self.hand if handorcity == "hand" else self.city
        if handorcity == "hand":
            return 8 - len(target)  # Max hand size is 8
        else:
            return 15 - self.city_spaces_occupied()  # Max city size is 15

    # Function to add workers
    def workers_add(self, amount):
        self.workers += amount
        return self.workers

    # Function to remove workers
    def workers_remove(self, amount):
        self.workers -= amount
        return self.workers

    # Function to add resources to a specific category
    def resources_add(self, resource, amount):
        self.resources[resource] += amount
        return self.resources

    # Function to remove resources from a specific category
    def resources_remove(self, resoure, amount):
        self.resources[resoure] -= amount
        return self.resources

    # Calculate the total remaining resources of the player
    def resources_total(self):
        return sum(self.resources.values())

    # Function to add points to a specific category
    def points_add(self, category, points):
        self.points[category] += points
        return self.points

    # Function to remove points from a specific category
    def points_remove(self, category, points):
        self.points[category] -= points
        return self.points

    # Calculate the total points of the player
    def points_total(self):
        return sum(self.points.values())

    # Function to make a decision based on the strategy and game state
    def decide(self, game_state: Any, decision_kind: str, options: Any) -> Any:
        return self.strategy.decide(game_state, decision_kind, options)

import random
from typing import Any

STRATEGY_TODO: list[str] = [
    "cards_to_take_hand: evaluate revealed card value and playability when choosing both the subset and its size; the random strategy samples uniformly.",
    "cards_to_store: use the possible cards as input when choosing how many cards to store; the random strategy samples uniformly.",
    "resources_to_location: use points_per_resource to prioritize the allocation; the random strategy currently samples without regard to point value.",
    "card_play_method: compare payment requirements, consumed cards, and card effects; the random strategy currently chooses a method category and option randomly.",
]

# ============================================
# BASE STRATEGY CLASS
# ============================================


class Strategy:
    def decide(self, game_state, decision_kind, parameters):
        handler_name = f"choose_{decision_kind}"
        handler = getattr(self, handler_name, None)

        if handler is None:
            raise ValueError(f"Unknown decision type: {decision_kind}")
        return handler(game_state, parameters)


# ============================================
# CLASS PER STRATEGY
# ============================================


class Strategy_random(Strategy):
    def choose_move(self, game_state, possible_moves):
        return random.choice(possible_moves)

    def choose_card_new(self, game_state, possible_cards):
        return random.choice(possible_cards)

    def choose_card_play_method(self, game_state, possible_methods):
        methods_by_type: dict[str, list[Any]] = {}
        for method in possible_methods:
            methods_by_type.setdefault(method.method, []).append(method)

        method_type = random.choice(list(methods_by_type))
        return random.choice(methods_by_type[method_type])

    def choose_card_hand_or_meadow(self, game_state, _):
        opt = ["hand", "meadow"]
        return random.choice(opt)

    def choose_card_deck_or_discardpile(self, game_state, _):
        opt = ["deck", "discardpile"]
        return random.choice(opt)

    def choose_nr_cards_discard_hand(self, game_state, max_nr):
        return random.randint(0, max_nr)

    def choose_cards_to_take_hand(self, game_state, parameters):
        possible_cards = parameters["cards"]
        max_count = parameters["max_count"]
        nr_to_take = random.randint(0, max_count)
        return random.sample(possible_cards, nr_to_take)

    def choose_cards_to_store(self, game_state, parameters):
        possible_cards = parameters["cards"]
        max_count = parameters["max_count"]
        nr_to_store = random.randint(1, max_count)
        return random.sample(possible_cards, nr_to_store)

    def choose_card_discard(self, game_state, possible_cards):
        return random.choice(possible_cards)

    def choose_card_reactivate_green(self, game_state, possible_cards):
        return random.choice(possible_cards)

    def choose_location_place_worker(self, game_state, possible_locations):
        return random.choice(possible_locations)

    def choose_location_activate_with_point_token(self, game_state, possible_locations):
        # Include a None option to model declining to spend the point token.
        return random.choice(possible_locations + [None])

    def choose_location_take_worker(self, game_state, possible_locations):
        return random.choice(possible_locations)

    def choose_resource_new(self, game_state, possible_resources):
        return random.choice(possible_resources)

    def choose_resource_discard(self, game_state, possible_resources):
        return random.choice(list(possible_resources))

    def choose_resource_give_away(self, game_state, parameters):
        nr_to_pick, available = parameters
        pool = [r for r, count in available.items() for _ in range(count)]
        return random.sample(pool, nr_to_pick)

    def choose_nr_resources_swap(self, game_state, max_nr_resources):
        return random.randint(0, max_nr_resources)

    def choose_nr_resources_for_points(self, game_state, max_nr_resources):
        return random.randint(0, max_nr_resources)

    def choose_resources_to_location(self, game_state, parameters):
        available = parameters["available"]
        max_count = min(parameters["max_nr_resources"], sum(available.values()))
        pool = [resource for resource, count in available.items() for _ in range(count)]
        chosen = random.sample(pool, random.randint(0, max_count))
        return {resource: chosen.count(resource) for resource in available}

    def choose_player_to_receive_resources(self, game_state, possible_players):
        return random.choice(possible_players)

    def choose_player_to_receive_cards_hand(self, game_state, possible_players):
        return random.choice(possible_players)

    def choose_player_to_receive_cards_city(self, game_state, possible_players):
        return random.choice(possible_players)

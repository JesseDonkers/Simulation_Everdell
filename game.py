import copy
import random
from typing import Any

from class_action import *
from class_card import init_cards
from class_deck import Deck
from class_discard_pile import DiscardPile
from class_location import init_locations, special_events
from class_meadow import Meadow
from class_player import Player
from class_strategy import *
from engine.selectors import get_possible_cards, get_possible_moves
from engine.turn import advance_current_player, finish_current_player
from functions_statistics import (
    init_simulation_results,
    record_game_result,
    simulation_results_to_text,
    summarize_simulation_results,
)
from functions_testing import clear_test_results, game_state_as_df_to_text

# ============================================
# VARIABLES & PARAMETERS
# ============================================

MODE = "scenario"  # "scenario" or "simulation"

NR_SIMULATION_RUNS = 100  # Number of times to run the scenario or simulation
NR_PLAYERS = 2  # Number of players in the game (2-4)
STRATEGY_PER_PLAYER = [Strategy_random, Strategy_random]
MAX_TURNS_PER_GAME = 10_000


# ============================================
# FUNCTIONS FOR SIMULATION AND SCENARIO RUNS
# ============================================


def create_game_state(nr_players, strategy_per_player):
    cards = copy.deepcopy(init_cards)
    deck = Deck()
    deck.add_to_deck(cards)
    deck.shuffle_deck()
    discardpile = DiscardPile()
    meadow = Meadow()
    meadow.add_to_meadow(8, deck, discardpile)

    players = [Player() for _ in range(nr_players)]
    card_counter = 5
    for i, player in enumerate(players):
        player.index = i
        drawn_cards = deck.draw_cards(card_counter, discardpile)
        player.cards_add(drawn_cards, "hand")
        card_counter += 1
        player.workers_add(2)

    locations: list[Any] = copy.deepcopy(init_locations)
    game_state: dict[str, Any] = {
        "deck": deck,
        "discardpile": discardpile,
        "meadow": meadow,
        "locations": locations,
        "players": players,
        "current_player": players[0],
    }

    # Shuffle special events and add 4 to locations.
    special_events_copy = copy.deepcopy(special_events)
    random.shuffle(special_events_copy)
    for i in range(4):
        game_state["locations"].append(special_events_copy[i])

    # TODO: forecast cards shuffle and place
    #  - Shuffle forest cards
    #  - Place 3 or 4 forest cards depending on nr players (add to locations)

    if len(strategy_per_player) != len(players):
        raise ValueError(
            f"Number of strategies ({len(strategy_per_player)})"
            f" does not match number of players ({len(players)})"
        )
    for i, player in enumerate(players):
        player.strategy = strategy_per_player[i]()

    return game_state


def _execute_move(game_state, move):
    if move == "play_card":
        action_play_card().execute(game_state)
    elif move == "place_worker":
        action_place_worker().execute(game_state)
    elif move == "advance_season":
        action_advance_season().execute(game_state)
    else:
        raise ValueError(f"Unknown move: {move}")


def run_single_turn(game_state):
    player = game_state["current_player"]

    # Branch 1: this player is already finished; skip to next player.
    if player.finished:
        pass

    # Branch 2: active player has no legal moves and therefore finishes.
    elif len(get_possible_moves(game_state)) == 0:
        finish_current_player(game_state)

    # Branch 3: active player takes one move; may finish if that was final.
    else:
        possible_moves = get_possible_moves(game_state)
        chosen_move = player.decide(game_state, "move", possible_moves)
        _execute_move(game_state, chosen_move)

        updated_moves = get_possible_moves(game_state)
        if len(updated_moves) == 0:
            finish_current_player(game_state)

    # Advance turn unless all players have already finished.
    if not all(p.finished for p in game_state["players"]):
        advance_current_player(game_state)


def run_full_game(game_state, max_turns=MAX_TURNS_PER_GAME):
    nr_turns = 0
    status_game_finished = all(player.finished for player in game_state["players"])

    while not status_game_finished:
        if nr_turns >= max_turns:
            raise RuntimeError("Maximum turns exceeded before game finished")

        run_single_turn(game_state)
        nr_turns += 1
        status_game_finished = all(player.finished for player in game_state["players"])

    return game_state


def run_scenario(game_state):
    player: "Player" = game_state["current_player"]

    class ScenarioStrategy(Strategy_random):
        def __init__(self):
            super().__init__()
            self.preferred_cards = ["Boerderij", "Houtsnijder"]

        def choose_card_new(self, game_state, possible_cards):
            for preferred in self.preferred_cards:
                for card in possible_cards:
                    if card.name == preferred:
                        return card
            return possible_cards[0]

        def choose_card_hand_or_meadow(self, game_state, _):
            return "hand"

        def choose_card_play_method(self, game_state, possible_methods):
            return possible_methods[0]

        def choose_resource_new(self, game_state, possible_resources):
            if "twig" in possible_resources:
                return "twig"
            return possible_resources[0]

    def find_card_in_zones(card_name):
        for card in player.hand + player.city:
            if card.name == card_name:
                return card
        for card in game_state["meadow"].cards:
            if card.name == card_name:
                return card
        for card in list(game_state["deck"].cards):
            if card.name == card_name:
                return card
        for card in game_state["discardpile"].cards:
            if card.name == card_name:
                return card
        raise ValueError(f"Card not found in any zone: {card_name}")

    def move_card_to_zone(card_name, zone):
        card = find_card_in_zones(card_name)
        if card in player.hand:
            player.cards_remove([card], "hand")
        elif card in player.city:
            player.cards_remove([card], "city")
        elif card in game_state["meadow"].cards:
            game_state["meadow"].cards.remove(card)
        elif card in game_state["deck"].cards:
            game_state["deck"].cards.remove(card)
        elif card in game_state["discardpile"].cards:
            game_state["discardpile"].cards.remove(card)
        else:
            raise ValueError(f"Unable to move card: {card_name}")

        if zone == "hand":
            player.cards_add([card], "hand")
        elif zone == "city":
            player.cards_add([card], "city")
        else:
            raise ValueError(f"Unknown destination zone: {zone}")

    # Build a deterministic test state for Gerechtsgebouw and Winkelier.
    player.hand.clear()
    player.city.clear()
    player.resources = {"twig": 2, "resin": 1, "pebble": 0, "berry": 2}
    player.workers = 2
    player.finished = False
    player.strategy = ScenarioStrategy()

    move_card_to_zone("Gerechtsgebouw", "city")
    move_card_to_zone("Winkelier", "city")
    move_card_to_zone("Boerderij", "hand")
    move_card_to_zone("Houtsnijder", "hand")

    game_state_as_df_to_text(game_state, "Game_state_start")

    # Play a construction to trigger Gerechtsgebouw
    action_play_card().execute(game_state)
    game_state_as_df_to_text(game_state, "Game_state_after_construction_play")

    # Play a critter to trigger Winkelier
    action_play_card().execute(game_state)
    game_state_as_df_to_text(game_state, "Game_state_after_critter_play")

    return True


def run_scenario_mode():
    clear_test_results()
    for _ in range(NR_SIMULATION_RUNS):
        game_state = create_game_state(NR_PLAYERS, STRATEGY_PER_PLAYER)
        if run_scenario(game_state):
            break


def run_simulation_mode():
    print("Running simulations...")
    clear_test_results()
    simulation_results = init_simulation_results(NR_PLAYERS)

    game_state = None

    # TODO: tqdm progress bar

    for _ in range(NR_SIMULATION_RUNS):
        game_state = create_game_state(NR_PLAYERS, STRATEGY_PER_PLAYER)
        run_full_game(game_state, max_turns=MAX_TURNS_PER_GAME)
        record_game_result(simulation_results, game_state["players"])

    if game_state is not None:
        game_state_as_df_to_text(game_state, "last_game_state.txt")

    simulation_summary = summarize_simulation_results(simulation_results)
    summary_output = simulation_results_to_text(
        simulation_summary,
        output_file="simulation_summary.txt",
    )
    simulation_summary["summary_text"] = summary_output["full_text"]
    simulation_summary["summary_file_path"] = summary_output["saved_file_path"]

    print("Simulations completed.")
    return simulation_summary


def main():
    if MODE == "scenario":
        run_scenario_mode()
        return
    if MODE == "simulation":
        run_simulation_mode()
        return
    raise ValueError(f"Unknown MODE: {MODE}")


if __name__ == "__main__":
    main()

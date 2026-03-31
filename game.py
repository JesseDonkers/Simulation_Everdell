import copy
import random

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

MODE = "simulation"  # "scenario" or "simulation"

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

    game_state = {
        "deck": deck,
        "discardpile": discardpile,
        "meadow": meadow,
        "locations": copy.deepcopy(init_locations),
        "players": players,
        "current_player": players[0],
    }

    # Shuffle special events and add 4 to locations.
    special_events_copy = copy.deepcopy(special_events)
    random.shuffle(special_events_copy)
    for i in range(4):
        game_state["locations"].append(special_events_copy[i])

    # To do: each special event can only be chosen once, is that modelled?

    # To do:
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

    if player.finished:
        if not all(p.finished for p in game_state["players"]):
            advance_current_player(game_state)
        return

    possible_moves = get_possible_moves(game_state)
    if len(possible_moves) == 0:
        finish_current_player(game_state)
        if not all(p.finished for p in game_state["players"]):
            advance_current_player(game_state)
        return

    chosen_move = player.decide(game_state, "move", possible_moves)
    _execute_move(game_state, chosen_move)

    updated_moves = get_possible_moves(game_state)
    if len(updated_moves) == 0:
        finish_current_player(game_state)

    if not all(p.finished for p in game_state["players"]):
        advance_current_player(game_state)


def run_full_game(game_state, max_turns=MAX_TURNS_PER_GAME):
    nr_turns = 0
    status_game_finished = all(
        player.finished for player in game_state["players"]
    )

    while not status_game_finished:
        if nr_turns >= max_turns:
            raise RuntimeError("Maximum turns exceeded before game finished")

        run_single_turn(game_state)
        nr_turns += 1
        status_game_finished = all(
            player.finished for player in game_state["players"]
        )

    return game_state


def run_scenario(game_state):
    player: "Player" = game_state["current_player"]

    player.resources_add("twig", 2)
    player.resources_add("resin", 1)
    player.resources_add("berry", 4)

    for _ in range(2):
        possible_cards = get_possible_cards(game_state, 99, True)
        if len(possible_cards) == 0:
            break
        action_play_card().execute(game_state)

    has_herberg = any(c.name == "Herberg" for c in player.city)
    has_zanger = any(c.name == "Zanger" for c in player.city)
    if has_herberg and has_zanger:
        print("Herberg and Zanger in city")

        game_state_as_df_to_text(game_state, "Game_state")

        action_place_worker().execute(game_state)

        heza_claimed = any(loc.name == "Heza" for loc in player.events)
        if heza_claimed:
            print("Worker placed on Heza")

            finish_current_player(game_state)
            game_state_as_df_to_text(game_state, "Game_state")
            
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


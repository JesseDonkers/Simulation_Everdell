import copy
import random
from concurrent.futures import ProcessPoolExecutor
from typing import Any

from tqdm import tqdm

from actions.cards import action_play_card
from actions.locations import action_place_worker
from actions.season import action_advance_season
from class_card import init_cards
from class_deck import Deck
from class_discard_pile import DiscardPile
from class_location import forest_locations, init_locations, special_events
from class_meadow import Meadow
from class_player import Player
from class_strategy import Strategy_random
from engine.selectors import (
    get_possible_cards,
    get_possible_moves,
    get_possible_moves_and_card_plays,
)
from engine.turn import advance_current_player, finish_current_player
from functions_statistics import (
    init_simulation_results,
    record_game_result,
    simulation_results_to_text,
    summarize_simulation_results,
)
from functions_testing import clear_test_results, game_state_as_df_to_text
from shared.game_state import GameState
from shared.game_types import CardZone, DecisionKind, GameMode, GameMove, ResourceType

# ============================================
# VARIABLES & PARAMETERS
# ============================================

MODE = GameMode.SIMULATION

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
        player.cards_add(drawn_cards, CardZone.HAND)
        card_counter += 1
        player.workers_add(2)

    locations: list[Any] = copy.deepcopy(init_locations)
    game_state = GameState(
        deck=deck,
        discardpile=discardpile,
        meadow=meadow,
        locations=locations,
        players=players,
        current_player=players[0],
    )

    # Shuffle special events and add 4 to locations.
    special_events_copy = copy.deepcopy(special_events)
    random.shuffle(special_events_copy)
    for i in range(4):
        game_state.locations.append(special_events_copy[i])

    # Shuffle forest locations and place 3 or 4 selected clearings.
    nr_forest_locations = 3 if nr_players <= 3 else 4
    forest_locations_copy = copy.deepcopy(forest_locations)
    random.shuffle(forest_locations_copy)
    selected_forest_locations = forest_locations_copy[:nr_forest_locations]

    if nr_players == 4:
        for location in selected_forest_locations:
            location.maxworkers = 2

    game_state.locations.extend(selected_forest_locations)

    # Provide each player with a strategy
    if len(strategy_per_player) != len(players):
        raise ValueError(
            f"Number of strategies ({len(strategy_per_player)})"
            f" does not match number of players ({len(players)})"
        )
    for i, player in enumerate(players):
        player.strategy = strategy_per_player[i]()

    return game_state


def _execute_move(game_state, move, precomputed_card_plays=None):
    if not isinstance(move, GameMove):
        raise TypeError("move must be a GameMove")
    if move == GameMove.PLAY_CARD:
        action_play_card(precomputed_card_plays=precomputed_card_plays).execute(
            game_state
        )
    elif move == GameMove.PLACE_WORKER:
        action_place_worker().execute(game_state)
    elif move == GameMove.ADVANCE_SEASON:
        action_advance_season().execute(game_state)
    else:
        raise ValueError(f"Unknown move: {move}")


def run_single_turn(game_state):
    player = game_state.current_player

    # Branch 1: this player is already finished; skip to next player.
    if not player.finished:
        possible_moves, possible_card_plays = get_possible_moves_and_card_plays(
            game_state, player
        )

        # Branch 2: active player has no legal moves and therefore finishes.
        if not possible_moves:
            finish_current_player(game_state)

        # Branch 3: active player takes one move; may finish if that was final.
        else:
            chosen_move = player.decide(game_state, DecisionKind.MOVE, possible_moves)
            _execute_move(game_state, chosen_move, possible_card_plays)

            updated_moves = get_possible_moves(game_state, player)
            if len(updated_moves) == 0:
                finish_current_player(game_state)

    # Advance turn unless all players have already finished.
    if not all(p.finished for p in game_state.players):
        advance_current_player(game_state)


def run_full_game(game_state, max_turns=MAX_TURNS_PER_GAME):
    nr_turns = 0
    status_game_finished = all(player.finished for player in game_state.players)

    while not status_game_finished:
        if nr_turns >= max_turns:
            raise RuntimeError("Maximum turns exceeded before game finished")

        run_single_turn(game_state)
        nr_turns += 1
        status_game_finished = all(player.finished for player in game_state.players)

    return game_state


def _simulate_one_game(game_spec):
    seed, include_state = game_spec
    random.seed(seed)
    game_state = create_game_state(NR_PLAYERS, STRATEGY_PER_PLAYER)
    run_full_game(game_state, max_turns=MAX_TURNS_PER_GAME)

    game_result = init_simulation_results(NR_PLAYERS)
    record_game_result(game_result, game_state.players)
    return (
        game_result["game_winners"][0],
        [player.points_total() for player in game_state.players],
        game_state if include_state else None,
    )


def run_scenario(game_state):
    player: "Player" = game_state.current_player

    class ScenarioStrategy(Strategy_random):
        def __init__(self):
            super().__init__()
            self.preferred_cards = []
            self.preferred_locations = ["Leun"]

        def choose_card_new(self, game_state, possible_cards):
            for preferred in self.preferred_cards:
                for card in possible_cards:
                    if card.name == preferred:
                        return card
            return super().choose_card_new(game_state, possible_cards)

        def choose_location_place_worker(self, game_state, possible_locs):
            for preferred in self.preferred_locations:
                for loc in possible_locs:
                    if loc.name == preferred:
                        return loc
            return super().choose_location_place_worker(game_state, possible_locs)

    def find_card_in_zones(card_name):
        for card in player.hand + player.city:
            if card.name == card_name:
                return card
        for card in game_state.meadow.cards:
            if card.name == card_name:
                return card
        for card in list(game_state.deck.cards):
            if card.name == card_name:
                return card
        for card in game_state.discardpile.cards:
            if card.name == card_name:
                return card
        raise ValueError(f"Card not found in any zone: {card_name}")

    def move_card_to_zone(card_name, zone):
        card = find_card_in_zones(card_name)
        if card in player.hand:
            player.cards_remove([card], CardZone.HAND)
        elif card in player.city:
            player.cards_remove([card], CardZone.CITY)
        elif card in game_state.meadow.cards:
            game_state.meadow.cards.remove(card)
        elif card in game_state.deck.cards:
            game_state.deck.cards.remove(card)
        elif card in game_state.discardpile.cards:
            game_state.discardpile.cards.remove(card)
        else:
            raise ValueError(f"Unable to move card: {card_name}")

        if zone == CardZone.HAND:
            player.cards_add([card], CardZone.HAND)
        elif zone == CardZone.CITY:
            player.cards_add([card], CardZone.CITY)
        else:
            raise ValueError(f"Unknown destination zone: {zone}")

    # Build a deterministic test state
    player.city.clear()
    player.resources = {
        ResourceType.TWIG: 0,
        ResourceType.RESIN: 0,
        ResourceType.PEBBLE: 0,
        ResourceType.BERRY: 0,
    }
    player.workers = 2
    player.finished = False
    player.strategy = ScenarioStrategy()

    move_card_to_zone("Ruines", CardZone.CITY)
    move_card_to_zone("Man", CardZone.CITY)
    move_card_to_zone("Vrouw", CardZone.CITY)
    move_card_to_zone("Kikkerkapitein", CardZone.CITY)
    move_card_to_zone("Leraar", CardZone.CITY)
    move_card_to_zone("Gerechtsgebouw", CardZone.CITY)
    move_card_to_zone("Boswachter", CardZone.CITY)
    move_card_to_zone("Universiteit", CardZone.CITY)

    game_state.meadow.add_to_meadow(50, game_state.deck, game_state.discardpile)

    game_state_as_df_to_text(game_state, "Game_state")

    action_place_worker().execute(game_state)
    finish_current_player(game_state)
    game_state_as_df_to_text(game_state, "Game_state")

    print("Scenario completed successfully.")
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

    seeds = [random.randrange(2**32) for _ in range(NR_SIMULATION_RUNS)]
    game_specs = [
        (seed, game_index == NR_SIMULATION_RUNS - 1)
        for game_index, seed in enumerate(seeds)
    ]
    game_state = None

    with ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(_simulate_one_game, game_specs)
        for winner, points, final_game_state in tqdm(
            results, total=NR_SIMULATION_RUNS, desc="Simulating", unit="game"
        ):
            simulation_results["game_winners"].append(winner)
            simulation_results["game_win_frequency"][winner] += 1
            for player_index, score in enumerate(points):
                simulation_results["game_points"][player_index].append(score)
            if final_game_state is not None:
                game_state = final_game_state

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
    if MODE == GameMode.SCENARIO:
        run_scenario_mode()
        return
    if MODE == GameMode.SIMULATION:
        run_simulation_mode()
        return
    raise ValueError(f"Unknown MODE: {MODE}")


if __name__ == "__main__":
    main()

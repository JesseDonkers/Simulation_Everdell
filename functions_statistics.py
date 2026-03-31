import os
from math import sqrt


def init_simulation_results(nr_players):
	return {
		"game_winners": [],
		"game_points": [[] for _ in range(nr_players)],
		"game_win_frequency": [0 for _ in range(nr_players)],
	}


def record_game_result(simulation_results, players):
	# Determine winner: most points, then most events, then most resources
	winner = max(
		players,
		key=lambda player: (
			player.points_total(),
			len(player.events),
			player.resources_total(),
		),
	)
	simulation_results["game_winners"].append(winner.index)
	simulation_results["game_win_frequency"][winner.index] += 1

	for player in players:
		simulation_results["game_points"][player.index].append(
			player.points_total()
		)

	return winner


def summarize_simulation_results(simulation_results):
	nr_runs = len(simulation_results["game_winners"])
	nr_players = len(simulation_results["game_win_frequency"])

	if nr_runs == 0:
		game_win_probabilities = [0.0 for _ in range(nr_players)]
		game_win_confidence_intervals = [(0.0, 0.0) for _ in range(nr_players)]
	else:
		game_win_probabilities = [
			win_count / nr_runs
			for win_count in simulation_results["game_win_frequency"]
		]
		game_win_confidence_intervals = []
		for player_index in range(nr_players):
			# Build a Bernoulli series: 1 if this player won that run, else 0
			win_indicators = [
				1 if winner_index == player_index else 0
				for winner_index in simulation_results["game_winners"]
			]

			# Sample variance of the win indicators
			mean_value = sum(win_indicators) / nr_runs
			sample_var = sum((v - mean_value) ** 2 for v in win_indicators) / (nr_runs - 1) if nr_runs > 1 else 0.0

			# 95% confidence interval, clamped to [0, 1]
			z_bar = game_win_probabilities[player_index]
			half_width = 1.96 * sqrt(sample_var / nr_runs)
			confidence_interval = (
				max(0.0, z_bar - half_width),
				min(1.0, z_bar + half_width),
			)
			game_win_confidence_intervals.append(confidence_interval)

	return {
		**simulation_results,
		"nr_runs": nr_runs,
		"game_win_probabilities": game_win_probabilities,
		"game_win_confidence_intervals": game_win_confidence_intervals,
	}


def simulation_results_to_text(simulation_results, output_file=None):
	lines = [
		f"NUMBER OF RUNS: {simulation_results['nr_runs']}",
		"",
		f"GAME WINNERS: {simulation_results['game_winners']}",
		f"GAME WIN FREQUENCY: {simulation_results['game_win_frequency']}",
		"",
		"PLAYER RESULTS:",
	]

	for player_index, points_history in enumerate(simulation_results["game_points"]):
		win_probability = simulation_results["game_win_probabilities"][player_index]
		ci_low, ci_high = simulation_results["game_win_confidence_intervals"][player_index]
		lines.append(f"Player {player_index}")
		lines.append(f"  Points per game: {points_history}")
		lines.append(f"  Wins: {simulation_results['game_win_frequency'][player_index]}")
		lines.append(f"  Win probability: {win_probability:.4f}")
		lines.append(
			f"  95% CI: ({ci_low:.4f}, {ci_high:.4f})"
		)

	full_text = "\n".join(lines)

	saved_file_path = None
	if output_file:
		test_results_folder = os.path.join(os.getcwd(), "test_results")
		os.makedirs(test_results_folder, exist_ok=True)
		saved_file_path = os.path.join(test_results_folder, output_file)
		with open(saved_file_path, "w") as file_handle:
			file_handle.write(full_text)

	return {
		"full_text": full_text,
		"saved_file_path": saved_file_path,
	}

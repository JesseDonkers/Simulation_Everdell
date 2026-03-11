from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from class_player import Player


def advance_current_player(game_state):
    players = game_state["players"]
    current_player = game_state["current_player"]
    current_player_index = players.index(current_player)

    nr_not_finished = len([p for p in players if p.finished is False])
    if nr_not_finished != 1:
        # Find the next player that has not finished
        new_player_index = (current_player_index + 1) % len(players)
        while players[new_player_index].finished:
            new_player_index = (new_player_index + 1) % len(players)

        game_state["current_player"] = players[new_player_index]


def finish_current_player(game_state):
    """
    Sets player.finished to True and evaluates all points.
    Returns list of points of all players if all players finished the game.
    """
    player: "Player" = game_state["current_player"]
    players = game_state["players"]
    player.finished = True

    # Card points
    for card in player.city:
        player.points_add("card", card.points)

        # Prosperity points
        if card.color == "purple":
            card.action_on_finish.execute(game_state)

    # Journey points
    # To do

    # Event points
    # To do

    # If all players have finished the game, compare sum of points
    if all(p.finished for p in players):
        points = [p.points_total() for p in players]
        return points

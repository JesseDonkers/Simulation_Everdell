from typing import TYPE_CHECKING

from actions.base import ActionContext

if TYPE_CHECKING:
    from class_player import Player

__all__ = ["advance_current_player", "finish_current_player"]


def advance_current_player(game_state):
    players = game_state["players"]
    current_player = game_state["current_player"]
    current_player_index = players.index(current_player)

    nr_not_finished = len([p for p in players if p.finished is False])
    if nr_not_finished == 0:
        return

    # Find the next player that has not finished
    new_player_index = (current_player_index + 1) % len(players)
    while players[new_player_index].finished:
        new_player_index = (new_player_index + 1) % len(players)

    game_state["current_player"] = players[new_player_index]


def finish_current_player(game_state):
    """
    Sets player.finished to True and evaluates all points.
    """
    player: "Player" = game_state["current_player"]
    players = game_state["players"]
    player.finished = True

    # Card points
    for card in player.city:
        player.points_add("card", card.points)

        # Prosperity points
        if card.color == "purple" and card.action_on_finish is not None:
            card.action_on_finish.execute(
                context=ActionContext(
                    player=player,
                    game_state=game_state,
                    host_card=card,
                )
            )

    # Vrouw scores 3 points per Man/Vrouw pair at game end.
    count_man = sum(1 for card in player.city if card.name == "Man")
    count_vrouw = sum(1 for card in player.city if card.name == "Vrouw")
    player.points_add("prosperity", 3 * min(count_man, count_vrouw))

    # Journey points
    for location in game_state["locations"]:
        if location.location_type == "journey":
            nr_workers = location.get_player_workers(player)
            for _ in range(nr_workers):
                player.points_add("journey", location.points)

    # Event points
    for event in player.events:
        if event.action_on_finish is not None:
            event.action_on_finish.execute(
                context=ActionContext(
                    player=player,
                    game_state=game_state,
                    event_location=event,
                )
            )

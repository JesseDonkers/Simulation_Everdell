from typing import TYPE_CHECKING

from actions.base import Action
from engine.selectors import get_possible_cards

__all__ = [
    "action_cards_from_deck_to_hand",
    "action_cards_from_meadow_to_hand",
    "action_give_discard_refill_hand",
    "action_play_card",
    "action_remove_card_from_city",    
    "action_play_cards_from_deck_or_discardpile",
    "action_refresh_meadow_draw_cards",
]

if TYPE_CHECKING:
    from class_deck import Deck
    from class_discard_pile import DiscardPile
    from class_meadow import Meadow
    from class_player import Player


class action_cards_from_deck_to_hand(Action):
    def __init__(self, nrCards):
        self.nrCards = nrCards

    def execute_action(self, player: "Player", game_state=None):
        deck: "Deck" = game_state["deck"]
        discardpile: "DiscardPile" = game_state["discardpile"]
        spaces_hand = player.cards_get_open_spaces("hand")
        nr_draw = min(self.nrCards, spaces_hand)
        listofcards = deck.draw_cards(nr_draw, discardpile)
        player.cards_add(listofcards, "hand")


class action_cards_from_meadow_to_hand(Action):
    def __init__(self, nrCards):
        self.nrCards = nrCards

    def execute_action(self, player: "Player", game_state=None):
        meadow: "Meadow" = game_state["meadow"]
        deck = game_state["deck"]
        discardpile = game_state["discardpile"]
        spaces_hand = player.cards_get_open_spaces("hand")
        listofcards = []
        selectable_cards = meadow.cards.copy()

        for _ in range(min(self.nrCards, spaces_hand)):
            card = player.decide(game_state, "card_new", selectable_cards)
            listofcards.append(card)
            selectable_cards.remove(card)

        meadow.draw_cards(listofcards, deck, discardpile)
        player.cards_add(listofcards, "hand")


class action_play_card(Action):
    def __init__(self, max_points=99, pay=True):
        self.max_points = max_points
        self.pay = pay

    def execute_action(self, player: "Player", game_state=None):
        meadow: "Meadow" = game_state["meadow"]
        deck = game_state["deck"]
        discardpile = game_state["discardpile"]
        possible_cards = get_possible_cards(game_state, self.max_points, self.pay)

        if len(possible_cards) == 0:
            raise ValueError("No possible cards to play")

        card = player.decide(game_state, "card_new", possible_cards)
        in_hand = card in player.hand
        in_meadow = card in meadow.cards

        loc = (
            player.decide(game_state, "card_hand_or_meadow", None)
            if in_hand and in_meadow
            else "hand" if in_hand else "meadow"
        )

        if loc == "hand":
            player.cards_remove([card], "hand")
        else:
            meadow.draw_cards([card], deck, discardpile)

        # To do: card can be played if a related card is played,
        #           no costs have to be paid, but
        #           the relatedoccupied should be set to True
        # To do: card can be played by discarding a card in the city,
        #           no or less costs have to paid

        # The player pays for the costs of the card if self.pay == True
        if self.pay:
            card_costs = card.requirements
            for resource, amount in card_costs.items():
                player.resources_remove(resource, amount)

        # Card is added to the player's city and action_on_play is executed
        player.cards_add([card], "city")
        if card.action_on_play:
            card.action_on_play.execute(game_state)


class action_remove_card_from_city(Action):
    def __init__(self, card_name):
        self.card_name = card_name

    def execute_action(self, player: "Player", game_state=None):
        card = next(c for c in player.city if c.name == self.card_name)
        player.cards_remove([card], "city")
        discard_pile: "DiscardPile" = game_state["discardpile"]
        discard_pile.add_to_discardpile([card])


class action_refresh_meadow_draw_cards(Action):
    def __init__(self, nr_refresh):
        self.nr_refresh = nr_refresh

    def execute_action(self, player: "Player", game_state=None):
        meadow: "Meadow" = game_state["meadow"]
        deck = game_state["deck"]
        discardpile: "DiscardPile" = game_state["discardpile"]
        listofcards = []
        selectable_cards = meadow.cards.copy()

        for _ in range(self.nr_refresh):
            card = player.decide(game_state, "card_discard", selectable_cards)
            listofcards.append(card)
            selectable_cards.remove(card)

        meadow.draw_cards(listofcards, deck, discardpile)
        discardpile.add_to_discardpile(listofcards)

        # Player chooses a card from the meadow to take on hand
        card = player.decide(game_state, "card_new", meadow.cards)
        meadow.draw_cards([card], deck, discardpile)
        player.cards_add([card], "hand")


class action_play_cards_from_deck_or_discardpile(Action):
    def __init__(self, nr_see):
        self.nr_see = nr_see

    def execute_action(self, player: "Player", game_state=None):
        deck: "Deck" = game_state["deck"]
        discardpile: "DiscardPile" = game_state["discardpile"]
        deck_or_discardpile = player.decide(game_state, "card_deck_or_discardpile", None)

        # Obtain possible cards
        # If there are no cards in the discardpile, it will automatically
        # take cards from the deck
        if deck_or_discardpile == "deck" or len(discardpile.cards) == 0:
            possible_cards = deck.draw_cards(self.nr_see, discardpile)
        else:
            nr_draw = min(self.nr_see, len(discardpile.cards))
            possible_cards = discardpile.draw_cards(nr_draw)

        # Place the card in the player's city for free
        card = player.decide(game_state, "card_new", possible_cards)
        player.cards_add([card], "city")

        # Add the other opened cards to the discardpile
        possible_cards.remove(card)
        discardpile.add_to_discardpile(possible_cards)


class action_give_discard_refill_hand(Action):
    def __init__(self, nr_give):
        self.nr_give = nr_give

    def execute_action(self, player: "Player", game_state=None):
        deck: "Deck" = game_state["deck"]
        discardpile: "DiscardPile" = game_state["discardpile"]

        # Give cards to another player, trying nr_give down to 1
        players = game_state["players"]
        nr_to_give = 0
        for nr in range(self.nr_give, 0, -1):
            can_receive = any(
                p != player
                and not p.finished
                and p.cards_get_open_spaces("hand") >= nr
                for p in players
            )
            if len(player.hand) >= nr and can_receive:
                nr_to_give = nr
                break

        if nr_to_give > 0:
            cards_to_give = []
            selectable = player.hand.copy()
            for _ in range(nr_to_give):
                card = player.decide(game_state, "card_discard", selectable)
                cards_to_give.append(card)
                selectable.remove(card)

            target = player.decide(game_state, "player_to_receive_cards", nr_to_give)
            player.cards_remove(cards_to_give, "hand")
            target.cards_add(cards_to_give, "hand")

        # Discard a number of cards by choice from hand
        nr_discard = player.decide(game_state, "nr_cards_discard_hand", None)
        cards_to_discard = []
        selectable = player.hand.copy()
        for _ in range(nr_discard):
            card = player.decide(game_state, "card_discard", selectable)
            cards_to_discard.append(card)
            selectable.remove(card)

        player.cards_remove(cards_to_discard, "hand")
        discardpile.add_to_discardpile(cards_to_discard)

        # Refill hand to the limit
        spaces = player.cards_get_open_spaces("hand")
        if spaces > 0:
            new_cards = deck.draw_cards(spaces, discardpile)
            player.cards_add(new_cards, "hand")

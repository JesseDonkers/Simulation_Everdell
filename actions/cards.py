from typing import TYPE_CHECKING

from actions.base import Action, ActionContext
from actions.common import resolve_city_card_target

__all__ = [
    "action_discard_cards_from_hand",
    "action_discard_stored_cards",
    "action_cards_from_deck_to_hand",
    "action_cards_from_meadow_to_hand",
    "action_draw_on_card_type",
    "action_cards_keep_and_give",
    "action_resource_on_card_type",
    "action_give_discard_refill_hand",
    "action_play_card",
    "action_play_meadow_card_with_discount",
    "action_remove_card_from_city",
    "action_play_revealed_deck_card_for_free",
    "action_play_cards_from_deck_or_discardpile",
    "action_refresh_meadow_draw_cards",
    "action_reactivate_green_card",
]

if TYPE_CHECKING:
    from class_deck import Deck
    from class_discard_pile import DiscardPile
    from class_meadow import Meadow
    from class_player import Player


class action_discard_cards_from_hand(Action):
    def __init__(self, nr_cards):
        self.nr_cards: int = nr_cards

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        discardpile: "DiscardPile" = game_state["discardpile"]

        if len(player.hand) < self.nr_cards:
            raise ValueError("Not enough cards in hand to discard")

        cards_to_discard = []
        selectable = player.hand.copy()
        for _ in range(self.nr_cards):
            card = player.decide(game_state, "card_discard", selectable)
            cards_to_discard.append(card)
            selectable.remove(card)

        player.cards_remove(cards_to_discard, "hand")
        discardpile.add_to_discardpile(cards_to_discard)


class action_discard_stored_cards(Action):
    """
    Handles discarding all stored cards from a specified card in the
    player's city by moving them to the discard pile and clearing card storage.
    """

    def __init__(self, card_name=None, card_id=None):
        self.card_name = card_name
        self.card_id = card_id

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        context_card_id = getattr(context.host_card, "card_id", None)
        effective_card_id = self.card_id if context_card_id is None else context_card_id
        target_card = resolve_city_card_target(
            player,
            self,
            card=context.host_card,
            card_id=effective_card_id,
            card_name=self.card_name,
        )
        stored_cards = target_card.card_storage["cards"]
        if len(stored_cards) == 0:
            return

        discard_pile: "DiscardPile" = game_state["discardpile"]
        discard_pile.add_to_discardpile(list(stored_cards))
        stored_cards.clear()


class action_cards_from_deck_to_hand(Action):
    def __init__(self, nrCards):
        self.nrCards = nrCards

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        deck: "Deck" = game_state["deck"]
        discardpile: "DiscardPile" = game_state["discardpile"]
        spaces_hand = player.cards_get_open_spaces("hand")
        nr_draw = min(self.nrCards, spaces_hand)
        listofcards = deck.draw_cards(nr_draw, discardpile)
        player.cards_add(listofcards, "hand")


class action_draw_on_card_type(Action):
    """Draw cards when a specified kind of card is played elsewhere.

    trigger_kinds: iterable containing any of "critter" and "construction".
    """

    def __init__(self, nrCards, trigger_kinds=("critter", "construction")):
        self.nrCards = nrCards
        self.trigger_kinds = tuple(trigger_kinds)

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        played_card = context.played_card
        if played_card is None:
            raise ValueError(
                "action_draw_on_card_type requires a 'played_card' argument when executed"
            )
        # Import here to avoid circular imports at module load time
        from class_card import Critter, Construction

        should_trigger = False
        if "critter" in self.trigger_kinds and isinstance(played_card, Critter):
            should_trigger = True
        if "construction" in self.trigger_kinds and isinstance(
            played_card, Construction
        ):
            should_trigger = True
        if not should_trigger:
            return

        # Reuse existing draw action
        action_cards_from_deck_to_hand(self.nrCards).execute(context=context)


class action_cards_keep_and_give(Action):
    def __init__(self, nrCards_keep, nrCards_give):
        self.nrCards_keep = nrCards_keep
        self.nrCards_give = nrCards_give

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        deck: "Deck" = game_state["deck"]
        discardpile: "DiscardPile" = game_state["discardpile"]
        players = game_state["players"]

        if self.nrCards_keep < 0 or self.nrCards_give < 0:
            raise ValueError("Card amounts to keep/give cannot be negative")

        eligible_targets = [
            p
            for p in players
            if p != player
            and not p.finished
            and p.cards_get_open_spaces("hand") >= self.nrCards_give
        ]

        if self.nrCards_give > 0 and len(eligible_targets) > 0:
            other_player: "Player" = player.decide(
                game_state, "player_to_receive_cards_hand", eligible_targets
            )

        spaces_hand = player.cards_get_open_spaces("hand")
        spaces_hand_other_player = (
            other_player.cards_get_open_spaces("hand") if other_player else 0
        )
        max_keep_possible = min(self.nrCards_keep, spaces_hand)
        max_give_possible = min(self.nrCards_give, spaces_hand_other_player)

        nr_draw = min(
            self.nrCards_keep + self.nrCards_give,
            max_keep_possible + max_give_possible,
        )
        if nr_draw == 0:
            return

        listofcards = deck.draw_cards(nr_draw, discardpile)
        cards_to_keep = []
        cards_to_give = []

        nr_keep = min(max_keep_possible, nr_draw)
        for _ in range(nr_keep):
            card_keep = player.decide(game_state, "card_new", listofcards)
            cards_to_keep.append(card_keep)
            listofcards.remove(card_keep)

        nr_give = min(max_give_possible, nr_draw - nr_keep)
        for _ in range(nr_give):
            card_give = player.decide(game_state, "card_discard", listofcards)
            cards_to_give.append(card_give)
            listofcards.remove(card_give)

        if len(cards_to_keep) > 0:
            player.cards_add(cards_to_keep, "hand")
        if len(cards_to_give) > 0:
            other_player.cards_add(cards_to_give, "hand")


class action_resource_on_card_type(Action):
    """Gain resources when a specified kind of card is played elsewhere.

    `resource` may be a single resource string or a list/tuple of resources
    to choose from when the trigger happens.
    """

    def __init__(self, resource, amount, trigger_kind="critter"):
        self.resource = resource
        self.amount = amount
        self.trigger_kind = trigger_kind

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        played_card = context.played_card
        if played_card is None:
            raise ValueError(
                "action_resource_on_card_type requires a 'played_card' argument when executed"
            )
        from class_card import Critter, Construction

        trigger_matches = False
        if self.trigger_kind == "critter" and isinstance(played_card, Critter):
            trigger_matches = True
        elif self.trigger_kind == "construction" and isinstance(
            played_card, Construction
        ):
            trigger_matches = True

        if not trigger_matches:
            return

        self._grant_resources(context)

    def _grant_resources(self, context: ActionContext):
        player: "Player" = context.player
        if isinstance(self.resource, (list, tuple)):
            from actions.resources import action_resources_by_choice

            action_resources_by_choice(self.resource, self.amount).execute(
                context=context
            )
        else:
            player.resources_add(self.resource, self.amount)


class action_cards_from_meadow_to_hand(Action):
    def __init__(self, nrCards):
        self.nrCards = nrCards

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
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
    def __init__(
        self,
        max_points=99,
        pay=True,
        allow_city_discard_then_pay=False,
    ):
        self.max_points = max_points
        self.pay = pay
        self.allow_city_discard_then_pay = allow_city_discard_then_pay

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        candidate_cards = context.options.get("candidate_cards")
        from engine.selectors import get_possible_card_plays

        meadow: "Meadow" = game_state["meadow"]
        deck = game_state["deck"]
        discardpile = game_state["discardpile"]
        possible_card_plays = get_possible_card_plays(
            game_state,
            self.max_points,
            self.pay,
            allow_city_discard_then_pay=self.allow_city_discard_then_pay,
        )
        if candidate_cards is not None:
            allowed = set(candidate_cards)
            possible_card_plays = [
                entry for entry in possible_card_plays if entry.card in allowed
            ]
        possible_cards = [entry.card for entry in possible_card_plays]

        if len(possible_cards) == 0:
            raise ValueError("No possible cards to play")

        card = player.decide(game_state, "card_new", possible_cards)
        card_play_data = next(
            entry for entry in possible_card_plays if entry.card == card
        )
        methods = card_play_data.methods

        selected_method = methods[0]
        if len(methods) > 1:
            selected_method = player.decide(game_state, "card_play_method", methods)

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

        target_player = self._get_target_player(player, game_state, card)
        existing_city_cards = list(player.city)

        pay_required = self._execute_selected_method(
            player,
            game_state,
            selected_method,
        )

        # Pay the cost defined by the chosen play method.
        if pay_required:
            card_costs = selected_method.pay_requirements
            if card_costs is None:
                raise ValueError("Selected paid play method has no pay_requirements")
            for resource, amount in card_costs.items():
                player.resources_remove(resource, amount)

        # Card is added to the target city and action_on_play is executed
        target_player.cards_add([card], "city")
        if card.action_on_play:
            card.action_on_play.execute(
                context=ActionContext(
                    player=target_player,
                    game_state=game_state,
                    host_card=card,
                )
            )

        # Trigger reactive effects on other cards in the player's city
        if target_player is player:
            for city_card in existing_city_cards:
                if getattr(city_card, "action_when_card_played", None):
                    city_card.action_when_card_played.execute(
                        context=ActionContext(
                            player=player,
                            game_state=game_state,
                            played_card=card,
                        )
                    )

    def _execute_selected_method(self, player: "Player", game_state, selected_method):
        if selected_method.method == "pay_resources":
            return self._method_pay_resources()
        if selected_method.method == "related_free":
            return self._method_related_free(selected_method)
        if selected_method.method == "city_discard_then_pay":
            return self._method_city_discard_then_pay(
                player, game_state, selected_method
            )
        if selected_method.method == "kerker_discount":
            return self._method_kerker_discount(player, game_state, selected_method)
        if selected_method.method == "free_no_pay":
            return self._method_free_no_pay()

        raise ValueError(f"Unknown card play method: {selected_method.method}")

    def _get_target_player(self, player: "Player", game_state, card):
        if card.name != "Dwaas":
            return player

        eligible_targets = [
            p
            for p in game_state["players"]
            if p != player and not p.finished and p.cards_get_open_spaces("city") > 0
        ]
        if len(eligible_targets) == 0:
            raise ValueError("No opponent has city space for Dwaas")

        return player.decide(
            game_state, "player_to_receive_cards_city", eligible_targets
        )

    def _method_pay_resources(self):
        return True

    def _method_related_free(self, selected_method):
        construction = selected_method.source_card
        if construction is None:
            raise ValueError("related_free method requires a source_card")
        construction.relatedoccupied = True
        return False

    def _method_city_discard_then_pay(
        self, player: "Player", game_state, selected_method
    ):
        if len(selected_method.consumed_cards) == 0:
            raise ValueError("city_discard_then_pay requires one consumed city card")
        discard_card = selected_method.consumed_cards[0]
        for resource, amount in discard_card.costs.items():
            player.resources_add(resource, amount)
        if discard_card.action_on_discard:
            discard_card.action_on_discard.execute(
                context=ActionContext(
                    player=player,
                    game_state=game_state,
                    host_card=discard_card,
                    options={"add_to_discard": False},
                )
            )
        return True

    def _method_kerker_discount(self, player: "Player", game_state, selected_method):
        if selected_method.source_card is None:
            raise ValueError("kerker_discount requires a source_card")
        if len(selected_method.consumed_cards) != 1:
            raise ValueError("kerker_discount requires one prisoner card")

        kerker = selected_method.source_card
        prisoner = selected_method.consumed_cards[0]

        # Imprisonment triggers discard side effects, but never sends
        # the card to discard pile.
        if prisoner.action_on_discard:
            prisoner.action_on_discard.execute(
                context=ActionContext(
                    player=player,
                    game_state=game_state,
                    host_card=prisoner,
                    options={"add_to_discard": False},
                )
            )
        elif prisoner in player.city:
            player.cards_remove([prisoner], "city")

        kerker.card_storage["cards"].append(prisoner)
        return True

    def _method_free_no_pay(self):
        return False


class action_play_meadow_card_with_discount(action_play_card):
    """
    Play a Critter or Construction from the Meadow for `discount` fewer
    resources of the player's choice (Herberg destination card effect).

    - Source is always the meadow; hand cards are excluded.
    - Kerker-discount cannot be combined with this effect.
    - Other compatible play methods (related_free, etc.) are preserved.
    """

    def __init__(self, discount=3):
        super().__init__()
        self.discount = discount

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        from engine.selectors import get_possible_meadow_card_plays_with_discount

        meadow: "Meadow" = game_state["meadow"]
        deck = game_state["deck"]
        discardpile = game_state["discardpile"]

        possible_card_plays = get_possible_meadow_card_plays_with_discount(
            game_state, self.discount
        )
        possible_cards = [entry.card for entry in possible_card_plays]

        if len(possible_cards) == 0:
            raise ValueError("No meadow cards can be played with the Herberg discount")

        card = player.decide(game_state, "card_new", possible_cards)
        card_play_data = next(
            entry for entry in possible_card_plays if entry.card == card
        )
        methods = card_play_data.methods

        selected_method = methods[0]
        if len(methods) > 1:
            selected_method = player.decide(game_state, "card_play_method", methods)

        # Always remove from meadow; Herberg only plays meadow cards
        meadow.draw_cards([card], deck, discardpile)
        existing_city_cards = list(player.city)

        pay_required = self._execute_selected_method(
            player, game_state, selected_method
        )

        if pay_required:
            card_costs = selected_method.pay_requirements
            if card_costs is None:
                raise ValueError("Selected paid play method has no pay_requirements")
            for resource, amount in card_costs.items():
                player.resources_remove(resource, amount)

        player.cards_add([card], "city")
        if card.action_on_play:
            card.action_on_play.execute(
                context=ActionContext(
                    player=player,
                    game_state=game_state,
                    host_card=card,
                )
            )

        # Trigger reactive effects on other cards in the player's city
        for city_card in existing_city_cards:
            if getattr(city_card, "action_when_card_played", None):
                city_card.action_when_card_played.execute(
                    context=ActionContext(
                        player=player,
                        game_state=game_state,
                        played_card=card,
                    )
                )


class action_remove_card_from_city(Action):
    def __init__(self, card_name=None, add_to_discard=True, card_id=None):
        self.card_name = card_name
        self.add_to_discard = add_to_discard
        self.card_id = card_id

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        context_card_id = getattr(context.host_card, "card_id", None)
        effective_card_id = self.card_id if context_card_id is None else context_card_id
        target_card = resolve_city_card_target(
            player,
            self,
            card=context.host_card,
            card_id=effective_card_id,
            card_name=self.card_name,
        )
        player.cards_remove([target_card], "city")

        add_to_discard = context.options.get("add_to_discard")
        effective_add_to_discard = (
            self.add_to_discard if add_to_discard is None else add_to_discard
        )
        if effective_add_to_discard:
            discard_pile: "DiscardPile" = game_state["discardpile"]
            discard_pile.add_to_discardpile([target_card])


class action_refresh_meadow_draw_cards(Action):
    def __init__(self, nr_refresh):
        self.nr_refresh = nr_refresh

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
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


class action_play_revealed_deck_card_for_free(Action):
    """Reveal cards from deck, play one up to max points for free, discard the rest."""

    def __init__(self, nr_see, max_points):
        self.nr_see = nr_see
        self.max_points = max_points

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        from engine.selectors import get_possible_card_plays

        deck: "Deck" = game_state["deck"]
        discardpile: "DiscardPile" = game_state["discardpile"]

        revealed_cards = deck.draw_cards(self.nr_see, discardpile)

        # Temporarily add revealed cards to hand so normal play checks can be reused.
        player.cards_add(revealed_cards, "hand")
        helper = action_play_card(self.max_points, False)

        possible_card_plays = get_possible_card_plays(
            game_state,
            self.max_points,
            False,
            allow_city_discard_then_pay=False,
        )
        playable_revealed_cards = [
            entry.card for entry in possible_card_plays if entry.card in revealed_cards
        ]

        if len(playable_revealed_cards) > 0:
            helper.execute(
                context=ActionContext(
                    player=player,
                    game_state=game_state,
                    options={"candidate_cards": playable_revealed_cards},
                )
            )

        # Discard all remaining revealed cards that were not played.
        leftovers = [card for card in revealed_cards if card in player.hand]
        if len(leftovers) > 0:
            player.cards_remove(leftovers, "hand")
            discardpile.add_to_discardpile(leftovers)


class action_play_cards_from_deck_or_discardpile(Action):
    def __init__(self, nr_see):
        self.nr_see = nr_see

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        deck: "Deck" = game_state["deck"]
        discardpile: "DiscardPile" = game_state["discardpile"]
        deck_or_discardpile = player.decide(
            game_state, "card_deck_or_discardpile", None
        )

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

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        deck: "Deck" = game_state["deck"]
        discardpile: "DiscardPile" = game_state["discardpile"]

        # Give exactly nr_give cards to another eligible player.
        players = game_state["players"]
        nr_to_give = self.nr_give
        eligible_targets = [
            p
            for p in players
            if p != player
            and not p.finished
            and p.cards_get_open_spaces("hand") >= nr_to_give
        ]

        if len(player.hand) < nr_to_give:
            raise ValueError("Not enough cards in hand to give away")
        if len(eligible_targets) == 0:
            raise ValueError("No eligible player can receive cards")

        cards_to_give = []
        selectable = player.hand.copy()
        for _ in range(nr_to_give):
            card = player.decide(game_state, "card_discard", selectable)
            cards_to_give.append(card)
            selectable.remove(card)

        target = player.decide(
            game_state, "player_to_receive_cards_hand", eligible_targets
        )

        player.cards_remove(cards_to_give, "hand")
        target.cards_add(cards_to_give, "hand")

        # Discard a number of cards by choice from hand
        nr_discard = player.decide(
            game_state, "nr_cards_discard_hand", len(player.hand)
        )
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


class action_reactivate_green_card(Action):
    """
    Reactivate a green card by executing its action_on_reactivate.

    Args:
        from_own_city (bool): If True, choose from player's own city.
                             If False, choose from other players' cities.
    """

    def __init__(self, from_own_city=True):
        self.from_own_city = from_own_city

    def execute_action(self, context: ActionContext):
        player: "Player" = context.player
        game_state = context.game_state
        if self.from_own_city:
            # Reactivate a green card from own city
            green_cards = [card for card in player.city if card.color == "green"]
        else:
            # Reactivate a green card from other players' cities
            green_cards = []
            for other_player in game_state["players"]:
                if other_player != player:
                    green_cards.extend(
                        [card for card in other_player.city if card.color == "green"]
                    )

        # Exclude cards whose action_on_reactivate is
        # action_reactivate_green_card only if it would cause recursion
        # (i.e., if there are no other green cards with different actions)
        non_recursive_cards = [
            card
            for card in green_cards
            if not isinstance(card.action_on_reactivate, action_reactivate_green_card)
        ]
        if len(non_recursive_cards) == 0:
            # All green cards would cause recursion,
            # so exclude them all to prevent infinite loop
            green_cards = []
        # Else, allow all

        if len(green_cards) > 0:
            card = player.decide(game_state, "card_reactivate_green", green_cards)
            if not card.action_on_reactivate:
                raise ValueError(f"{card.name} has no action_on_reactivate")
            card.action_on_reactivate.execute(
                context=ActionContext(
                    player=player,
                    game_state=game_state,
                    host_card=card,
                )
            )

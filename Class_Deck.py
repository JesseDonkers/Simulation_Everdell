from numpy import random
from collections import deque


class Deck:
    def __init__(self):
        self.cards = deque([])
        
    def __str__(self):
        return str(self.cards)
    
    # Function to add cards to the deck
    def add_to_deck(self, listofcards):
        self.cards.extend(listofcards)
        return self.cards

    # Deck can be shuffled at the start of a game
    def shuffle_deck(self):
        random.shuffle(self.cards)
        return self.cards

    # A player can draw one or multiple cards from the deck
    def draw_cards(self, nrCards, discardpile):
        if nrCards > len(self.cards): # If a player wants to draw more cards than the pile size
            random.shuffle(discardpile) # the discardpile is shuffled
            self.cards.extend(discardpile) # and added to the deck
            discardpile.clearDiscardPile() # The discard pile is cleared

        listofcards = []
        for _ in range(nrCards):
            card = self.cards[0] # Obtain first card
            self.cards.popleft() # Delete first card from the deck
            listofcards.append(card)
        return listofcards

from numpy import random
from collections import deque

class Deck:
    def __init__(self):
        self.deck = deque([])
        
    def __str__(self):
        return str(self.deck)
    
    # Function to add cards to the deck
    def add_to_deck(self, listofcards):
        self.deck.extend(listofcards)
        return self.deck

    # Deck can be shuffled at the start of a game
    def shuffle_deck(self):
        random.shuffle(self.deck)
        return self.deck

    # A player can draw one or multiple cards from the deck
    def draw_cards(self, nrCards, discardpile):
        if nrCards > len(self.deck): # If a player wants to draw more cards than the pile size
            random.shuffle(discardpile) # the discardpile is shuffled
            self.deck.extend(discardpile) # and added to the deck
            discardpile.clearDiscardPile() # The discard pile is cleared

        listofcards = []
        for _ in range(nrCards):
            card = self.deck[0] # Obtain first card
            self.deck.popleft() # Delete first card from the deck
            listofcards.append(card)
        return listofcards

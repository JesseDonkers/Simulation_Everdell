from numpy import random
from collections import deque

class DiscardPile:
    def __init__(self):
        self.discardpile = deque([])
        
    def __str__(self):
        return str(self.discardpile)
    
    # A player can add one more cards to the discard pile
    def add_to_discardpile(self, listofcards):
        self.discardpile.extend(listofcards)
        return self.discardpile
    
    # Function to obtain one ore more cards that were placed most recently
    def draw_cards(self, nrCards):
        cards = []
        for _ in range(nrCards):
            card = self.discardpile[-1]
            self.discardpile.pop()
            cards.append(card)
        return cards
    
    # When the deck is empty and the discard pile is reshuffled and added to the deck,
    # it should be possible to clear the discard pile
    def clear_discardpile(self):
        self.discardpile.clear()
        return self.discardpile

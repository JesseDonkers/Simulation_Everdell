from numpy import append, delete, random
from collections import deque

class Deck:
    def __init__(self):
        self.deck = deque(["Architect", "Bard", "Barge Toad", "Chip Sweep"])
        
    def __str__(self):
        return str(self.deck)
    
    # Deck can be shuffled at the start of a game
    def shuffleDeck(self):
        random.shuffle(self.deck)
        return self.deck

    # A player can draw one or multiple cards from the deck
    def drawCards(self, nrCards, discardpile):
        if nrCards > len(self.deck): # If a player wants to draw more cards than the pile size
            random.shuffle(discardpile) # the discardpile is shuffled
            self.deck.extend(discardpile) # and added to the deck

        cards = []
        for i in range(nrCards):
            card = self.deck[0] # Obtain first card
            self.deck.popleft() # Delete first card from the deck
            cards.append(card)
        return cards

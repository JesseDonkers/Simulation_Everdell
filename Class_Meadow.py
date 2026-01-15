class Meadow:
    def __init__(self):
        self.meadow = []
        
    def __str__(self):
        return str(self.meadow)

    # Function to add cards to the meadow
    def add_to_meadow(self, nrCards, deck):
        for _ in range(nrCards):
            self.meadow.append(deck.drawCard())
        return self.meadow

    # A player can draw one or multiple cards from the meadow
    def draw_cards(self, listofcards, deck, discardpile):
        for card in listofcards:
            self.meadow.remove(card)
        deck.drawCards(len(listofcards), discardpile) # Replenish the meadow from the deck
        return listofcards

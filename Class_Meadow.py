class Meadow:
    def __init__(self):
        self.cards = []
        
    def __str__(self):
        return str(self.cards)

    # Function to add cards to the meadow
    def add_to_meadow(self, nrCards, deck, discardpile):
        cards = deck.draw_cards(nrCards, discardpile)
        self.cards.extend(cards)
        return self.cards

    # A player can draw one or multiple cards from the meadow
    def draw_cards(self, listofcards, deck, discardpile):
        for card in listofcards:
            self.cards.remove(card)
        deck.draw_cards(len(listofcards), discardpile) # Replenish the meadow from the deck
        return listofcards

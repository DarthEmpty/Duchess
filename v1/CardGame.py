# external modules
from random import randint

# global constants
RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
SUITS = ("d", "c", "h", "s")


# classes
class Card(object):
    """A card object consisting of a rank and a suit."""

    # Constructor
    def __init__(self, rank, suit):
        self._rank = rank
        self._suit = suit

    # toString
    def __str__(self):
        return self._rank + self._suit  # e.g. "3h"

    # Getters
    def getRank(self):
        """Returns an integer value of the rank of a card object."""
        if self._rank == "A":
            return 1, 14  # Both values of Ace are returned
        elif self._rank == "J":
            return 11,  # Tuple form because of Ace's values
        elif self._rank == "Q":
            return 12,
        elif self._rank == "K":
            return 13,
        else:
            return int(self._rank),

    def getStringRank(self):
        """Returns a string of the rank of the card object"""
        return self._rank

    def getSuit(self):
        """Returns the suit of a card object as a single string letter.
        'd' = diamonds, 'c' = clubs, 'h' = hearts, 's' = spades."""
        return self._suit


class CardPile(object):
    """The most basic collection of card objects."""

    # Constructor
    def __init__(self):
        self._cards = []  # list for cards in CardPile

    # toString
    def __str__(self):
        cards = ""
        n = 0

        while n < len(self._cards):
            cards += str(self._cards[n]) \
                     + " [" + str(n + 1) + "]"
            n += 1
            if n < len(self._cards):
                cards += ", "

        return cards  # e.g. "As [1], 9d [2], ..."

    # Getters
    def getCards(self):
        return self._cards

    # Setters
    def setCards(self, cards):
        self._cards = cards

    # Methods
    def receiveCard(self, card, card_pos=-1):
        """Adds the input card to the CardPile's list of cards.
        'card' is put to the end of the list by default.
        'card' must be a card object.
        'card_pos' must be an integer referring to the new position of the input card."""

        if card_pos < 0:
            self._cards.append(card)
        else:
            self._cards.insert(card_pos, card)

    def sendCard(self, dest, old_card_pos=0, new_card_pos=-1):
        """Sends a card from own card list to another card list.
        Cards are sent from the start of self's card list to the end of 'dest's' card list by default.
        'dest' must be a cardpile object.
        'old_card_pos' must be an integer referring to the position of the card to be sent.
        'new_card_pos' must be an integer referring to the new position of the sent card."""

        card = self._cards.pop(old_card_pos)
        dest.receiveCard(card, new_card_pos)

    def isEmpty(self):
        """Checks to see if the list of cards is empty."""
        return len(self._cards) == 0


class Deck(CardPile):
    """A collection of card objects with the ability to generate all cards,
    shuffle cards and deal cards."""

    def populate(self, jokers=False):
        """Fills the deck with the complete list of 52 cards (54 if jokers = true)."""

        for i in RANKS:
            for j in SUITS:
                self._cards.append(Card(i, j))  # Generates all cards of each suit

        # Generating Jokers
        if jokers:
            self._cards.append(Card("Joker", "Red"))  # Generates Red Joker
            self._cards.append(Card("Joker", "Black"))  # Generated Black Joker

    def shuffle(self):
        """Randomly swaps the positions of cards in order to shuffle them."""

        temp = None
        SWAPS = 1000

        for i in range(SWAPS):
            x = y = 0
            while x == y:
                x = randint(0, len(self._cards) - 1)
                y = randint(0, len(self._cards) - 1)
            temp = self._cards[x]
            self._cards[x] = self._cards[y]
            self._cards[y] = temp

    def deal(self, dest, amount):
        """Sends the given amount of cards to dest's card list.
        'dest' must be a CardPile object.
        'amount' must be an integer smaller than the current size of the deck."""

        while (amount and len(self._cards)) > 0:
            self.sendCard(dest)
            amount -= 1
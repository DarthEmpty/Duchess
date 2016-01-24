# external modules
import os
import CardGame
import DuchIO

# global constants
SPECIAL_RANKS = ("2", "7", "8", "J", "Q", "K")


# objects
class DuchCard(CardGame.Card):
    """A card object for Duchess consisting of a rank, a suit and the ability to battle."""

    # Constructor
    def __init__(self, rank, suit):
        super().__init__(rank, suit)
        self._destroyed = False

    # Getters
    def isDestroyed(self):
        return self._destroyed

    # Setters
    def setDestroyed(self, boolean):
        self._destroyed = boolean


class SpecialDuchCard(DuchCard):
    """An enhanced DuchCard object with an ability unique to its rank."""

    # Constructor
    def __init__(self, rank, suit):
        super().__init__(rank, suit)
        self._active = True

    # Getters
    def isActive(self):
        return self._active

    # Setters
    def setActive(self, boolean):
        self._active = boolean


class DuchDeck(CardGame.Deck):
    """A collection of card objects with the ability to generate, shuffle and deal DuchCards."""

    # Methods
    def populate(self, jokers=False):
        """Fills the DuchDeck with the complete list of 52 cards (54 if jokers = true)."""

        for i in CardGame.RANKS:
            for j in CardGame.SUITS:
                if i in SPECIAL_RANKS:
                    self._cards.append(SpecialDuchCard(i, j))  # Generates all special DuchCards
                else:
                    self._cards.append(DuchCard(i, j))  # Generated all other normal DuchCards

        # PROGRAM NOT YET PREPARED FOR JOKERS
        if jokers:
            self._cards.append(DuchCard("Joker", "Red"))  # Generates Red Joker
            self._cards.append(DuchCard("Joker", "Black"))  # Generated Black Joker


class Hand(CardGame.CardPile):
    """The place where DuchCards are played from.
    'capacity' must be an integer."""

    # Constructor
    def __init__(self, capacity):
        super().__init__()
        self._CAPACITY = capacity

    # Getters
    def getCapacity(self):
        return self._CAPACITY

    # Methods
    def isFull(self):
        """Checks to see if the field is full."""
        return len(self._cards) >= self._CAPACITY


class Field(Hand):
    """The place where DuchCards are played.
    'capacity' must be an integer."""

    # Constructor
    def __init__(self, capacity):
        super().__init__(capacity)
        self._tributes = 0

    # Getters
    def getTributes(self):
        return self._tributes

    # Methods
    def incrementTributes(self):
        """Increases the number of tributes by 1."""
        self._tributes += 1

    def resetTributes(self):
        """Reduces the number of tributes to 0."""
        self._tributes = 0


class Battlefield(CardGame.CardPile):
    """The place where DuchCards are sent to battle."""

    # Methods
    def battleRanks(self):
        """Compares the ranks of the attacking and defending cards.
        The attacker only wins if its rank is higher than that of the defender.
        Otherwise, there is no battle."""

        # Getting ranks of cards in question
        attack_rank = self._cards[0].getRank()[0]
        defence_rank = self._cards[1].getRank()[-1]

        if attack_rank > defence_rank:
            self._cards[1].setDestroyed(True)  # Destroys defending card

        return attack_rank > defence_rank

    def battleSuits(self):
        """Compares the suits of the attacking and defending cards.
        The attacker only wins if its suit is before the defender's suit in the list
        of suits in CardGame.
        (So, diamonds beats clubs beats hearts beats spades beats diamonds.)
        Otherwise, there is no battle."""

        # Getting suits of cards in question
        attack_suit = self._cards[0].getSuit()
        defence_suit = self._cards[1].getSuit()

        # Indexing the attacker's suit
        n = CardGame.SUITS.index(attack_suit)
        if n == 3:
            n = -1  # Allows spades to beat diamonds

        if defence_suit == CardGame.SUITS[n + 1]:
            self._cards[1].setDestroyed(True)  # Destroy defending card

        return defence_suit == CardGame.SUITS[n + 1]

    def battleCards(self):
        """Compares the ranks of two battlinng cards. Will only compare the suits
        if the rank battle fails. If the attacking card doesn't win, ther is no battle."""

        if not self.battleRanks():  # Conducts rank battle
            return self.battleSuits()  # Conducts suit battle if rank battle fails
        return True


class Player(object):
    """An abstraction of the user, allowing a human to interact with the system and play the game.
    The player object consists of a deck, hand, field and a grave as well as a name and 'played' and 'battled' flags.
    'name' must be a String."""

    # Constructor
    def __init__(self, name):
        self._name = name  # The player's name
        self._deck = DuchDeck()  # Where player draws from
        self._hand = Hand(8)  # Where player plays from
        self._field = Field(5)  # Where cards in play are
        self._battlefield = Battlefield()  # Where cards are sent to battle others
        self._grave = CardGame.CardPile()  # Where cards go once destroyed
        self._played = False  # flag to say if the player has played a card this turn
        self._battled = False  # flag to say if the player has battled this turn

    # toString
    def __str__(self):
        name = "\nName: " + self._name
        field = "\nField: " + str(self._field)
        hand = "\nHand: " + str(self._hand)
        deck_size = "\nNo. of cards in deck: " + str(len(self._deck.getCards()))
        tributes = "\nNo. of cards tributed this go: " + str(self._field.getTributes())

        return str(name + field + hand + deck_size + tributes)

    # Getters
    def getName(self):
        return self._name

    def getDeck(self):
        return self._deck

    def getHand(self):
        return self._hand

    def getField(self):
        return self._field

    def getBattlefield(self):
        return self._battlefield

    def getGrave(self):
        return self._grave

    def hasPlayed(self):
        return self._played

    def hasBattled(self):
        return self._battled

    # Setters
    def setDeck(self, deck):
        self._deck = deck

    def setHand(self, hand):
        self._hand = hand

    def setField(self, field):
        self._field = field

    def setGrave(self, grave):
        self._grave = grave

    # Methods
    def reset(self):
        """Restarts the player's go. """

        self._field.resetTributes()
        self._played = False
        self._battled = False

    def burn(self):
        """Destroys the top card of the player's deck, burning the card."""
        self._deck.getCards()[0].setDestroyed(True)

    def bury(self, source, card_pos=0):
        """Moves a card from its source to the player's grave.
        The first card in a CardPile is buried by default.
        'card_pos' must be an integer referring to the position of the card to be buried.
        'source' must be the CardPile object that card is in."""
        source.sendCard(self._grave, card_pos)

    def draw(self):
        """Sends a card from the top of the player's deck to their hand if the game isn't just starting.
        Otherwise, the player's first 5 cards are dealt to them."""

        if self._hand.isEmpty() and self._field.isEmpty() and self._grave.isEmpty():
            self._deck.deal(self._hand, 5)
        elif not self._deck.isEmpty():
            self._deck.sendCard(self._hand)

    def tribute(self, source, card_pos):
        """Destroys and buries a card in the player's CardPile, tributing the card.
        'source' must be either the player's hand or field.
        'card_pos' must be an integer referring to the position of the card to be tributed."""

        source.getCards()[card_pos].setDestroyed(True)
        self.bury(source, card_pos)
        self._field.incrementTributes()

    def play(self, card_pos):
        """Sends a card from the player's hand to their field, playing the card.
        'card_pos' must be an integer referring to the position of the card to be sent."""

        self._hand.sendCard(self._field, card_pos)
        self._played = True  # Tells the player object that a card has been played
        self._field.resetTributes()

    def battle(self, opponent, atk_card_pos, def_card_pos):
        """Sends a card from the player's field and a card from the opponent's field
        to the player's battlefield, battling the cards.
        'opponent' must be a player object.
        'atk_card_pos' must be an integer referring to the position of the player's card to be sent.
        'def_card_pos' must be an integer referring to the position of the opponent's card to be sent."""

        # Sending cards in question to the battlefield
        op_field = opponent.getField()
        self._field.sendCard(self._battlefield, atk_card_pos, 0)
        op_field.sendCard(self._battlefield, def_card_pos, 1)

        # Whether the player has battled or not depends on the result of the battle
        self._battled = self._battlefield.battleCards()

        # Returning cards in question to their respective players
        if self._battlefield.getCards()[1].isDestroyed():
            opponent.bury(self._battlefield, 1)
        else:
            self._battlefield.sendCard(op_field, 1, def_card_pos)
        opponent.setField(op_field)

        self._battlefield.sendCard(self._field, 0, atk_card_pos)

    def menuIO(self):
        """Asks the user what they want to do during their go."""

        choice = DuchIO.ask(str(self)
                            + "\nEnter:\n"
                            + "\t1 - Tribute\n"
                            + "\t2 - Play\n"
                            + "\t3 - Battle\n"
                            + "\t4 - View other fields\n"
                            + "\tq - End your go\n",
                            "1234q", "\nPlease enter a valid option.\n")
        return choice

    def overflowIO(self):
        """Asks the user about which card they wish to get rid of since their hand is full."""

        choice = DuchIO.ask("\nYour hand:\n"
                            + str(self._hand)
                            + "\nYour hand is too full"
                            + "\nEnter the number of a card to destroy so you can continue",
                            DuchIO.prepareOptions(self._hand.getCards()))
        return choice

    def tributeIO(self):
        """Asks the user about which card they wish to tribute.
        Will ask if they want to tribute from the hand if their deck is empty."""

        choice = ""

        if self._deck.isEmpty():
            choice = DuchIO.ask("\nWould you like to tribute from the hand? (y/n)\n",
                                "yn")
        if choice == "y":
            source = self._hand
            label = "\nYour hand:"
        else:
            source = self._field
            label = "\nYour field:"

        choice = DuchIO.ask(label
                            + str(source)
                            + "\nEnter the number of the card you want to tribute"
                            + "\n(or 'c' to cancel)\n",
                            DuchIO.prepareOptions(source.getCards()) + "c")
        return choice, source

    def playIO(self):
        """Asks the user about which card they wish to play."""

        choice = DuchIO.ask("\nYour hand:\n"
                            + str(self._hand)
                            + "\nEnter the number of the card you want to play"
                            + "\n(or c to cancel)\n",
                            DuchIO.prepareOptions(self._hand.getCards()) + "c")
        return choice

    def battleIO(self, opponent):
        """Asks the user about which of their cards and their opponents cards they want to battle."""

        atk_card_pos = DuchIO.ask("\nYour Field:\n"
                                  + str(self._field)
                                  + "\nEnter the number of the card you want "
                                  + "to attack with:\n(or 'c' to cancel)\n",
                                  DuchIO.prepareOptions(self._field.getCards()) + "c")

        if atk_card_pos != "c":
            def_card_pos = DuchIO.ask("\nYour Opponent's Field:\n"
                                      + str(opponent.getField())
                                      + "\nEnter the number of the card you want "
                                      + "to attack:\n(or 'c' to cancel)\n",
                                      DuchIO.prepareOptions(opponent.getField().getCards())
                                      + "c")
            return atk_card_pos, def_card_pos

        return "c", "c"

    def go(self, progress="", opponent=None):
        """Takes the user through a series of other methods organised in such a way that allows them to have a turn
        in the game.
        Allows the Player to be in communication with the Playground object that it's in so that, based on its
        parameters, it can start at different places.
        'progress' must be a string.
        'opponent' must be a Player object."""

        choice = ""  # Stores the user's choice

        # "Start of go" preparations
        if not progress:
            self.draw()
            self.reset()

            # Get player to discard a card if their hand is full
            while self._hand.isFull():
                choice = self.overflowIO()
                self._hand.getCards()[int(choice) - 1].setDestroyed(True)
                self.bury(self._hand, int(choice) - 1)
                choice = ""

        # Continuation of battle stage
        elif progress == "battling":
            choice = "3"

        # Player's main loop
        while choice != "q":
            # Menu
            if not choice:
                choice = self.menuIO()

            # Tributing
            if choice == "1":
                if self._played:
                    DuchIO.notify("\nYou can't tribute after you've played a card.")
                elif self._field.isEmpty():
                    DuchIO.notify("\nYour field is empty. Play a card and tribute next turn.")
                else:
                    choice, source = self.tributeIO()
                    if choice != "c":
                        self.tribute(source, int(choice) - 1)

            # Playing
            elif choice == "2":
                if self._played:
                    DuchIO.notify("\nYou've already played a card this turn.")
                elif self._field.isFull():
                    DuchIO.notify("\nYour field is too full to play anymore cards right now.")
                else:
                    choice = self.playIO()
                    if choice != "c":
                        tributes = self._field.getTributes()
                        card_rank = self._hand.getCards()[int(choice) - 1].getRank()[0]
                        if ((tributes == 0 and card_rank < 6) or
                                (tributes == 1 and card_rank < 11) or
                                    tributes == 2):
                            self.play(int(choice) - 1)
                            return "playing", None  # Tells Playground that Player has just played a card
                        else:
                            DuchIO.notify("\nYou can't do that. Please tribute more cards.")

            # Battling
            elif choice == "3":
                if self._battled:
                    DuchIO.notify("\nYou've already battled cards this turn.")
                elif self._field.isEmpty():
                    DuchIO.notify("\nYou field is empty. Play a card if you want to battle it.")
                elif opponent:  # From playground
                    atk_card_pos, def_card_pos = self.battleIO(opponent)
                    if def_card_pos != "c":
                        self.battle(opponent, int(atk_card_pos) - 1, int(def_card_pos) - 1)
                        if self._battled:
                            DuchIO.notify("\nTarget destroyed!")
                        else:
                            DuchIO.notify("\nPlease choose appropriate cards to battle.")
                    return "battle complete", opponent  # Tells playground that Player is done battling
                else:
                    return "battling", None  # Request to Playground for opponent

            # Viewing fields
            elif choice == "4":
                return "viewing", None  # Request to Playground for opponents' fields

            # Reset choice to go back to the menu
            if choice != "q":
                choice = ""

        return "done", None  # Tells Playground that Player is done with their go


class Playground(object):
    """The place where Duchess is hosted. Players interact here.
    The control of the flow of the game is delegated to the playground."""

    # Constructor
    def __init__(self, *players):
        # Creating the attribute objects
        self._players = list(players)  # Where the players are stored
        self._losers = []  # Where players that have lost are stored
        self._turnPlayer = 0  # Indicator stating who's turn it is

        # Creating and shuffling the master deck
        master = DuchDeck()
        master.populate()
        master.shuffle()

        card_total = len(master.getCards())
        player_total = len(self._players)

        # Distributing the cards between players
        for player in self._players:
            deck = player.getDeck()
            master.deal(deck, int(card_total / player_total))
            deck.shuffle()
            player.setDeck(deck)
            player.draw()

    # Methods
    def getOpponents(self):
        """Creates a list of opponents and options to choose from for the turnPlayer."""
        options = ""
        opponents = ""
        n = 0

        while n < len(self._players):
            if n != self._turnPlayer:  # Ensures turnPlayer is ignored
                opponents += "\n" + self._players[n].getName() + "[" + str(n + 1) + "]" \
                             + "\n" + str(self._players[n].getField()) + "\n"
                options += str(n + 1)
            n += 1

        return opponents, options

    def royalIO(self, rank):
        """Asks the user about which of their cards in their grave they want to revive, rescue or reset.
        'rank' must be an integer between 11 and 13 inclusive."""

        player = self._players[self._turnPlayer]

        # Determine action depending on rank
        if rank == 11:
            action = "revive"
        elif rank == 12:
            action = "rescue"
        else:
            action = "reset"

        choice = DuchIO.ask("\nYour Grave:\n"
                            + str(player.getGrave())
                            + "\nEnter the number of the card you wish to " + action + "\n",
                            DuchIO.prepareOptions(player.getGrave().getCards()))

        return int(choice) - 1

    def opponentIO(self):
        """Asks the user about which opponent they wish to do battle with."""

        opponents, options = self.getOpponents()
        choice = DuchIO.ask(opponents + "\nEnter the number of the player you wish to battle with\n",
                            options + "c")
        return choice

    def twoEffect(self):
        """Causes all opponents of the turnPlayer to draw a card from their respective decks."""

        n = 0
        while n < len(self._players):
            if n != self._turnPlayer:
                self._players[n].draw()
            n += 1
        DuchIO.notify("\nAll other players draw a card!")

    def sevenEffect(self):
        """Causes all opponents of the turnPlayer to burn the top card of their respective decks."""

        n = 0
        while n < len(self._players):
            if n != self._turnPlayer and not self._players[n].getDeck().isEmpty():
                self._players[n].burn()
                self._players[n].bury(self._players[n].getDeck())
            n += 1
        DuchIO.notify("\nAll other players burn the top card of their deck!")

    def eightEffect(self):
        """Causes the turnPlayer's go to restart."""

        self._players[self._turnPlayer].reset()
        DuchIO.notify("\nYour go starts again!")

    def royalEffect(self, rank):
        """Allows the turnPlayer to revive, rescue or reset a card from their grave,
        depending on the value of 'rank'.
        'rank' must be an integer between 11 and 13 inclusive."""

        grave = self._players[self._turnPlayer].getGrave()
        cards = grave.getCards()

        card_pos = self.royalIO(rank)

        # Determine where the card will be sent to
        if rank == 11:
            source = self._players[self._turnPlayer].getField()
        elif rank == 12:
            source = self._players[self._turnPlayer].getHand()
        else:
            source = self._players[self._turnPlayer].getDeck()

        # Bring the card back to life
        cards[card_pos].setDestroyed(False)
        if cards[card_pos].getStringRank() in SPECIAL_RANKS:
            cards[card_pos].setActive(True)

        grave.setCards(cards)
        grave.sendCard(source, card_pos)
        if rank == 13:
            source.shuffle()

        self._players[self._turnPlayer].setGrave(grave)
        if rank == 11:
            self._players[self._turnPlayer].setField(source)
        elif rank == 12:
            self._players[self._turnPlayer].setHand(source)
        else:
            self._players[self._turnPlayer].setDeck(source)

    def trigger(self):
        """Handles the activation of SpecialDuchCard abilities, activating them once the card in question has been
        played."""

        cards = self._players[self._turnPlayer].getField().getCards()

        for card in cards:
            string_rank = card.getStringRank()
            if string_rank in SPECIAL_RANKS and card.isActive():
                rank = card.getRank()[0]
                if rank == 2:
                    self.twoEffect()
                elif rank == 7:
                    self.sevenEffect()
                elif rank == 8:
                    self.eightEffect()
                else:
                    self.royalEffect(rank)
                card.setActive(False)

        self._players[self._turnPlayer].getField().setCards(cards)

    def turn(self):
        """Allows the turnPlayer to have their turn in the Playground, alerting them about it at the start of it
        and progressing on to the next player at the end.
        Allows the Playground to be in communication with each Player object that it has so that, based on its
        parameters, the Player can start at different places.
        """

        player = self._players[self._turnPlayer]
        progress = ""
        opponent = None

        # Alert the turnPlayer of their turn
        DuchIO.notify("\nThis turn: " + player.getName())

        # Let them have their go
        while progress != "done":
            progress, opponent = player.go(progress, opponent)  # variables set up for requests and notifications

            # if they play a SpecialDuchCard, trigger its effect immediately
            if progress == "playing":
                self.trigger()

            # if they wish to battle, let them choose their opponent
            elif progress == "battling":
                if len(self._players) == 2:
                    choice = self._turnPlayer
                else:
                    choice = self.opponentIO()

                if choice != "c":
                    opponent = self._players[int(choice) - 1]  # will always select other player as opponent
                else:
                    progress = "cancel"

            # if they've finished battling, return the opponent to the original list
            elif progress == "battle complete":
                self._players[self._players.index(opponent)] = opponent
                opponent = None

            elif progress == "viewing":
                DuchIO.notify(self.getOpponents()[0])

        # Sort out the losers from the winners
        for player in self._players:
            if player.getField().isEmpty() and player.getHand().isEmpty() and player.getDeck().isEmpty():
                self._losers.append(self._players.pop(self._players.index(player)))
                DuchIO.notify(player.getName() + " has lost!")

        # Proceed to the next player
        if self._turnPlayer == len(self._players) - 1:
            self._turnPlayer = -1

        self._turnPlayer += 1

    def start(self):
        """Begins the mainloop of Duchess. Continues until a there's only one player that hasn't lost."""

        while len(self._players) != 1:
            self.turn()
            os.system("cls")
        DuchIO.notify("\n" + self._players[0].getName() + " has won!")
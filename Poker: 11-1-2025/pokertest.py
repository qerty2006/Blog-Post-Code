import random

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __lt__(self, other):
        return self.rank < other.rank

    def __gt__(self, other):
        return self.rank > other.rank

class Hand:
    def __init__(self):
        self.rank_points = {
            "A": 2**(-1), "K": 2**(-2), "Q": 2**(-3), "J": 2**(-4),
            "T": 2**(-5), "9": 2**(-6), "8": 2**(-7), "7": 2**(-8),
            "6": 2**(-9), "5": 2**(-10), "4": 2**(-11), "3": 2**(-12),
            "2": 2**(-13)
        }
        self.numcards = {"2":0, "3":0, "4":0, "5":0, "6":0, "7":0, "8":0, "9":0, "T":0, "J":0, "Q":0, "K":0, "A":0}
        self.suitcards = {"♠":0, "♥":0, "♦":0, "♣":0}
        self.cards = []
        self.hand = ""
        self.score = 0

    def add_card(self, card):
        self.cards.append(card)
        self.numcards[card.rank] += 1
        self.suitcards[card.suit] += 1
    def add_cards(self, cards):
        for card in cards:
            self.add_card(card)
    def __add__(self, other):
        if isinstance(other, Hand):
            for card in other.cards:
                self.add_card(card)
        else:
            raise TypeError("Can only add other Hand objects")
        return self

    def show_hand(self):
        return ', '.join(str(card) for card in self.cards)

    def __eq__(self, value):
        if isinstance(value, Hand):
            return self.cards == value.cards
        else:
            return False

    def sort(self):
        self.cards.sort(key=lambda card: 1-self.rank_points[card.rank])

    def quality(self):
        backup = Hand()
        backup = backup + self
        backup.sort()

        hand_points = {
            "Straight Flush": 18, "Four of a Kind": 15, "Full House": 12,
            "Flush": 10, "Straight": 8, "Three of a Kind": 5,
            "Two Pair": 3, "Pair": 1, "High Card": 0
        }

        cards = []
        mult_score = 0
        size = {"0": 0,"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}

        # Check for Four of a Kind first
        if 4 in backup.numcards.values():
            mult_score = hand_points["Four of a Kind"]
            cards = [card for card in backup.cards if backup.numcards[card.rank] == 4]
            for card in cards:
                backup.cards.remove(card)
            self.hand = "Four of a Kind"
            return mult_score + sum(self.rank_points[card.rank] for card in cards), self.hand

        elif 3 in (backup.numcards.values()):
            fullhouse = False
            rank = list(backup.numcards.keys())[list(backup.numcards.values()).index(3)]
            cards = [card for card in backup.cards if backup.numcards[card.rank] == rank]
            #print(rank)
            #removes the isolated hand from the original hand
            backup.cards = [card for card in backup.cards if card not in cards]
            backup.numcards[rank] = 0
            #print(backup.numcards)
            #now check for the highest rank  with at least a pair

            if 3 in (backup.numcards.values()) or 2 in (backup.numcards.values()):
                #print(backup.numcards)
                """rank1 = list(backup.numcards.keys())[list(backup.numcards.values()).index(3)] or "0"
                rank2 = list(backup.numcards.keys())[list(backup.numcards.values()).index(2)] or "0"
                    #rank is the key rank of the bigger rank given rank1 and rank2 using the size dictionary so 14 is A
                rank = rank1 if size[rank1] > size[rank2] else rank2"""
                rank1 = next((rank for rank, count in backup.numcards.items() if count == 3), "0")
                rank2 = next((rank for rank, count in backup.numcards.items() if count == 2), "0")
                
                # Assuming 'size' is a dictionary that maps ranks to their numerical values
                rank = rank1 if size[rank1] > size[rank2] else rank2


                part2hand = [card for card in backup.cards if backup.numcards[card.rank] == rank]
                cards.extend(part2hand[0:2])
                #removes the isolated hand from the original hand 
                for card in part2hand:
                    backup.cards.remove(card)
                fullhouse = True
            mult_score += hand_points["Full House"] if fullhouse else hand_points["Three of a Kind"]
        elif 2 in (backup.numcards.values()):
            twopair = False
            rank = list(backup.numcards.keys())[list(backup.numcards.values()).index(2)]
            cards = [card for card in self.cards if backup.numcards[card.rank] == rank]
            #removes the isolated hand from the original hand
            for card in cards:
                backup.cards.remove(card)
            #now check for the highest rank  with at least a pair
            if 2 in (backup.numcards.values()):
                rank = list(backup.numcards.keys())[list(backup.numcards.values()).index(2)] or None
                #rank is the key rank of the bigger rank given rank1 and rank2 using the size dictionary so 14 is A
                rank 
                part2hand = [card for card in backup.cards if backup.numcards[card.rank] == rank]
                cards.extend(part2hand)
                #removes the isolated hand from the original hand 
                for card in part2hand:
                    backup.cards.remove(card)
            mult_score += hand_points["Two Pair"] if twopair else hand_points["Pair"]
        backup.sort()
        #while num of cards in hand is less than 5 add the next highest card
        while len(backup.cards) < 5:
            backup.add_card(next((card for card in self.cards if card not in backup.cards)))
        #scroe with this type of hand
        mult_score += sum(self.rank_points[card.rank] for card in cards)

        side_score = 0
        backup2 = Hand() + self
        backup2.sort()

        # Check for flush
        flush = False
        flush_suit = None
        for suit, count in backup2.suitcards.items():
            if count >= 5:
                flush = True
                flush_suit = suit
                break

        # Check for straight
        straight = False
        A_low = 0
        ranks = "23456789TJQKA"  # Note: A can be high or low
        rank_sequence = "".join(sorted(set(card.rank for card in backup2.cards), key=lambda x: ranks.index(x)))
        
        for i in range(len(ranks) - 4):
            if ranks[i:i+5] in rank_sequence:
                straight = True
                straight_high = ranks[i+4]
                break
            
        else:
            if "2345A" in rank_sequence:
                straight = True
                A_low = 1

        # Determine the hand quality
        if flush and straight:
            # Check if it's a straight flush
            flush_cards = [card for card in backup2.cards if card.suit == flush_suit]
            flush_ranks = "".join(sorted(set(card.rank for card in flush_cards), key=lambda x: ranks.index(x)))
            straight_flush = False
            for j in range(len(ranks) - 4):
                if ranks[j:j+5] in flush_ranks:
                    straight_flush = True
                    break
            else:
                if "2345A" in flush_ranks:
                    straight_flush = True
            
            if straight_flush:
                backup2 = Hand()
                self.hand = "Straight Flush"
                side_score = 18 - 0.5 * A_low
                #puts only the straight flush cards into the hand
                for card in flush_cards:
                    if card.rank in ranks and len(backup2.cards) < 5:
                        backup2.add_card(card)


            
        elif flush:
            
            side_score = 10
            #puts only the flush cards into the hand
            backup2 = Hand()
            self.cards.sort()
            for card in self.cards:
                if card.suit == flush_suit and len(backup2.cards) < 5:
                    backup2.add_card(card)

        elif straight:
            side_score = 8 - 0.5 * A_low
            backup2 = Hand()
            self.cards.sort()
            #puts only the straight cards into the hand
            for card in self.cards:
                if card.rank in rank_sequence and len(backup2.cards) < 5:
                    backup2.add_card(card)

    

        score = max(mult_score, side_score)
        if mult_score > side_score:
            self.cards = backup.cards
        else:
            self.cards = backup2.cards

        for card in self.cards:
            score += self.rank_points[card.rank]

        self.score = score

        for hand, hand_score in hand_points.items():
            if hand_score <= self.score:
                self.hand = hand
                break

        return self.score, self.hand

class Deck:
    def __init__(self, fresh=True):
        if fresh:
            suits = ['♠', '♥', '♦', '♣']
            ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
            self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        else:
            self.cards = []

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            return None

    def __add__(self, other):
        if isinstance(other, Deck):
            self.cards.extend(other.cards)
        elif isinstance(other, Card):
            self.cards.append(other)
        else:
            raise TypeError("Can only add Card or other Deck objects")

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = Hand()
        self.score = 0
        self.type = ""

    def add_card(self, card):
        self.hand.add_card(card)

    def add_cards(self, cards):
        for card in cards:
            self.add_card(card)

    def show_hand(self):
        return self.hand.show_hand()

    def sort(self):
        self.hand.sort()

    def quality(self):
        self.score, self.hand = self.hand.quality()

class community_cards:
    def __init__(self):
        self.hand = Hand()

    def add_card(self, card):
        self.hand.add_card(card)

    def show_hand(self):
        return self.hand.show_hand()

    def sort(self):
        self.hand.sort()

def simulate_poker(num_players, debug=False, printer=False):
    deck1 = Deck()
    deck1.shuffle()
    players = [Player(f"Player {i+1}") for i in range(num_players)]
    community = community_cards()

    for _ in range(2):
        for player in players:
            card = deck1.deal()
            player.add_card(card)

    for _ in range(5):
        card = deck1.deal()
        community.add_card(card)

    for player in players:
        player.sort()
        if debug:
            print(f"{player.name}'s hand: {player.show_hand()}")
        player.hand = player.hand + community.hand
        player.sort()
        player.hand.quality()
        if debug:
            print("full hand =", player.show_hand(), player.hand.quality())

    best_player = max(players, key=lambda player: player.hand.score)
    if debug or printer:
        print(f"Best player: {best_player.name} with hand: {best_player.show_hand()} with score: {best_player.hand.score} and hand: {best_player.hand.hand}")

    community.sort()
    if debug:
        print(f"Community cards: {community.show_hand()}")

    return players, community, best_player, deck1

from itertools import combinations

def test_all_7_card_hands():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    deck = [Card(suit, rank) for suit in suits for rank in ranks]

    # Generate all possible 7-card combinations from the deck
    all_hands = combinations(deck, 7)

    # Test each combination
    for hand_cards in all_hands:
        test_hand = Hand()
        test_hand.add_cards(hand_cards)
        test_hand.sort()
        quality, hand_type = test_hand.quality()

        print(f"Hand: {test_hand.show_hand()}, Quality: {quality}, Type: {hand_type}")

# Note: Running this function would take significant time and resources due to the large number of combinations
test_all_7_card_hands()



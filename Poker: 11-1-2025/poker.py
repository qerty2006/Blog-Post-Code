import random
import json
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
        self.numcards = {"2":0, "3":0, "4":0, "5":0, "6":0, "7":0, "8":0, 
                        "9":0, "T":0, "J":0, "Q":0, "K":0, "A":0}
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
        size = {"0": 0, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
                "8": 8, "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}

        # Four of a Kind
        if 4 in backup.numcards.values():
            mult_score = hand_points["Four of a Kind"]
            quads = [card for card in backup.cards if backup.numcards[card.rank] == 4]
            remaining = [card for card in backup.cards if card not in quads]
            remaining.sort(key=lambda card: self.rank_points[card.rank], reverse=True)
            backup.cards = quads + remaining[:1]
            self.hand = "Four of a Kind"
            return mult_score + sum(self.rank_points[card.rank] for card in backup.cards), self.hand

        # Full House and Three of a Kind
        elif 3 in backup.numcards.values():
            trips_rank = next(rank for rank, count in backup.numcards.items() if count == 3)
            trips = [card for card in backup.cards if card.rank == trips_rank]
            remaining = [card for card in backup.cards if card not in trips]
            
            # Check for Full House
            if 2 in [backup.numcards[card.rank] for card in remaining]:
                pair_rank = next(card.rank for card in remaining 
                               if backup.numcards[card.rank] == 2)
                pair = [card for card in remaining if card.rank == pair_rank][:2]
                backup.cards = trips + pair
                mult_score = hand_points["Full House"]
            else:
                remaining.sort(key=lambda card: self.rank_points[card.rank], reverse=True)
                backup.cards = trips + remaining[:2]
                mult_score = hand_points["Three of a Kind"]

        # Pairs
        elif 2 in backup.numcards.values():
            pairs = []
            remaining = list(backup.cards)
            
            # Find all pairs
            for rank in backup.numcards:
                if backup.numcards[rank] == 2:
                    pair = [card for card in remaining if card.rank == rank]
                    pairs.extend(pair)
                    remaining = [card for card in remaining if card not in pair]
            
            remaining.sort(key=lambda card: self.rank_points[card.rank], reverse=True)
            
            if len(pairs) >= 4:  # Two pair
                backup.cards = pairs[:4] + remaining[:1]
                mult_score = hand_points["Two Pair"]
            else:  # One pair
                backup.cards = pairs[:2] + remaining[:3]
                mult_score = hand_points["Pair"]

        # Check for straight and flush
        flush = any(count >= 5 for count in backup.suitcards.values())
        flush_suit = next((suit for suit, count in backup.suitcards.items() 
                         if count >= 5), None)
        
        ranks = "23456789TJQKA"
        rank_sequence = "".join(sorted(set(card.rank for card in backup.cards), 
                                     key=lambda x: ranks.index(x)))
        
        straight = any(ranks[i:i+5] in rank_sequence for i in range(len(ranks) - 4))
        if not straight and "2345A" in rank_sequence:
            straight = True
            
        if flush and straight:
            flush_cards = [card for card in backup.cards if card.suit == flush_suit]
            flush_ranks = "".join(sorted(set(card.rank for card in flush_cards), 
                                       key=lambda x: ranks.index(x)))
            
            straight_flush = any(ranks[i:i+5] in flush_ranks 
                               for i in range(len(ranks) - 4))
            if not straight_flush and "2345A" in flush_ranks:
                straight_flush = True
                
            if straight_flush:
                backup.cards = [card for card in flush_cards 
                              if card.rank in ranks][:5]
                mult_score = hand_points["Straight Flush"]
        elif flush:
            flush_cards = [card for card in backup.cards if card.suit == flush_suit]
            flush_cards.sort(key=lambda card: self.rank_points[card.rank], reverse=True)
            backup.cards = flush_cards[:5]
            mult_score = hand_points["Flush"]
        elif straight:
            straight_cards = []
            for i in range(len(ranks) - 4):
                if ranks[i:i+5] in rank_sequence:
                    pattern = ranks[i:i+5]
                    straight_cards = [card for card in backup.cards 
                                    if card.rank in pattern][:5]
                    break
            if not straight_cards and "2345A" in rank_sequence:
                pattern = "2345A"
                straight_cards = [card for card in backup.cards 
                                if card.rank in pattern][:5]
            backup.cards = straight_cards
            mult_score = hand_points["Straight"]

        # Calculate final score
        score = mult_score
        for card in backup.cards[:5]:
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
        return self.cards.pop() if self.cards else None

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
        self.score, self.type = self.hand.quality()

class CommunityCards:
    def __init__(self):
        self.hand = Hand()

    def add_card(self, card):
        self.hand.add_card(card)

    def show_hand(self):
        return self.hand.show_hand()

    def sort(self):
        self.hand.sort()

def simulate_poker(num_players, debug=False, printer=False):
    deck = Deck()
    deck.shuffle()
    players = [Player(f"Player {i+1}") for i in range(num_players)]
    community = CommunityCards()

    # Deal hole cards
    for _ in range(2):
        for player in players:
            card = deck.deal()
            player.add_card(card)

    # Deal community cards
    for _ in range(5):
        card = deck.deal()
        community.add_card(card)

    # Evaluate hands
    for player in players:
        player.sort()
        if debug:
            print(f"{player.name}'s hand: {player.show_hand()}")
        player.hand = player.hand + community.hand
        player.sort()
        player.quality()
        if debug:
            print(f"Full hand = {player.show_hand()}, "
                  f"Quality: {player.score}, Type: {player.type}")

    best_player = max(players, key=lambda p: p.hand.score)
    if debug or printer:
        print(f"Winner: {best_player.name} with {best_player.show_hand()}, "
              f"Score: {best_player.hand.score}, Hand: {best_player.type}")

    community.sort()
    if debug:
        print(f"Community cards: {community.show_hand()}")

    return players, community, best_player, deck

from itertools import combinations

def test_all_7_card_hands():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    deck = [Card(suit, rank) for suit in suits for rank in ranks]
    all_hands = combinations(deck, 7)
    with open('test.json', 'a') as f:
        # Test each combination
        for hand_cards in all_hands:
            test_hand = Hand()
            test_hand.add_cards(hand_cards)
            test_hand.sort()
            quality, hand_type = test_hand.quality()
            print(f"Hand: {test_hand.show_hand()}, Quality: {quality}, Type: {hand_type}")
            json.dump({"Hand": test_hand.show_hand(), "Quality": quality, "Type": hand_type}, f)
            f.write('\n')

def testrandom7cardhands():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    handtypes = {"Straight Flush" : 0, "Four of a Kind" : 0, "Full House" : 0, "Flush" : 0, "Straight" : 0, "Three of a Kind" : 0, "Two Pair" : 0, "Pair" : 0, "High Card" : 0}
    for type in handtypes.keys():
        handtypes[type] = 10
    while len(handtypes) > 0:
        deck = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(deck)
        test_hand = Hand()
        test_hand.add_cards(deck[:7])
        test_hand.sort()
        quality, hand_type = test_hand.quality()
        if hand_type in handtypes.keys():
            print(f"Hand: {test_hand.show_hand()}, Quality: {quality}, Type: {hand_type}")
            handtypes[hand_type] -= 1
            if handtypes[hand_type] == 0:
                del handtypes[hand_type]

        
# Note: Running this function would take significant time and resources due to the large number of combinations
#test_all_7_card_hands()
#testrandom7cardhands()
#test a 7 card hand to see if it identfies correctly
test_hand = Hand()
test_hand.add_cards([Card('♥', '3'), Card('♠', '3'), Card('♠', '4'), Card('♠', '5'), Card('♠', '6'), Card('♠', '7'), Card('♠', '8')])
test_hand.sort()
quality, hand_type = test_hand.quality()
print(f"Hand: {test_hand.show_hand()}, Quality: {quality}, Type: {hand_type}")

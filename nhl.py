# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 20:13:56 2023

@author: brend
"""

import collections, random, string
import pandas as pd

class Card(object):
    def __init__(self,s,v):
        card_num_vals = {'T':10,'J':11,'Q':12,'K':13,'A':14}
        self.suit = s
        self.val = v
        if self.val in string.digits:
            self.num_val = int(self.val)
        else:
            self.num_val = card_num_vals.get(self.val)
    def __str__(self):
        return f'{self.val}{self.suit}'

class Deck(object):
    def __init__(self):
        self.d = [Card(s,v) for v in '23456789TJQKA' for s in 'cdhs']
        random.shuffle(self.d)
    def __str__(self):
        return f'\n{len(self.d)} cards remain in the deck...\n\n{", ".join([str(c) for c in self.d])}'
    def draw(self):
        card = self.d[0]; self.d.remove(card); return card

class Hand(object):
    def __init__(self,card1,card2):
        self.c1 = card1
        self.c2 = card2
        self.hand_class = self.classify_hand()
        self.hand_val = 0
        self.card_vals_of_made_hand = []
        self.five_card_hand = []
    def __str__(self):
        return f'{self.c1.val}{self.c1.suit}{self.c2.val}{self.c2.suit} ({self.hand_class})'
    def classify_hand(self):
        if self.c1.suit == self.c2.suit:
            suffix = 's'
        else:
            suffix = 'o'
        if self.c2.num_val == self.c1.num_val:
            return f'{self.c2.val}{self.c1.val}'
        if self.c2.num_val > self.c1.num_val:
            return f'{self.c2.val}{self.c1.val}{suffix}'
        else:
            return f'{self.c1.val}{self.c2.val}{suffix}'
    def evaluate_hand(self,board):
        '''
        Hand vals: 0=HC,1=P,2=2P,3=T,4=S,5=F,6=FH,7=Q,8=SF,9=RF
        
        '''
        playables = sorted([self.c1, self.c2]+board, key = lambda x:x.num_val, reverse=True)
        playables_num_vals = [p.num_val for p in playables]
        def eval_pairs_and_HC(playables):
            num_pairs = 0
            pairs = []
            count = dict(collections.Counter(playables_num_vals))
            for i,c in enumerate(count.items()):
                # print(c[1])
                if c[1] > 1:
                    num_pairs += 1
                    pairs.append(c[0])
            if len(pairs) == 0:
                self.hand_val = 0
                i = 0
                while len(self.five_card_hand) < 5 and i < len(playables):
                    if playables[i] not in self.five_card_hand:
                        self.five_card_hand.append(playables[i])
                        self.card_vals_of_made_hand.append((playables[i].num_val))
                    i += 1
            elif 1 <= len(pairs) <= 2:
                self.hand_val = len(pairs)
                self.five_card_hand = [p for p in playables if p.num_val in pairs]
                self.card_vals_of_made_hand = [p.num_val for p in playables if p.num_val in pairs]
                i = 0
                while len(self.five_card_hand) < 5 and i < len(playables):
                    if playables[i] not in self.five_card_hand:
                        self.five_card_hand.append(playables[i])  
                    i += 1
            elif len(pairs) > 2:
                pass # sort pairs, add top 2, then add top to five-card-hand

        if len(playables) == 2:
            hand_eval = eval_pairs_and_HC(playables)
        else:
            pass 
            # eval royal --> HC & pairs until binking a hand
            hand_eval = eval_pairs_and_HC(playables)
        # print(','.join([f'{fc.val}{fc.suit}' for fc in self.five_card_hand]))
        # print(num_pairs,pairs)

class Player(object):
    def __init__(self):
        self.holding = ''
        self.stack = 0
        self.player_type = ''

class Table(object):
    def __init__(self,num_players):
        self.deck = Deck()
        self.player_hands = [self.deal_player() for hand in range(num_players)]
        self.discarded_hands = []
        self.burn_pile = []
        self.board = []
    def __str__(self):
        return f'\n{", ".join([f"Player {i+1}: {h}" for i,h in enumerate(self.player_hands)])}\nBoard: {", ".join([f"{str(c)}" for i,c in enumerate(self.board)])}'
    def deal_player(self):
        return Hand(self.deck.draw(),self.deck.draw())
    def deal_flop(self):
        self.burn_pile.append(self.deck.draw())
        for c in range(3): self.board.append(self.deck.draw())
    def deal_turn_or_river(self):
        self.burn_pile.append(self.deck.draw())
        self.board.append(self.deck.draw())
    
### LIVE TEST CODE ###

if __name__ == '__main__':
    table = Table(5)
    print(table)
    table.deal_flop()
    print(table)
    table.deal_turn_or_river()
    print(table)
    table.deal_turn_or_river()
    print(table)
    # print(table.deck)
    
    player_to_eval = 1
    table.player_hands[player_to_eval].evaluate_hand(table.board)
    print(table.player_hands[player_to_eval])
    
    # print(table.player_hands[player_to_eval].five_card_hand)
    print(table.player_hands[player_to_eval].card_vals_of_made_hand)
    print([c.num_val for c in table.player_hands[player_to_eval].five_card_hand])
    print(table.player_hands[player_to_eval].hand_val)


'''
Great Idea Section:
    likelihood of different hand combos
    spreadsheet of hands & their "best equity likelihood" (aka chance that hands the best at the table) at different table sizes

'''

### FUNCTIONS ###

### SIMULATIONS & EXPERIMENTS ###

def hand_type_frequency():
    num_trails = 10000000
    num_seats = 6
    dealt_hands = []
    for t in range(num_trails):
        table = Table(num_seats)
        dealt_hands += [ph.hand_class for ph in table.player_hands]
    hand_tracker = {}
    for hand in dealt_hands:
        try:
            hand_tracker[hand] += 1
        except KeyError:
            hand_tracker.update({hand:1})
    card_val_ranks = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
    hand_tracker = dict(sorted(hand_tracker.items(),key = lambda x: (len(x[0]),card_val_ranks[x[0][0]],card_val_ranks[x[0][1]],x[0][1:])))
    hand_frequency_tracker = {}
    for hand in hand_tracker.items():
        hand_frequency_tracker.update({hand[0]:round((hand[1]/(num_trails*num_seats))*100,4)})
    df = pd.DataFrame()
    df['Hand Types'] = list(hand_frequency_tracker.keys())
    df['Hand Frequency'] = list(hand_frequency_tracker.values())
    df.to_csv(r'C:\Users\brend\Documents\Coding Projects\Poker\starting_hand_frequencies.csv')
    pocket_pair_chance = 0; offsuit_connector_chance = 0; other_hands_chance = 0
    suited_connector_chance = 0; suited_gapper_chance = 0; suited_doubleGapper_chance = 0 # cannot have two broadways!!!
    suited_broadway_chance = 0; offsuit_broadway_chance = 0; offsuit_ace_chance = 0; suited_ace_chance = 0; suited_king_chance = 0
    for i,row in df.iterrows():
        if len(row['Hand Types']) == 2:
            pocket_pair_chance += row['Hand Frequency']/100
        elif card_val_ranks[row['Hand Types'][0]] >= 10 and card_val_ranks[row['Hand Types'][1]] >= 10 and row['Hand Types'][2] == 's':
            suited_broadway_chance += row['Hand Frequency']/100
        elif card_val_ranks[row['Hand Types'][0]] >= 10 and card_val_ranks[row['Hand Types'][1]] >= 10 and row['Hand Types'][2] == 'o':
            offsuit_broadway_chance += row['Hand Frequency']/100
        elif card_val_ranks[row['Hand Types'][0]] == 14 and card_val_ranks[row['Hand Types'][1]] < 10 and row['Hand Types'][2] == 's':
            suited_ace_chance += row['Hand Frequency']/100
        elif card_val_ranks[row['Hand Types'][0]] == 14 and card_val_ranks[row['Hand Types'][1]] < 10 and row['Hand Types'][2] == 'o':
            offsuit_ace_chance += row['Hand Frequency']/100
        elif card_val_ranks[row['Hand Types'][0]] == 13 and card_val_ranks[row['Hand Types'][1]] < 10 and row['Hand Types'][2] == 's':
            suited_king_chance += row['Hand Frequency']/100
        elif abs(card_val_ranks[row['Hand Types'][0]] - card_val_ranks[row['Hand Types'][1]]) == 1 and row['Hand Types'][2] == 's':
            suited_connector_chance += row['Hand Frequency']/100
        elif abs(card_val_ranks[row['Hand Types'][0]] - card_val_ranks[row['Hand Types'][1]]) == 2 and row['Hand Types'][2] == 's':
            suited_gapper_chance += row['Hand Frequency']/100
        elif abs(card_val_ranks[row['Hand Types'][0]] - card_val_ranks[row['Hand Types'][1]]) == 3 and row['Hand Types'][2] == 's':
            suited_doubleGapper_chance += row['Hand Frequency']/100
        elif abs(card_val_ranks[row['Hand Types'][0]] - card_val_ranks[row['Hand Types'][1]]) == 1 and row['Hand Types'][2] == 'o':
            offsuit_connector_chance += row['Hand Frequency']/100
        else:
            other_hands_chance += row['Hand Frequency']/100
    with open(r'C:\Users\brend\Documents\Coding Projects\Poker\hand_type_frequency.txt',mode='w',encoding='utf-8') as stdOutput_file:
        print(f'Pocket Pair: {pocket_pair_chance*100:.2f}% ({int(round(1/pocket_pair_chance))}:1)', file = stdOutput_file)
        print(f'Suited Broadway: {suited_broadway_chance*100:.2f}% ({int(round(1/suited_broadway_chance))}:1)', file = stdOutput_file)
        print(f'Offsuit Broadway: {offsuit_broadway_chance*100:.2f}% ({int(round(1/offsuit_broadway_chance))}:1)', file = stdOutput_file)
        print(f'Suited Ace (Axs): {suited_ace_chance*100:.2f}% ({int(round(1/suited_ace_chance))}:1)', file = stdOutput_file)
        print(f'Offsuit Ace (Axo): {offsuit_ace_chance*100:.2f}% ({int(round(1/offsuit_ace_chance))}:1)', file = stdOutput_file)
        print(f'Suited King (Kxs): {suited_king_chance*100:.2f}% ({int(round(1/suited_king_chance))}:1)', file = stdOutput_file)
        print(f'Suited Connecter: {suited_connector_chance*100:.2f}% ({int(round(1/suited_connector_chance))}:1)', file = stdOutput_file)
        print(f'Offsuit Connecter: {offsuit_connector_chance*100:.2f}% ({int(round(1/offsuit_connector_chance))}:1)', file = stdOutput_file)
        print(f'Suited Gapper: {suited_gapper_chance*100:.2f}% ({int(round(1/suited_gapper_chance))}:1)', file = stdOutput_file)
        print(f'Suited Double-Gapper: {suited_doubleGapper_chance*100:.2f}% ({int(round(1/suited_doubleGapper_chance))}:1)', file = stdOutput_file)
        print(f'Other Hands: {other_hands_chance*100:.2f}% ({int(round(1/other_hands_chance))}:1)', file = stdOutput_file)
    return df

df_hand_freq = hand_type_frequency()




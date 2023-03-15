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
        playables_suits = [p.suit for p in playables]
        def eval_pairs_and_HC(playables,playables_num_vals):
            pairs = []
            count = dict(collections.Counter(playables_num_vals))
            for i,c in enumerate(count.items()):
                # print(c[1])
                if c[1] > 1:
                    pairs.append(c[0])
            pairs = sorted(pairs,reverse=True)[:2]
            if len(pairs) == 0:
                self.hand_val = 0
                i = 0
                while len(self.five_card_hand) < 5 and i < len(playables):
                    if playables[i] not in self.five_card_hand:
                        self.five_card_hand.append(playables[i])
                        self.card_vals_of_made_hand.append((playables[i].num_val))
                    i += 1
            elif len(pairs) > 0:
                self.hand_val = len(pairs)
                self.five_card_hand = [p for p in playables if p.num_val in pairs]
                self.card_vals_of_made_hand = [p.num_val for p in playables if p.num_val in pairs]
                i = 0
                while len(self.five_card_hand) < 5 and i < len(playables):
                    if playables[i] not in self.five_card_hand:
                        self.five_card_hand.append(playables[i])  
                    i += 1
            return True
        
        def eval_trips(playables,playables_num_vals):
            trips = []
            count = dict(collections.Counter(playables_num_vals))
            for i,c in enumerate(count.items()):
                # print(c[1])
                if c[1] > 2:
                    trips.append(c[0])
            if len(trips) == 0: return False
            elif len(trips) > 0:
                self.hand_val = 3
                self.five_card_hand = [p for p in playables if p.num_val in trips]
                self.card_vals_of_made_hand = [p.num_val for p in playables if p.num_val in trips]
                i = 0
                while len(self.five_card_hand) < 5 and i < len(playables):
                    if playables[i] not in self.five_card_hand:
                        self.five_card_hand.append(playables[i])  
                    i += 1
                return True
        def eval_straight(playables):
            i = 0
            straight_cards = [playables[i]]
            while len(straight_cards) < 5 and i+1 < len(playables):
                if playables[i].num_val - playables[i+1].num_val == 1:
                    straight_cards.append(playables[i+1])
                elif playables[i].num_val == playables[i+1].num_val:
                    pass
                else:
                    straight_cards = [playables[i+1]]
                i += 1
            if len(straight_cards) == 5:
                self.hand_val = 4
                self.five_card_hand = straight_cards
                self.card_vals_of_made_hand = [sc.num_val for sc in straight_cards]
                return True
            else:
                return False
        def eval_flush(playables,playables_suits):
            playables_suits = [p.suit for p in playables]
            count = dict(collections.Counter(playables_suits))
            flush_suit = ''
            for i,c in enumerate(count.items()):
                # print(c[1])
                if c[1] > 4:
                    flush_suit = c[0]
            if flush_suit == '': return False
            self.hand_val = 5
            for p in playables:
                if p.suit == flush_suit:
                    self.five_card_hand.append(p)
                    self.card_vals_of_made_hand.append(p.num_val)
            return True
        def eval_full_house(playables,playables_num_vals):
            trips = []; pairs= []
            count = dict(collections.Counter(playables_num_vals))
            for i,c in enumerate(count.items()):
                # print(c[1])
                if c[1] > 2 and len(trips) == 0:
                    trips.append(c[0])
                elif c[1] > 1:
                    pairs.append(c[0])
            if len(trips) == 0 or len(pairs) == 0: return False
            pairs = sorted(pairs,reverse=True)[:1]
            self.hand_val = 6
            self.five_card_hand = [p for p in playables if p.num_val in trips] + [p for p in playables if p.num_val in pairs]
            self.five_card_hand = self.five_card_hand[:5]
            self.card_vals_of_made_hand = [p.num_val for p in playables if p.num_val in trips] + [p.num_val for p in playables if p.num_val in pairs]
            self.card_vals_of_made_hand = self.card_vals_of_made_hand[:5]
            return True
        def eval_quads(playables,playables_num_vals):
            quads = []
            count = dict(collections.Counter(playables_num_vals))
            for i,c in enumerate(count.items()):
                # print(c[1])
                if c[1] > 3:
                    quads.append(c[0])
            if len(quads) == 0: return False
            elif len(quads) > 0:
                self.hand_val = 7
                self.five_card_hand = [p for p in playables if p.num_val in quads]
                self.card_vals_of_made_hand = [p.num_val for p in playables if p.num_val in quads]
                i = 0
                while len(self.five_card_hand) < 5 and i < len(playables):
                    if playables[i] not in self.five_card_hand:
                        self.five_card_hand.append(playables[i])  
                    i += 1
                return True            
        def eval_straight_flush(playables,playables_suits):
            playables_suits = [p.suit for p in playables]
            count = dict(collections.Counter(playables_suits))
            flush_suit = ''
            for i,c in enumerate(count.items()):
                # print(c[1])
                if c[1] > 4:
                    flush_suit = c[0]
            if flush_suit == '': return False
            sf_candidates = []
            for p in playables:
                if p.suit == flush_suit:
                    sf_candidates.append(p)
            sf_candidates = sorted(sf_candidates,key=lambda x: x.num_val,reverse = True)
            i = 0
            sf_cards = [sf_candidates[i]]
            while len(sf_cards) < 5 and i+1 < len(sf_candidates):
                if sf_candidates[i].num_val - sf_candidates[i+1].num_val == 1:
                    sf_cards.append(sf_candidates[i+1])
                elif sf_candidates[i].num_val == sf_candidates[i+1].num_val:
                    pass
                else:
                    sf_cards = [sf_candidates[i+1]]
                i += 1
            if len(sf_cards) == 5:
                self.hand_val = 8
                self.five_card_hand = sf_cards
                self.card_vals_of_made_hand = [sfc.num_val for sfc in sf_cards] 
                return True
            else:
                return False
        def eval_royal_flush(playables,playables_suits):
            count = dict(collections.Counter(playables_suits))
            flush_suit = ''
            for i,c in enumerate(count.items()):
                # print(c[1])
                if c[1] > 4:
                    flush_suit = c[0]
            if flush_suit == '': return False
            rf_candidates = []
            for p in playables:
                if p.suit == flush_suit:
                    rf_candidates.append(p)
            rf_candidates = sorted(rf_candidates,key=lambda x: x.num_val,reverse = True)
            if [rfc.num_val for rfc in rf_candidates] != [14,13,12,11,10]: return False
            i = 0
            rf_cards = [rf_candidates[i]]
            while len(rf_cards) < 5 and i+1 < len(rf_candidates):
                if rf_candidates[i].num_val - rf_candidates[i+1].num_val == 1:
                    rf_cards.append(rf_candidates[i+1])
                elif rf_candidates[i].num_val == rf_candidates[i+1].num_val:
                    pass
                else:
                    rf_cards = [rf_candidates[i+1]]
                i += 1
            if len(rf_cards) == 5:
                self.hand_val = 9
                self.five_card_hand = rf_cards
                self.card_vals_of_made_hand = [rfc.num_val for rfc in rf_cards] 
                return True
            else:
                return False                    
        hand_eval = False          
        if len(playables) == 2:
            hand_eval = eval_pairs_and_HC(playables,playables_num_vals)
        else:
            pass 
            # eval royal --> HC & pairs until binking a hand
            if max(dict(collections.Counter(playables_suits)).values()) > 4:
                hand_eval = eval_royal_flush(playables,playables_suits)
                if not hand_eval:
                    hand_eval = eval_straight_flush(playables,playables_suits)
            if not hand_eval and max(dict(collections.Counter(playables_num_vals)).values()) > 3:
                hand_eval = eval_quads(playables,playables_num_vals)
            if not hand_eval and max(dict(collections.Counter(playables_num_vals)).values()) > 2:
                hand_eval = eval_full_house(playables,playables_num_vals)
            if not hand_eval and max(dict(collections.Counter(playables_suits)).values()) > 4:
                hand_eval = eval_flush(playables,playables_suits)
            if not hand_eval:
                hand_eval = eval_straight(playables)
            if not hand_eval and max(dict(collections.Counter(playables_num_vals)).values()) > 2:
                hand_eval = eval_trips(playables,playables_num_vals)
            if not hand_eval:
                hand_eval = eval_pairs_and_HC(playables,playables_num_vals)
        # print(','.join([f'{fc.val}{fc.suit}' for fc in self.five_card_hand]))

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
    val = False
    while True:
        num_players = 9
        table = Table(num_players)
        print(table)
        table.deal_flop()
        print(table)
        table.deal_turn_or_river()
        print(table)
        table.deal_turn_or_river()
        print(table)
        # print(table.deck)
        for player_to_eval in list(range(0,num_players)):
        # player_to_eval = 1
            table.player_hands[player_to_eval].evaluate_hand(table.board)
            print(table.player_hands[player_to_eval])
            
            # print(table.player_hands[player_to_eval].card_vals_of_made_hand)
            # print([c.num_val for c in table.player_hands[player_to_eval].five_card_hand])
            print(table.player_hands[player_to_eval].hand_val)
            if table.player_hands[player_to_eval].hand_val == 9:
                val = True
        if val:
            break


'''
Great Idea Section:
    spreadsheet of hands & their "best equity likelihood" (aka chance that hands the best at the table) at different table sizes
    Absolute/raw value matrix of different hands without any play, simply as-is analysis
    Likelihood of made of hands across flop, turn and river

'''

### FUNCTIONS ###

### SIMULATIONS & EXPERIMENTS ###

def hand_type_frequency():
    card_val_ranks = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
    try:
        df = pd.read_csv(r'C:\Users\brend\Documents\Coding Projects\Poker\starting_hand_frequencies.csv')
    except FileNotFoundError:   
        num_trials = 10000000
        num_seats = 6
        dealt_hands = []
        for t in range(num_trials):
            table = Table(num_seats)
            dealt_hands += [ph.hand_class for ph in table.player_hands]
        hand_tracker = {}
        for hand in dealt_hands:
            try:
                hand_tracker[hand] += 1
            except KeyError:
                hand_tracker.update({hand:1})
        hand_tracker = dict(sorted(hand_tracker.items(),key = lambda x: (len(x[0]),card_val_ranks[x[0][0]],card_val_ranks[x[0][1]],x[0][1:])))
        hand_frequency_tracker = {}
        for hand in hand_tracker.items():
            hand_frequency_tracker.update({hand[0]:round((hand[1]/(num_trials*num_seats))*100,4)})
        df = pd.DataFrame()
        df['Hand Types'] = list(hand_frequency_tracker.keys())
        df['Hand Frequency (%)'] = list(hand_frequency_tracker.values())
        df.set_index('Hand Types',drop=True).to_csv(r'C:\Users\brend\Documents\Coding Projects\Poker\starting_hand_frequencies.csv')
    pocket_pair_chance = 0; pocket_broadway = 0; offsuit_connector_chance = 0; other_hands_chance = 0
    suited_connector_chance = 0; suited_gapper_chance = 0; suited_doubleGapper_chance = 0 # cannot have two broadways!!!
    suited_broadway_chance = 0; offsuit_broadway_chance = 0; offsuit_ace_chance = 0; suited_ace_chance = 0; suited_king_chance = 0
    for i,row in df.iterrows():
        if len(row['Hand Types']) == 2:
            if card_val_ranks[row['Hand Types'][0]] >= 10:
                pocket_broadway += row['Hand Frequency']/100
            else:
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
        print(f'Pocket Broadway: {pocket_broadway*100:.2f}% ({int(round(1/pocket_broadway))}:1)', file = stdOutput_file)        
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

# df_hand_freq = hand_type_frequency()

def flop_texture_analysis():
    card_val_ranks = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
    card_class_ranks = {'A':4,'H':3,'M':2,'L':1}
    suit_class_ranks = {'Monotone':3,'Two-Tone':2,'Rainbow':1}
    pairedness_ranks = {'Trips':3,'Paired':2,'Unpaired':1}
    connected_ranks = {'N/A':5,'Fully Connected':4,'Single Gap':3,'Two Gap':2,'Partially Connected':1,'Disconnected':0}
    try:
        df = pd.read_csv(r'C:\Users\brend\Documents\Coding Projects\Poker\flop_texture_frequencies.csv')
        with open(r'C:\Users\brend\Documents\Coding Projects\Poker\flop_texture_frequencies.txt',mode='r',encoding='utf-8') as file:
            lines = [l.rstrip() for l in file.readlines()]
            for l in lines:
                print(l)
    except FileNotFoundError:
        num_seats = 6
        num_trials = 10000000
        monotone = 0; two_tone = 0; rainbow = 0
        unpaired = 0; paired = 0; trips = 0
        board_card_classes = []
        fully_connected = 0; single_gap = 0; two_gap = 0; partially_connected = 0; disconnected = 0; connectedness_not_applicable = 0
        # fully = 0 gaps (ex. 678) | 3 possible made straights & 2 OESDs
        # single gap = 1 gap (ex. J98) | 2 possible made straights w/ 1 OESD
        # two_gap = 2 gaps (ex. T76) | 1 possible made straight w/ 2 OESDs
        # partially 2 < gaps < 5 (ex. J96, J95) or 2 connected w/ 1 disconnected (ex. T92) | 1-3 OESDs
        # disconnected > 5 gaps and no connected  (ex. K93)
        meta_board_list = []
        for t in range(num_trials):
            meta_board = ['','','','']
            table = Table(num_seats)
            table.deal_flop()
            suits = list(set([c.suit for c in table.board])) 
            if len(suits) == 1:
                monotone += 1; meta_board[1] = 'Monotone'
            elif len(suits) == 2:
                two_tone += 1; meta_board[1] = 'Two-Tone'
            elif len(suits) == 3:
                rainbow += 1; meta_board[1] = 'Rainbow'
            num_vals = sorted([card_val_ranks[c.val] for c in table.board],reverse=True)
            if len(set(num_vals)) == 3:
                unpaired += 1; meta_board[2] = 'Unpaired'
                if 14 not in num_vals:
                    gap_list = [num_vals[0] - 1 - num_vals[1], num_vals[1] - 1 - num_vals[2]]
                else:
                    gap_list = [num_vals[0] - 1 - num_vals[1], num_vals[1] - 1 - num_vals[2]]
                    wheel_num_vals = sorted([nv if nv != 14 else 1 for nv in num_vals],reverse=True)
                    wheel_list = [wheel_num_vals[0] - 1 - wheel_num_vals[1], wheel_num_vals[1] - 1 - wheel_num_vals[2]]
                    if sum(wheel_list) < sum(gap_list):
                        gap_list = wheel_list
                if sum(gap_list) == 0:
                    fully_connected += 1; meta_board[3] = 'Fully Connected'
                elif sum(gap_list) == 1:
                    single_gap += 1; meta_board[3] = 'Single Gap'
                elif sum(gap_list) == 2:
                    two_gap += 1; meta_board[3] = 'Two Gap'
                elif sum(gap_list) < 5 or gap_list.count(0) > 0:
                    partially_connected += 1; meta_board[3] = 'Partially Connected'
                elif sum(gap_list) >= 5:
                    disconnected += 1; meta_board[3] = 'Disconnected'            
            elif len(set(num_vals)) == 2:
                paired += 1; meta_board[2] = 'Paired'; meta_board[3] = 'N/A'; connectedness_not_applicable += 1
            elif len(set(num_vals)) == 1:
                trips += 1; meta_board[2] = 'Trips'; meta_board[3] = 'N/A'; connectedness_not_applicable += 1
            card_classes = []
            for nv in num_vals:
                if nv == 14:
                    card_classes.append('A'); continue
                elif 10 <= nv <= 13:
                    card_classes.append('H'); continue           
                elif 6 <= nv <= 9:
                    card_classes.append('M'); continue           
                elif 2 <= nv <= 5:
                    card_classes.append('L'); continue
            card_classes = ''.join(sorted(card_classes,key = lambda x: card_class_ranks[x],reverse=True))
            board_card_classes.append(card_classes)
            meta_board[0] = card_classes
            meta_board_list.append(':'.join(meta_board))
        
        
        board_class_tracker = dict(sorted(dict(collections.Counter(board_card_classes)).items(),key = lambda x: (card_class_ranks[x[0][0]],card_class_ranks[x[0][1]],card_class_ranks[x[0][2]]),reverse=True))
        meta_board_tracker = dict(sorted(dict(collections.Counter(meta_board_list)).items(),key = lambda x: (card_class_ranks[x[0].split(':')[0][0]],card_class_ranks[x[0].split(':')[0][1]],card_class_ranks[x[0].split(':')[0][2]],suit_class_ranks[x[0].split(':')[1]],pairedness_ranks[x[0].split(':')[2]],connected_ranks[x[0].split(':')[3]]),reverse=True))
        board_class_frequency_tracker = {}
        for board_class in board_class_tracker.items():
            board_class_frequency_tracker.update({board_class[0]:round((board_class[1]/(num_trials))*100,4)})
        meta_board_frequency_tracker = {}
        for meta_board in meta_board_tracker.items():
            meta_board_frequency_tracker.update({meta_board[0]:round((meta_board[1]/(num_trials))*100,4)})
        df_data = []; df_columns = ['Board','Suit Texture','Pairedness','Connectedness','Percentage (%)']
        for item in meta_board_frequency_tracker.items():
            df_data.append([item[0].split(':')[0],item[0].split(':')[1],item[0].split(':')[2],item[0].split(':')[3],item[1]])
        df = pd.DataFrame(df_data,columns=df_columns)
        df.set_index('Board',drop=True).to_csv(r'C:\Users\brend\Documents\Coding Projects\Poker\flop_texture_frequencies.csv')
        with open(r'C:\Users\brend\Documents\Coding Projects\Poker\flop_texture_frequencies.txt',mode='w',encoding='utf-8') as stdOutput_file:
            print('Frequency of Flop Characteristics:', file = stdOutput_file)
            print(f'\n**Suit Texture**\nMonotone: {(monotone/num_trials)*100:.2f}%\nTwo-Tone: {(two_tone/num_trials)*100:.2f}%\nRainbow: {(rainbow/num_trials)*100:.2f}%', file = stdOutput_file)
            print(f'\n**Pairedness**\nTrips: {(trips/num_trials)*100:.2f}%\nPaired Board: {(paired/num_trials)*100:.2f}%\nUnpaired Board: {(unpaired/num_trials)*100:.2f}%', file = stdOutput_file)
            print(f'\n**Connectedness**\nFully Connected: {(fully_connected/num_trials)*100:.2f}%\nSingle Gap: {(single_gap/num_trials)*100:.2f}%\nTwo Gaps: {(two_gap/num_trials)*100:.2f}%\nPartially Connected: {(partially_connected/num_trials)*100:.2f}%\nDisconnected: {(disconnected/num_trials)*100:.2f}%\nN/A (Paired or Trips Board): {(connectedness_not_applicable/num_trials)*100:.2f}%', file = stdOutput_file)
            board_string = '\n**Board Combos**'
            for item in board_class_tracker.items():
                board_string += f'\n{item[0]}: {(item[1]/num_trials)*100:.2f}%'
            print(board_string, file = stdOutput_file)
    return df

# df = flop_texture_analysis()
    
    
    
    
    


import random

def calculate_score(hand):
    score = 0
    aces = 0
    for card in hand:
        if card in ['J', 'Q', 'K']:
            score += 10
        elif card == 'A':
            aces += 1
            score += 11
        else:
            score += int(card)
        
    while score > 21 and aces:
        score -= 10
        aces -= 1
    
    return score

def shuffle_deck():
    deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
    random.shuffle(deck)
    return deck
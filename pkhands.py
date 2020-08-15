
import pktypes
from pktypes import *
import random
from collections import Counter

## Use this convention

PAIRSCORE=100
TWOPAIRSCORE=200
TRIPSCORE=300
STRAIGHTSCORE=400
FLUSHSCORE=500
FULLSCORE=600
QUADSCORE=700
STRFLSCORE=800

def checkStraight(vals):
    hand = set(vals)
    if 14 in hand:
        hand.add(1) # Account for Ace being a low card
    for low in range(10,0,-1):
        straight = set(range(low, low+5))
        if len(straight-hand) < 1:
            isStraight = True
            straightval = list(sorted(straight))
            highcard = low+4
            score = STRAIGHTSCORE+int(highcard)
            return (True, straightval, score, "Straight")
    return (False, None, 0, None)

def checkFlush(vals, suits):
    suit_dict = Counter(suits)
    if 5 in suit_dict.values() or 6 in suit_dict.values() or 7 in suit_dict.values():
        flushvals=[]
        for s, cnt in suit_dict.items():
            if cnt>4:
                flush_suit = s
        for idx in range(len(suits)):
            if suits[idx] == flush_suit:
                flushvals.append(vals[idx])
        flushvals = list(sorted(flushvals))
        highcard = flushvals[-1]
        score=FLUSHSCORE+highcard       
        return (True, flushvals, score, "Flush")
    return (False, None, 0, "Flush")

#Call only if both straight and flush
def checkStraightFlush(flushvals):
    if 14 in flushvals:
        flushvals.append(1) # Treat Ace as a low card as well
    flushset = set(flushvals)
    for low in range(10,0,-1):
        straight = set(range(low, low+5))
        if len(straight-flushset) < 1:
            flushvals = list(sorted(flushvals))
            highcard = low+4
            score = STRFLSCORE+int(highcard)
            return (True, flushvals, score, "Straight Flush")
    return (False, None, 0, "Straight Flush")
        
def checkQuads(vals):
    for card, count in Counter(vals).items():
        if count == 4:
            return (True, card, QUADSCORE+int(card), "Quads")
    return (False, None, 0, "Quads")

def checkTrips(vals):
    val_dict = Counter(vals)
    trips = []
    if 3 in val_dict.values():
        hightrip = 0
        for card, count in val_dict.items():
            if count == 3:
                trips.append(card)
                if card > hightrip: hightrip = card
        return (True, trips, TRIPSCORE+hightrip, "Trips")
    return (False, trips, 0, "Trips")

def checkPairs(vals):
    val_dict = Counter(vals)
    if 2 in val_dict.values():
        score = PAIRSCORE
        pairs = []
        highpair = 0
        for card, count in val_dict.items():
            if count == 2:
                pairs.append(card)
                if card > highpair: highpair = card
        if len(pairs)>1:
            score = TWOPAIRSCORE
        return (True, pairs, score+highpair, "Pair_s")
    return (False, None, 0, "Pair_s")


def getHand(allCards):
    
    assert len(allCards)==7
    
    #isHandType = (True/False, vals of hand, hand score, str(name of hand))
    values = [v.value for v in allCards]
    suits = [v.suit for v in allCards]
    ranks = [v.rank for v in allCards]

    isFlush = isStraight = isQuads = isFull = isTrips = isTwoPair = isPair = False

    isStraight = checkStraight(values)
    isFlush = checkFlush(values, suits)

    if isStraight[0] and isFlush[0]:
        isStraightFlush = checkStraightFlush(isFlush[1])
        if isStraightFlush[0]:
            return isStraightFlush 

    isQuads = checkQuads(values)
    if isQuads[0]:
        return isQuads      

    if isFlush[0]:
        return isFlush
    
    if isStraight[0]:
        return isStraight
    
    isTrips = checkTrips(values)
    isPairs = checkPairs(values)

    if len(isTrips[1])>1:  # Player has 2 trips, so basically a full house
        tripcards = sorted(isTrips[1])
        trip = tripcards[1]
        pair = tripcards[0]
        isFullHouse = (True, (trip, pair), FULLSCORE+trip+(pair/10), "Full House")
        return isFullHouse

    if isTrips[0] and isPairs[0]:
        trip = isTrips[1][0]
        paircards = sorted(isPairs[1])
        pair = paircards[-1]
        isFullHouse = (True, (trip, pair), FULLSCORE+trip+(pair/10), "Full House")
        return isFullHouse

    if isTrips[0]:
        return isTrips

    if isPairs[0]:
        return isPairs

    else:
        highcard = sorted(values)[-1]
        isHighCard = (True, highcard, highcard, "High card")
        return isHighCard



import numpy as np
import random
import mtgtools as mtg
from mtgtools.MtgDB import MtgDB
from mtgtools.PCardList import PCardList
import argparse

# -----------
# Parameters
# -----------

COMMANDER = "Vren, the Relentless"
MUL_MAX = 5
LAND_MIN = 3
DEBUG = True

# ----------
# Functions
# ----------

# Library and card draw logic

def shuffle_library(library):
    if DEBUG:
        print("Shuffling library")
    new_library = library
    random.shuffle(new_library)
    return new_library

def draw_hand(library):
    if DEBUG:
        print("Drawing first hand")
    hand = PCardList()
    for _ in range(7):
        hand += library[0]
        library.pop(0)
    return library, hand

def mulligan(library, hand, n_mul):
    if DEBUG:
        print(f"Performing mulligan number {n_mul}")

    library += hand
    library = shuffle_library(deck)
    hand = PCardList()
    # Draw top 7 cards to hand
    for _ in range(7):
        hand += library[0]
        library.pop(0)

    # Discard n_mul -1 cards from hand and put on the bottom of library
    discards = PCardList()
    for i in range(n_mul):
        hand, discard = discard_card(hand, starting=True)
        library.append(discard)
    return library, hand

def pop_commander(commander, deck):
    if DEBUG:
        print(f"Popping out {commander}")

    cmdr = deck.where(name=commander)
    library = deck - cmdr
    return library, cmdr

def draw_starting_hand(library, mul_max, land_min):
    library, hand = draw_hand(library)
    n_mul = 0
    to_mulligan = to_mulligan_or_not_to_mulligan(hand, n_mul, mul_max, land_min)
    while to_mulligan:
        library, hand = mulligan(library, hand, n_mul)
        n_mul += 1
        to_mulligan = to_mulligan_or_not_to_mulligan(hand, n_mul, mul_max, land_min)
    return library, hand


# Hand logic

def to_mulligan_or_not_to_mulligan(hand, n_mul, mul_max, land_min):
    # TODO: Determine whether to mulligan
    # for now determine based on number of lands
    if n_mul >= mul_max:
        return False
    n_land = sum(["Land" in card.type_line for card in hand])
    if DEBUG:
        print(f"{n_land} Land in hand")
    if n_land >= land_min:
        return False
    return True

# General logic for discarding a card
def discard_card(hand, starting=False):
    # TODO: look at the hand and determine which discard function to use
    # for now just use by mana value
    return discard_card_by_mana(hand)

# Discard a card from a hand based on mana value
def discard_card_by_mana(hand):
    # get index of the card with the highest mana cost
    idx = np.argmax([card.cmc for card in hand])
    if DEBUG:
        print(f"Discarding card {idx}")
    discard = hand[idx]
    hand.pop(idx)
    return hand, discard

# Discard a card based on preference
def discard_card_by_preference(hand, preferences):
    return Null

# Discard a card based on number of lands
def discard_card_by_lands(hand):
    return Null

# Arguments
parser = argparse.ArgumentParser("Mana Ramp Simulation")
parser.add_argument("--update", help="Updates the local MTG card database from Scryfall", action="store_true")
args = parser.parse_args()

mtg_db = MtgDB('/home/c5046848/lab/fun/mtg/my_db.fs')

if args.update:
    mtg_db.scryfall_bulk_update()
    mtg_db.mtgio_update()

# Get all cards in MTG as given by Scryfall

cards = mtg_db.root.scryfall_cards

# ------------------
# Single Game Logic
# ------------------

deck_string = open("/home/c5046848/lab/fun/mtg/Vren.txt").read()
deck = cards.from_str(deck_string)

library, cmdr = pop_commander(COMMANDER, deck)
library = shuffle_library(library)
library, hand = draw_starting_hand(library, MUL_MAX, LAND_MIN)

print(hand)

# Take turns

# Play land, play mana ramp if possible
# Repeat

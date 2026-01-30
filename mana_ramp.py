import numpy as np
import random
import mtgtools as mtg
from mtgtools.MtgDB import MtgDB
from mtgtools.PCardList import PCardList
import argparse

# ---------------
# Parameters
# ---------------


COMMANDER = "Vren, the Relentless"

CONDITIONS = {
    "PLAY_LEGENDARY_LAND_MAX": 3,
    "MUL_MAX": 5,
    "LAND_MIN": 3
}
NUM_TURNS = 5

DEBUG = True

# -------------
# Functions
# -------------

# ----------------------------
# Library and card draw logic

# Shuffle library
def shuffle_library(library):
    if DEBUG:
        print("Shuffling library")
    new_library = library
    random.shuffle(new_library)
    return new_library

# Pop out commander from deck
def pop_commander(commander, deck):
    if DEBUG:
        print(f"Popping out {commander}")

    cmdr = deck.where(name=commander)
    library = deck - cmdr
    return library, cmdr


# Draw starting hand with mulligan logic
def draw_starting_hand(library, mul_max, land_min):
    n_mul = 0
    library, hand = draw_hand(library)
    to_mulligan = to_mulligan_or_not_to_mulligan(hand, n_mul, mul_max, land_min)
    while to_mulligan:
        n_mul += 1
        library, hand = mulligan(library, hand, n_mul)
        to_mulligan = to_mulligan_or_not_to_mulligan(hand, n_mul, mul_max, land_min)
    return library, hand

# Draw 7 cards to hand
def draw_hand(library):
    if DEBUG:
        print("Drawing first hand")
    hand = PCardList()
    for _ in range(7):
        hand += library.pop(0)
    return library, hand


def draw_card(library):
    if DEBUG:
        print("Drawing a card")
    drawn_card = library.pop(0)
    return library, drawn_card


# Mulligan logic
def mulligan(library, hand, n_mul):
    if DEBUG:
        print(f"Performing mulligan number {n_mul}")

    library += hand
    library = shuffle_library(deck)
    hand = PCardList()
    # Draw top 7 cards to hand
    for _ in range(7):
        hand += library.pop(0)

    # Discard n_mul -1 cards from hand and put on the bottom of library
    discards = PCardList()
    for i in range(n_mul - 1):
        hand, discard = discard_card(hand, starting=True)
        library.append(discard)
    return library, hand

# Determine whether to mulligan or not
def to_mulligan_or_not_to_mulligan(hand, n_mul, mul_max, land_min):
    # TODO: Determine whether to mulligan

    # Simple toy logic: mulligan if too few lands or too many muls

    # If we've already mulliganed the max number of times, don't mulligan again
    if n_mul >= mul_max:
        return False
    
    # If we have enough lands, don't mulligan
    n_land = sum(["Land" in card.type_line for card in hand])
    if DEBUG:
        print(f"{n_land} Land in hand")
    if n_land >= land_min:
        return False
    
    # Otherwise, mulligan
    return True

# General logic for discarding a card
def discard_card(hand, starting=False):
    # TODO: look at the hand and determine which discard function to use
    # Toy logic: discard highest mana cost card
    return discard_card_by_mana(hand)

# Discard a card from a hand based on mana value
def discard_card_by_mana(hand):
    # get index of the card with the highest mana cost
    idx = int(np.argmax([card.cmc for card in hand]))
    # if DEBUG:
    #     print(f"Discarding card {idx}")
    discard = hand[idx]
    hand.pop(idx)
    return hand, discard

# Discard a card based on preference
def discard_card_by_preference(hand, preferences):
    return None

# Discard a card based on number of lands
def discard_card_by_lands(hand):
    return None


# ----------------------------
# Game state and turn logic

def initial_game_state(library, hand, cmdr):
    graveyard = PCardList()
    exile = PCardList()

    battlefield = {
        "creatures": PCardList(),
        "artifacts": PCardList(),
        "enchantments": PCardList(),
        "planeswalkers": PCardList(),
        "lands": PCardList(),
        "tapped_cards": PCardList(),
    }

    game_state = {
        "library": library,
        "hand": hand,
        "battlefield": battlefield,
        "graveyard": graveyard,
        "exile": exile,
        "commander": cmdr,
        "turn": 0,
    }
    return game_state

def main_phase(game_state, conditions=None):
    hand = game_state["hand"]

    # Main phase actions go here

    # If Land in type_line but not "Basic Land", attempt to play legendary land
    if any(s == "Land" for s in [card.type_line for card in hand]):
        if DEBUG:
            print("Attempting to play a legendary land")
        game_state = attempt_cast_legendary_land(game_state, conditions)
    elif "Land" in [card.type_line for card in hand]:
        if DEBUG:
            print("Attempting to play a land")
        game_state = attempt_cast_land(game_state, conditions)
    else:
        if DEBUG:
            print("No lands to play this turn")

    game_state = attempt_tap_legendary_land(game_state, conditions)
    
    game_state = attempt_play_ramp_card(game_state, conditions)

    # Play creature logic
    game_state = attempt_play_creature(game_state, conditions)

    # Play artifact and enchantment logic
    game_state = attempt_play_artifact_enchantment(game_state, conditions)

    return game_state

def attempt_cast_legendary_land(game_state, conditions):
    play_legendary_land_max = conditions["PLAY_LEGENDARY_LAND_MAX"]
    hand = game_state["hand"]
    turn = game_state["turn"]

    # If we are past the max turn to play legendary land, check to see if there are basic lands first
    if turn >= play_legendary_land_max:
        if DEBUG:
            print("Past turn limit for playing legendary lands, checking for basic lands")
        basic_lands = [card for card in hand if "Basic Land" in card.type_line]
        if len(basic_lands) > 0:
            return attempt_cast_land(game_state, conditions)
        
    # If we are within the turn limit, or if no basic lands are available
    else:
        if DEBUG:
            print("Within turn limit for playing legendary lands, or no basic lands available")
        # Get list of legendary lands in hand
        legendary_lands = [card for card in hand if "Land" == card.type_line]

        # If there are more than 1 legendary lands in hand we must choose which one
        # Toy logic: pick randomly
        chosen_land = random.choice(legendary_lands)

        # Add the chosen legendary land to the battlefield
        game_state["battlefield"]["lands"].append(chosen_land)
        game_state["hand"].remove(chosen_land)

        return game_state

def attempt_cast_land(game_state, conditions):
    hand = game_state["hand"]
    
    # If there is only one land in hand, play it
    lands_in_hand = [card for card in hand if "Land" in card.type_line]
    if DEBUG:
        print(f"Lands in hand: {lands_in_hand}")

    if len(lands_in_hand) == 1:
        if DEBUG:
            print("Only one land in hand, playing it")
        chosen_land = lands_in_hand[0]
        game_state["battlefield"]["lands"].append(chosen_land)
        game_state["hand"].remove(chosen_land)
        return game_state

    # If there are multiple lands in hand choose which one
    # If they are of the same type, pick randomly
    
    # Logic, get last word in type line for each land
    land_types = [card.type_line.split()[-1] for card in lands_in_hand]
    if len(set(land_types)) == 1:
        if DEBUG:
            print("All lands in hand are of the same type, picking randomly")
        chosen_land = random.choice(lands_in_hand)
        game_state["battlefield"]["lands"].append(chosen_land)
        game_state["hand"].remove(chosen_land)
        return game_state
    else:
        if DEBUG:
            print("Lands in hand are of different types, picking based on mana needs")
        # Look at the mana colours of other cards in hand
        all_costs = "".join([card.mana_cost for card in hand if "Land" not in card.type_line]).replace("{", "").replace("}", "")
        # Get colour with greatest frequency
        mana_colours = {"U": 0, "B": 0, "R": 0, "G": 0, "W": 0 }
        for letter in all_costs:
            if letter not in mana_colours:
                mana_colours[letter] = 0
            mana_colours[letter] += 1
        # Get the colour with the highest count
        # If there are no colours needed, a tie, or the land doesn't produce any of the needed colours, pick randomly
        if all(value == 0 for value in mana_colours.values()) or len(set(mana_colours.values())) == 1:
            if DEBUG:
                print("No preferred mana colour, picking land randomly")
            chosen_land = random.choice(lands_in_hand)
            game_state["battlefield"]["lands"].append(chosen_land)
            game_state["hand"].remove(chosen_land)
            return game_state
        else:
            if DEBUG:
                print("Choosing land based on preferred mana colour")
            preferred_colour = max(mana_colours, key=mana_colours.get)
            if DEBUG:
                print(f"Preferred colour is {preferred_colour}")
            # Pick the first land that produces the preferred colour
            for card in lands_in_hand:
                if preferred_colour in card.color_identity:
                    chosen_land = card
                    game_state["battlefield"]["lands"].append(chosen_land)
                    game_state["hand"].remove(chosen_land)
                    return game_state
        
        return game_state # failsafe

def attempt_tap_legendary_land(game_state, conditions):
    # This will be a bit complicated since we need to have logic for the oracle text
    # for now, we will just leave the game state unchanged
    return game_state

def attempt_play_ramp_card(game_state, conditions):
    # first we need a list of all ramp cards in the library, then check if there are any in hand

    # then we need to check if we have enough mana to play the ramp card

    # if we can play the ramp card, we need to choose which one to play

    # then we play it
    return game_state

def attempt_play_creature(game_state, conditions):
    # get list of creatures in hand

    # check if any are legendary

    # play legendary creature if possible

    # otherwise play the cheapest creature possible
    return game_state

def attempt_play_artifact_enchantment(game_state, conditions):
    # Leave the game state unchanged for now
    return game_state


# ----------------------------
# Diagnostics and Helpers

def get_total_mana_potential(card_list):
    return None

def get_land_count(card_list):
    return None

def get_total_mana_available(game_state):
    return None

# ----------------------------
# Main script

# Arguments
parser = argparse.ArgumentParser("Mana Ramp Simulation")
parser.add_argument("--update", help="Updates the local MTG card database from Scryfall", action="store_true")
args = parser.parse_args()

mtg_db = MtgDB('/home/c5046848/lab/fun/mtg/my_db.fs')
cards = mtg_db.root.scryfall_cards


if args.update:
    mtg_db.scryfall_bulk_update()
    mtg_db.mtgio_update()

# Get all cards in MTG as given by Scryfall

# ------------------
# Single Game Logic
# ------------------

deck_string = open("/home/c5046848/lab/fun/mtg/Vren.txt").read()
deck = cards.from_str(deck_string)

library, cmdr = pop_commander(COMMANDER, deck)
library = shuffle_library(library)
library, hand = draw_starting_hand(library, CONDITIONS["MUL_MAX"], CONDITIONS["LAND_MIN"])

print("Starting hand:")
print(hand)
print("\n")

game_state = initial_game_state(library, hand, cmdr)
print("Battlefield:")
print(game_state["battlefield"])
print("\n")

for _ in range(NUM_TURNS):
    game_state["turn"] += 1
    # draw a card from library at start of turn
    print("Drawing card for turn", game_state["turn"])
    library, drawn_card = draw_card(library)
    print("Drew card:")
    print(drawn_card)
    game_state["hand"].append(drawn_card)
    game_state = main_phase(game_state, CONDITIONS)
    print("Battlefield:")
    print(game_state["battlefield"])
    print("Hand:")
    print(game_state["hand"])
    print("\n")

    # End step
    # If there are more than 7 cards in hand, discard down to 7
    while len(game_state["hand"]) > 7:
        game_state["hand"], discard = discard_card(game_state["hand"])
        game_state["graveyard"].append(discard)
        if DEBUG:
            print(f"Discarded card to graveyard: {discard}")
        print("Graveyard:")
        print(game_state["graveyard"])
    print("\n")


# Take turns

# Play land, play mana ramp if possible
# Repeat

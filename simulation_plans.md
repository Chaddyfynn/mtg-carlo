# Simulation Plans
Using mtgtools with my python 3.11 environment (conda activate 3.11), how much cool stuff can we do?

## Mana Ramp Test
A simple starting exercise. 

### Simple Ramp (No other turn 2 or 3 plays)
Create a deck, then create a starting hand.
Mulligan until we get M lands or have N cards.
If we have M-m lands but m ramp cards with converted mana cost M, keep the hand.

Assume noninteraction
Play a land -> skip other turns -> play another land (play ramp if possible) -> so on
Graph total mana, mana of each colour, over time

For nonbasic lands, if we get one, try
	 1) not sac'ing the land
	 2) sac the land after n turns
	 3) sac the land immediately

When searching for a new land, try different options
	1) Random nonbasic
	2) Random dual/basic dual
	3) Random basic
	4) Basic of mana type least acquired

Then perform a Monte Carlo simulation for each set of rules with, say 10^5 samples, and graph the envelopes of the mana curves

## Rat Scaling

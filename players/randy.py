# randy.py
# AI player for Hand of the King that makes all moves randomly.

from hotk import getvalidmoves
import pdb
import random


def get_computer_move(state, whichplayer):
    '''Randomly select a move from the set of valid moves.'''
    moves = getvalidmoves(state)
    return random.choice(moves)
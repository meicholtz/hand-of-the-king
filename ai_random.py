# ai_random.py
# Random AI player for A Game of Thrones: Hand of the King

from hand_of_the_king import getvalidmoves
import pdb
import random


def get_computer_move(board, cards, banners, turn):
    '''Randomly select a move from the set of valid moves.'''
    moves = getvalidmoves(board)
    return random.choice(moves)
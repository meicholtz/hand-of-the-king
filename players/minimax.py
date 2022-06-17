# minimax.py
# AI player for Hand of the King initially developed by Matthew Eicholtz.
# This player is equipped to apply minimax for making decision after a specified
# number of moves. In the early game, it moves randomly.
#
# No pruning, no depth-limiting heuristic, no nonsense. :)

from copy import deepcopy
from hotk import getvalidmoves, makemove
import math
import pdb
import random

WIN = 1
LOSS = -1


def get_computer_move(state, whichplayer):
    '''Returns the best move for the current player based on game state (board, cards, banners).'''
    if state['moves'] <= 24:  # move randomly
        moves = getvalidmoves(state)
        return random.choice(moves)
    else:  # use minimax
        print(f'Player {whichplayer} is using minimax...', end='')
        return minimax(state, whichplayer)


def minimax(state, player):
    '''Runs minimax to find the optimal move for the current player.'''
    # Loop through all possible moves, finding one with best (maximum) utility
    moves = getvalidmoves(state)
    bestmove = moves[0]  # default best move is first move
    bestutil = minval(state, player, bestmove)
    for move in moves[1:]:
        util = minval(state, player, move)
        if util > bestutil:
            bestmove = move
            bestutil = util
    print(f'utility={bestutil}')
    return bestmove


def minval(state, maxplayer, maxmove):
    '''Returns the minimum utility available after allowing the maxplayer (us) to make a move.'''
    # Copy all mutable objects
    statecopy = deepcopy(state)

    # Simulate move of maxplayer (i.e. us)
    makemove(statecopy, maxplayer, maxmove)
    minplayer = abs(1 - maxplayer)

    # Check if this move ends the game
    moves = getvalidmoves(statecopy)
    if len(moves) == 0:
        return utility(statecopy, maxplayer, minplayer)

    # If game is not over, find minimum value from possible moves
    value = math.inf
    for minmove in moves:
        value = min(value, maxval(statecopy, minplayer, minmove))
    return value


def maxval(state, minplayer, minmove):
    '''Returns the maximum utility available after allowing the minplayer (our opponent) to make a move.'''
    # Copy all mutable objects
    statecopy = deepcopy(state)

    # Simulate move of minplayer (i.e. our opponent)
    makemove(statecopy, minplayer, minmove)
    maxplayer = abs(1 - minplayer)

    # Check if this move ends the game
    moves = getvalidmoves(statecopy)
    if len(moves) == 0:
        return utility(statecopy, maxplayer, minplayer)

    # If game is not over, find minimum value from possible moves
    value = -math.inf
    for maxmove in moves:
        value = max(value, minval(statecopy, maxplayer, maxmove))
    return value


def utility(state, player, opponent):
    '''Returns utility based on who wins the game (e.g. has the most banners).'''
    banners = state['banners']
    us = sum(banners[player])
    them = sum(banners[opponent])
    if us > them:  # win
        return WIN
    elif them > us:  # loss
        return LOSS
    else:  # if there is a tie, then the owner of the largest house wins
        return WIN if banners[player][::-1].index(1) < banners[opponent][::-1].index(1) else LOSS


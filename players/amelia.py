# amelia.py
# AI player for Hand of the King initially developed by Amelia Reiss during CSC 3510 (Spring 2022)
# and subsequently modified by Matthew Eicholtz. This player uses minimax with alpha-beta pruning
# coupled with depth-limited search and a custom heuristic.
#
# The heuristic takes into account three variables based on the current game state:
#   1) card count: +1 for every card taken, -1 for every card opponent has taken
#   2) banner count: +3 for every banner taken, -3 for every banner opponent has taken
#   3) secure banners: +10 for every color that the player has > half the cards in that color,
#      -10 for every color secured by the opponent; e.g. if a player owns 4 or more of the black
#      cards (7 possible), then it is a guaranteed banner and cannot be stolen

from hand_of_the_king import getvalidmoves
import math
import copy
import pdb


def get_computer_move(board, cards, banners, turn):
    '''Returns the best move for given player, based on current game state.'''
    # Copy all mutable objects
    boardCopy = copy.deepcopy(board)
    bannersCopy = copy.deepcopy(banners)
    cardsCopy = copy.deepcopy(cards)

    # Setup minimax
    DLSmax = 7  # limited depth (higher numbers mean go deeper, but take longer)
    moves = getvalidmoves(boardCopy)
    bestMove = moves[0]  # default best move is first move
    utility = minval(boardCopy, turn, bestMove, bannersCopy, cardsCopy, -math.inf, math.inf, DLSmax)

    # Loop through all possible moves, finding one with best utility
    for move in moves[1:]:
        util = minval(boardCopy, turn, move, bannersCopy, cardsCopy, -math.inf, math.inf, DLSmax)
        if util > utility:
            bestMove = move
            utility = util

    return bestMove


def minval(board, player, move, banners, cards, a, b, DLSmax):
    '''Returns the minimum utility available from a move on the board.'''
    # Copy all mutable objects
    boardCopy = copy.deepcopy(board)
    bannersCopy = copy.deepcopy(banners)
    cardsCopy = copy.deepcopy(cards)

    # Decrease depth
    DLSmax -= 1

    # Simulate move of current player
    simulate(boardCopy, player, move, bannersCopy, cardsCopy)
    nextPlayer = abs(1 - player)

    # Check if this move ends the game or the search
    moves = getvalidmoves(boardCopy)
    if len(moves) == 0 or DLSmax == 0:
        return heuristic(cardsCopy, bannersCopy, player, nextPlayer)

    # If search is not over, find minimum utility from possible moves
    utility = math.inf
    for nextMove in moves:
        utility = min(utility, maxval(boardCopy, nextPlayer, nextMove, bannersCopy, cardsCopy, a, b, DLSmax))
        if utility <= a:
            return utility
        b = min(b, utility)

    return utility


def maxval(board, player, move, banners, cards, a, b, DLSmax):
    '''Returns the maximum utility available from a move on the board.'''
    # Copy all mutable objects
    boardCopy = copy.deepcopy(board)
    bannersCopy = copy.deepcopy(banners)
    cardsCopy = copy.deepcopy(cards)

    # Decrease depth
    DLSmax -= 1

    # Simulate move of current player
    simulate(boardCopy, player, move, bannersCopy, cardsCopy)
    nextPlayer = abs(1 - player)

    # Check if this move ends the game or the search
    moves = getvalidmoves(boardCopy)
    if len(moves) == 0 or DLSmax == 0:
        return heuristic(cardsCopy, bannersCopy, nextPlayer, player)

    # If game is not over, find maximum utility from possible moves
    utility = -math.inf
    for nextMove in moves:
        utility = max(utility, minval(boardCopy, nextPlayer, nextMove, bannersCopy, cardsCopy, a, b, DLSmax))
        if utility >= b:
            return utility
        a = max(a, utility)

    return utility


def simulate(board, player, move, banners, cards):
    '''Update game state based on a potential move made by a specific player.'''
    startIndex = board.index(1)  # starting index of 1-card
    color = board[move]  # color of captured card
    count = 1  # number of cards collected after move
    board[move] = 1  # move 1 card to correct spot
    board[startIndex] = 0  # remove card from start spot

    # Find out what direction the move was in and calculate step value to loop through column or row
    if move < startIndex:
        if startIndex - move >= 6:  # moved up
            step = -6
        else:  # moved left
            step = -1
    else:
        if move - startIndex >= 6:  # moved down
            step = 6
        else:  # moved right
            step = 1

    # Loop through cards passed, seeing if more than 1 needs to be collected
    for i in range(startIndex, move, step):
        if board[i] == color:  # remove that card because it will be picked up
            board[i] == 0
            count += 1

    # Update card collection for player
    cards[player][color - 2] += count

    # Update banner collection, if needed
    if cards[player][color - 2] >= cards[abs(player - 1)][color - 2]:
        banners[player][color - 2] = 1
        banners[abs(player - 1)][color - 2] = 0


def heuristic(cards, banners, player, opponent):
    '''Returns utility of current game state based on custom heuristic.'''
    # Initialize utility
    utility = 0

    # Add +1 for player cards, -1 for opponent cards
    utility += sum(cards[player])
    utility -= sum(cards[opponent])

    # Add +3 for player banners, -3 for opponent banners
    utility += 3 * sum(banners[player])
    utility -= 3 * sum(banners[opponent])

    # Add +10 for player banners secured, -10 for opponent banners secured
    for i in range(len(cards[player])):
        if cards[player][i] > (i + 2) / 2:  # player owns banner
            utility += 10
        if cards[opponent][i] > (i + 2) / 2:  # opponent owns banner
            utility -= 10

    return utility

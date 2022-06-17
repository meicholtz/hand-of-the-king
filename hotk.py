# hotk.py
# A Game of Thrones: Hand of the King is a card game in which players take turns moving the Varys card
# in a single direction around a grid of cards in order to collect cards of a chosen house. Players 
# gain control of a house once they acquire an equal or greater number of cards for that house compared 
# to their opponents. The player in control of the most houses (there are traditionally seven houses) 
# when no more moves are available on the board is declared the winner.
#
# ***This is a non-graphics, AI-only version implemented for speed***

import argparse
from copy import deepcopy
import importlib
import os
import pdb
import random
import sys
import time

ROWS = 6
COLS = 6
HOUSES = [2, 3, 4, 5, 6, 7, 8]  # number of cards for each house

parser = argparse.ArgumentParser(description="Play a Game of Thrones: Hand of the King!")
parser.add_argument('-p', '--players', nargs=2, metavar='name', type=str, help="specify two AI players by filename", default=['ai_random', 'ai_random'])
parser.add_argument('-b', '--board', metavar='file', type=str, help="file containing starting board setup (for repeatability)", default=None)
parser.add_argument('-s', '--seed', metavar='n', type=int, help="seed for random number generator", default=None)
parser.add_argument('-v', '--verbose', action="store_true", help="flag to show helpful text")
parser.add_argument('-d', '--debug', action="store_true", help="flag to use pdb when applicable")


def play(players, board=None, seed=None, verbose=False, debug=False):
    # Initialize the game
    if verbose: print("Let's play a Game of Thrones: Hand of the King!")
    random.seed(seed)  # set seed for random number generator (for repeatability of shuffled cards, if desired)
    ai = loadplayers(players, verbose=verbose)
    board = loadcards(board) if board else dealcards(HOUSES)
    cards = [[0] * len(HOUSES) for i in range(2)]  # initialize card collection for each player
    banners = [[0] * len(HOUSES) for i in range(2)]  # initialize banner collection for each player

    # Store game state as dictionary
    state = {
        'board': board,
        'cards': cards,
        'banners': banners,
        'columns': COLS,
        'rows': ROWS,
        'moves': 0}

    # Play the game
    currentplayer = 0
    while True:
        # Show game info, if desired
        if verbose: show(state, currentplayer)

        # Is the game over?
        validmoves = getvalidmoves(state)
        if len(validmoves) == 0:
            if verbose: print(f'There are no remaining moves. Game over.')
            break

        # Query player to select a card
        whichcard = ai[currentplayer]['module'].get_computer_move(deepcopy(state), currentplayer)

        # Make the move if it is valid
        if whichcard in validmoves:
            makemove(state, currentplayer, whichcard)
            currentplayer = abs(currentplayer - 1)  # switch turns
            state['moves'] += 1
        else:
            sys.exit(f"  ERROR: in play, player {currentplayer} ({ai[currentplayer]['name']}) made an invalid move")

    # Determine winner and return the game output
    return whowins(state, ai)


def dealcards(houses):
    '''Initialize the board by dealing and shuffling the cards.'''
    board = [[i] * i for i in [1] + houses]
    board = [item for sublist in board for item in sublist]
    random.shuffle(board)

    return board


def getvalidmoves(state):
    '''Returns an array of available remaining moves based on current state of game.'''
    # Unpack relevant info
    board = state['board']
    cols = state['columns']
    rows = state['rows']

    # Initialize list of moves
    moves = []

    # Get row and col of 1-card
    ind = board.index(1)
    row, col = ind // cols, ind % cols

    # Check all directions for possible valid moves
    if row > 0:  # up
        possible = [ind - cols * (i + 1) for i in range(row) if board[ind - cols * (i + 1)] != 0]
        possible.reverse()
        houses = []
        for i in possible:
            if board[i] not in houses:
                moves.append(i)
                houses.append(board[i])
    if row < rows - 1:  # down
        possible = [ind + cols * (i + 1) for i in range(rows - row - 1) if board[ind + cols * (i + 1)] != 0]
        possible.reverse()
        houses = []
        for i in possible:
            if board[i] not in houses:
                moves.append(i)
                houses.append(board[i])
    if col > 0:  # left
        possible = [ind - (i + 1) for i in range(col) if board[ind - (i + 1)] != 0]
        possible.reverse()
        houses = []
        for i in possible:
            if board[i] not in houses:
                moves.append(i)
                houses.append(board[i])
    if col < cols - 1:  # right
        possible = [ind + (i + 1) for i in range(cols - col - 1) if board[ind + (i + 1)] != 0]
        possible.reverse()
        houses = []
        for i in possible:
            if board[i] not in houses:
                moves.append(i)
                houses.append(board[i])
    
    return moves


def loadcards(file):
    '''Initialize the board by loading "pre-shuffled" cards from a text file.'''
    with open(file, 'r') as f:
        data = f.read()
    board = [int(i) for i in data.replace('\n', ' ').split()]

    if len(board) != ROWS * COLS:
        sys.exit('  ERROR: in loadcards, invalid board because size does not match expected dimensions')

    return board


def loadplayers(players, verbose=False):
    '''Load AI players from file, if applicable.'''
    ai = [{}, {}]
    for i in range(len(players)):
        pathname, filename = os.path.split(os.path.abspath(players[i]))
        filename = ''.join(filename.split('.')[:-1])  # remove filename extension
        ai[i]['name'] = filename  # simplify the player name for display
        if verbose: print(f"Loading Player {i + 1} AI ({players[i]})...", end="")
        
        try:
            sys.path.append(pathname)  # add directory containing AI player to system path
            ai[i]['module'] = importlib.import_module(filename)
        except ImportError:
            sys.exit(f"\n  ERROR: in loadplayers, cannot import AI player from file ({players[i]})")

        if not hasattr(ai[i]['module'], 'get_computer_move'):
            sys.exit(f"\n  ERROR: in loadplayers, AI player ({players[i]}) does not have required 'get_computer_move' function")
        
        if verbose: print("done")

    if ai[0]['name'] == ai[1]['name']:
        ai[0]['name'] = ai[0]['name'] + '1'
        ai[1]['name'] = ai[1]['name'] + '2'
    
    return ai


def makemove(state, player, card):
    '''Move the Varys card to the position on the board specified by the card index, capturing
    cards of the same house along the way. Update the player's card collection accordingly.'''
    # Extract relevant info
    board = state['board']
    cards = state['cards']
    banners = state['banners']
    cols = state['columns']
    varys = board.index(1)  # index of the Varys card on the board
    house = board[card]  # house of the main captured card

    # Move Varys card to desired position
    board[card] = 1
    board[varys] = 0
    cards[player][house - 2] += 1

    # Determine possible cards to capture based on direction of move
    if abs(card - varys) < cols:  # move is either left or right
        if card < varys:  # left
            possible = range(card + 1, varys)
        else:  # right
            possible = range(varys + 1, card)
    else:  # move is either up or down
        if card < varys:  # up
            possible = range(card + cols, varys, cols)
        else:  # down
            possible = range(varys + cols, card, cols)

    # Capture relevant cards
    for i in possible:
        if board[i] == house:
            board[i] = 0  # there is no card in this position anymore
            cards[player][house - 2] += 1

    # Check to see if current player should capture a banner
    if cards[player][house - 2] >= cards[abs(player - 1)][house - 2]:
        banners[player][house - 2] = 1  # add the banner to the player's collection
        banners[abs(player - 1)][house - 2] = 0


def show(state, player):
    '''Displays relevant info about the game state.'''
    print(f"Number of Moves: {state['moves']}")
    print(f"Current Player: {player}")
    print("Board:")
    board = ''.join(str(i) for i in state['board']).replace('0', '-').replace('1', '*')
    j = 0
    for i in range(state['rows']):
        print("  " + board[j:j+state['columns']])
        j += state['columns']

    print("Cards:", end="\n  ")
    print(*state['cards'][0], end="\n  ")
    print(*state['cards'][1])
    
    print("Banners:", end="\n  ")
    print(*state['banners'][0], end="\n  ")
    print(*state['banners'][1])

    print(f"Score: {sum(state['banners'][0])}-{sum(state['banners'][1])}\n")


def whowins(state, players):
    '''Returns a string describing the outcome of the game, including the winner and corresponding score.'''
    # Unpack relevant info
    banners = state['banners']
    player1 = players[0]['name']
    player2 = players[1]['name']

    # Compare scores
    if sum(banners[0]) > sum(banners[1]):
        result = f"{player1} def {player2} {sum(banners[0])}-{sum(banners[1])}"
    elif sum(banners[1]) > sum(banners[0]):
        result = f"{player2} def {player1} {sum(banners[1])}-{sum(banners[0])}"
    else:
        if banners[0][::-1].index(1) < banners[1][::-1].index(1):
            result = f"{player1} def {player2} {sum(banners[0])}-{sum(banners[1])} w/ tiebreaker"
        else:
            result = f"{player2} def {player1} {sum(banners[1])}-{sum(banners[0])} w/ tiebreaker"

    return result


if __name__ == "__main__":
    result = play(**vars(parser.parse_args()))
    print(result)
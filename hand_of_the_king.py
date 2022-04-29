# hand_of_the_king.py
# A Game of Thrones: Hand of the King is a game in which players take turns moving a purple card
# in a single direction around a grid of colored cards in order to collect cards of a chosen color.
# Players gain control of a color once they acquire an equal or greater number of cards compared to
# their opponents. The player in control of the most colors (there are seven colors total) when no
# more moves are available on the board is declared the winner.

import argparse
from graphics import *
import importlib
import pdb
import random
import time

ROWS = 6
COLS = 6
COLORS = 8  # number of colors, 7 of which can be controlled
CARD_SIZE = 60  # height and width of cards, in pixels
MARGIN = 10  # space in between cards, in pixels
PAUSE = 1  # default time (in seconds) to wait between things

parser = argparse.ArgumentParser(description="Play a Game of Thrones: Hand of the King!")
parser.add_argument('--player1', metavar='p1', type=str, help="either human or the name of an AI file", default='human')
parser.add_argument('--player2', metavar='p2', type=str, help="either human or the name of an AI file", default='human')
parser.add_argument('-b', '--board', type=str, help="file containing starting board setup (for repeatability)", default=None)
parser.add_argument('-s', '--seed', metavar='n', type=int, help="seed for random number generator", default=None)


def main(args):
    print("Let's play a Game of Thrones: Hand of the King!")

    # Initialize the game
    random.seed(args.seed)  # set seed for random number generator (for repeatability of shuffled cards, if desired)
    board = loadcards(args.board) if args.board else shufflecards()  # load or shuffle cards to make a board array
    x0 =  board.index(1)  # starting position of the 1-card (which will be needed as a workaround for actually swapping graphics objects)
    gui = gamesetup(board)  # make the gui
    cards = [[0] * (COLORS - 1) for i in range(2)]  # initialize card collection for each player
    banners = [[0] * (COLORS - 1) for i in range(2)]  # initialize banner collection for each player

    # Load AI player(s) if needed
    players = [args.player1, args.player2]
    ai = [None, None]
    for i in range(2):
        if players[i] != "human":
            print(f"Loading Player {i + 1} AI ({players[i]})...", end="")
            try:
                pathname, filename = os.path.split(os.path.abspath(players[i]))
                filename = ''.join(filename.split('.')[:-1])  # remove filename extension
                players[i] = filename  # simplify the player name for display
                sys.path.append(pathname)  # add directory containing AI player to system path
                ai[i] = importlib.import_module(filename)
            except ImportError:
                print(f"\n\tERROR: Cannot import AI player from file ({players[i]})")
                return 0

            if not hasattr(ai[i], 'get_computer_move'):
                print(f"\n\tERROR: This AI player does not have a 'get_computer_move' function")
                return 0
            print("done")

    # Play the game
    turn = 0
    gameover = False
    while True:
        # Is the game over?
        validmoves = getvalidmoves(board)
        if len(validmoves) == 0:
            # print(f'There are no remaining moves. Game over.')
            gameover = True
            if sum(banners[0]) > sum(banners[1]):
                winner = 'Player 1' if players[0] == 'human' or players[0] == players[1] else players[0]
                status(gui, f"{winner} wins!")
            elif sum(banners[1]) > sum(banners[0]):
                winner = 'Player 2' if players[1] == 'human' or players[0] == players[1] else players[1]
                status(gui, f"{winner} wins!")
            else:
                status(gui, "It's a tie!")

        # Keep playing if it is not over
        if not gameover:
            # Query player to select a card
            ind = -1
            if players[turn] == 'human':
                status(gui, f'Player {turn + 1}, choose a move')
                # Check for mouse input
                pt = gui.checkMouse()
                if pt:
                    x, y = int(pt.getX()), int(pt.getY())
                    row = max(0, min(ROWS - 1, (y - MARGIN // 2) // (CARD_SIZE + MARGIN)))
                    col = max(0, min(COLS - 1, (x - MARGIN // 2) // (CARD_SIZE + MARGIN)))
                    # print(f'(x,y)=({x},{y}), (row,col)=({row},{col})')
                    ind = COLS * row + col
            else:  # the player is an AI agent
                status(gui, f'{players[turn]} is thinking...')
                time.sleep(PAUSE)
                ind = ai[turn].get_computer_move(board.copy(), cards, banners, turn)

            # Make the move if it is valid
            if ind in validmoves:
                # print(f"choosing card {ind}")
                # print(*board)
                # print(*validmoves)
                color = board[ind]  # save the color being captured for later
                makemove(gui, board, ind, x0, cards[turn])
                # print(*board)

                # Check to see if current player should capture a banner
                if cards[turn][color - 2] >= cards[abs(turn - 1)][color - 2]:
                    banners[turn][color - 2] = 1  # add the banner to the player's collection
                    banners[abs(turn - 1)][color - 2] = 0
                
                # Switch turns
                turn = abs(turn - 1)
                
                # Stuff for debugging
                print("card collections")
                print(*cards[0])
                print(*cards[1])
                print("banners")
                print(*banners[0])
                print(*banners[1])
                print(f'score: {sum(banners[0])}-{sum(banners[1])}\n')
                
                # print(*board)

        # Check for keyboard input
        key = gui.checkKey()
        if key:
            # print(key)
            if key == "Escape" or key == "Ctrl+e":  # exit game
                break


def gamesetup(board):
    '''Create the board user interface.'''
    # Read colors from file
    colors = [0] * COLORS
    with open('colors.txt', 'r') as f:
        for i in range(COLORS):
            colors[i] = f.readline().strip().split(',')

    # Make game window
    wid = COLS * CARD_SIZE + MARGIN * (COLS + 1)
    hei = ROWS * CARD_SIZE + MARGIN * (ROWS + 1) + 30
    gui = GraphWin("A Game of Thrones: Hand of the King", wid, hei)
    
    # Create card graphics
    for row in range(ROWS):
        for col in range(COLS):
            x1 = MARGIN * (col + 1) + CARD_SIZE * col
            y1 = MARGIN * (row + 1) + CARD_SIZE * row
            x2 = x1 + CARD_SIZE
            y2 = y1 + CARD_SIZE
            card = Rectangle(Point(x1, y1), Point(x2, y2))
            whichcolor = board[COLS * row + col]  # index of the color for the card in the current (row, col)
            # print(f'row={row}, col={col}, index={COLS * row + col}, color={whichcolor}')
            card.setFill(colors[whichcolor - 1][0])
            card.setOutline(colors[whichcolor - 1][1])
            card.setWidth(4)
            card.draw(gui)

    # Add text message at bottom
    txt = Text(Point(wid // 2, hei - 20), "")
    txt._reconfig("anchor", "c")
    txt.setSize(12)
    txt.draw(gui)

    return gui


def getvalidmoves(board):
    '''Returns an array of available remaining moves based on current board.'''
    # Initialize list of moves
    moves = []

    # Get row and col of 1-card
    ind = board.index(1)
    row, col = ind // COLS, ind % COLS

    # Check all directions for possible valid moves
    if row > 0:  # up
        possible = [ind - COLS * (i + 1) for i in range(row) if board[ind - COLS * (i + 1)] != 0]
        possible.reverse()
        colors = []
        for i in possible:
            if board[i] not in colors:
                moves.append(i)
                colors.append(board[i])
    if row < ROWS - 1:  # down
        possible = [ind + COLS * (i + 1) for i in range(ROWS - row - 1) if board[ind + COLS * (i + 1)] != 0]
        possible.reverse()
        colors = []
        for i in possible:
            if board[i] not in colors:
                moves.append(i)
                colors.append(board[i])
    if col > 0:  # left
        possible = [ind - (i + 1) for i in range(col) if board[ind - (i + 1)] != 0]
        possible.reverse()
        colors = []
        for i in possible:
            if board[i] not in colors:
                moves.append(i)
                colors.append(board[i])
    if col < COLS - 1:  # right
        possible = [ind + (i + 1) for i in range(COLS - col - 1) if board[ind + (i + 1)] != 0]
        possible.reverse()
        colors = []
        for i in possible:
            if board[i] not in colors:
                moves.append(i)
                colors.append(board[i])
    
    return moves


def loadcards(txtfile):
    '''Initialize the board by loading "pre-shuffled" cards from file.'''
    with open(txtfile, 'r') as f:
        data = f.read()
    board = [int(i) for i in data.replace('\n', ' ').split()]

    if len(board) != ROWS * COLS:
        print('ERROR: Invalid board (size does not match expected dimensions)')
        exit()

    return board


def makemove(gui, board, x, x0, collection):
    '''Move the 1-card in the GUI to the position on the board specified by the input index, capturing
    cards of the same color along the way. Update the player's card collection accordingly.
    
    Note that x0 is the intial position of the 1-card in the objects array, which we need to correctly move it around.'''
    # Get relevant data
    cards = gui.items[:-1]
    x1 = board.index(1)  # index of the 1-card on the board
    # print(f'moving from {x1} to {x}')

    # Remove captured cards from board
    d = gui.width + 100  # distance to move cards
    color = board[x]  # color of the main captured card
    cards[x].move(d, 0)
    board[x] = 1  # the 1-card moves here
    collection[color - 2] += 1
    if abs(x - x1) < COLS:  # move is either left or right
        dx = (x - x1) * (CARD_SIZE + MARGIN)
        dy = 0
        if x < x1:  # left
            possible = range(x + 1, x1)
        else:  # right
            possible = range(x1 + 1, x)
    else:  # move is either up or down
        dx = 0
        dy = ((x - x1) // COLS) * (CARD_SIZE + MARGIN)
        if x < x1:  # up
            possible = range(x + COLS, x1, COLS)
        else:  # down
            possible = range(x1 + COLS, x, COLS)

    for i in possible:
        if board[i] == color:
            cards[i].move(d, 0)
            board[i] = 0  # there is no card in this position anymore
            collection[color - 2] += 1

    # Move the 1-card to the correct position
    cards[x0].move(dx, dy)
    board[x1] = 0



def shufflecards():
    '''Initialize the board by shuffling the cards.'''
    board = [[i] * i for i in range(1, COLORS + 1)]
    board = [item for sublist in board for item in sublist]
    random.shuffle(board)

    return board


def status(gui, msg):
    '''Update the text status in the GUI.'''
    txt = gui.items[-1]
    txt.setText(msg)


if __name__ == "__main__":
    main(parser.parse_args())
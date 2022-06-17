# test_dict.py
# Testing to see if using a dictionary to store the state of the game is a good idea.

import copy
import pdb
import random

def main():
    # Make a board
    houses = [2, 3, 4, 5, 6, 7, 8]
    board = [[i] * i for i in [1] + houses]
    board = [item for sublist in board for item in sublist]
    random.shuffle(board)
    # print(board)

    # Initialize cards and banners
    cards = [[0] * len(houses) for i in range(2)]  # initialize card collection for each player
    banners = [[0] * len(houses) for i in range(2)]  # initialize banner collection for each player

    # Compile into dictionary
    state = {'board': board, 'cards': cards, 'banners': banners}
    print(state)

    # Test mutability
    dosomething(copy.deepcopy(state))
    print(state)


def dosomething(state):
    '''Alter the state without returning the variable.'''
    state['board'][0] = -1
    
    mycards = state['cards'][0]
    mycards[-1] = 8

    banners = state['banners']
    banners[0][0] = 1


if __name__ == "__main__":
    main()
    
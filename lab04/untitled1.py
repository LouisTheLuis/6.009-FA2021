# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 16:21:26 2021

@author: Louis Martinez
"""

#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)

# HELPER FUNCTIONS

def check_square_number(board, r, c):
    """ 
    Returns the number of bombs surrounding the tile at position (r, c), where r is the row number and c is
    the columns number.
    
    Parameters:
        board (list): Two-dimensional list represent the state of the board (where bombs are represented with
        '.' and lack of bombs are represented by 0)
        r (int): Row number
        c (int): Row column
    """
    spaces = [-1, 0, 1]
    row_len = len(board)
    col_len = len(board[0])
    
    neighbor_bombs = 0
    for i in spaces:
        for j in spaces:
            if (r + i >= 0 and r + i < row_len) and (c + j >= 0 and c + j < col_len):
                if board[r + i][c + j] == '.':
                    neighbor_bombs += 1
    return neighbor_bombs

def board_and_mask(num_rows, num_cols, bombs):
    """ 
    Returns the 2D array representations of the board and the mask.
    
    Parameters:
        num_rows (int): Number of rows.
        num_cols (int): Number of columns.
        bombs (list): List of tuples containing the locations of the bombs.
    """
    board = []
    mask = []
    for r in range(num_rows):
        row_board = []
        row_mask = []
        for c in range(num_cols):
            if [r, c] in bombs or (r, c) in bombs:
                row_board.append('.')
            else:
                row_board.append(0)
            row_mask.append(False)
        board.append(row_board)
        mask.append(row_mask)
    return [board, mask]


def checks_conditions(game, row_len, col_len):
    """
    Returns whether the tile at position (row_len, col_len) satisfies the following conditions:
        > The position is within the bounds of the game's board dimensions.
        > The position does not contain a bomb.
        > The position has not been shown.
    
    Parameters:
        game (dict): a dictionary with the information of the game.
        row_len (int): the row coordinate.
        col_len (int): the column coordinate.
        
    Return:
        boolean: False or True.
    """
    num_rows, num_cols = game['dimensions']
    if 0 <= row_len < num_rows:
        if 0 <= col_len < num_cols:
            if game['board'][row_len][col_len] != '.':
                if game['mask'][row_len][col_len] == False:
                    return True
    return False

def check_state(board, mask, num_rows, num_cols):
    """ 
    Returns the state of the game given the board and the mask of a game.
    
    Parameters:
        board (list): Two-dimensional list representing the state of the board (where bombs are represented with
        '.' and lack of bombs are represented by 0).
        mask (list): Two-dimensional list of booleans which determine whether a tile is shown (True) or not
        (False).
        num_rows (int): Number of rows.
        num_cols (int): Number of columns.
    """
    bombs = 0
    covered_squares = 0
    for r in range(num_rows):
        for c in range(num_cols):
            if board[r][c] == '.':
                if mask[r][c] == True:
                    bombs += 1
            elif mask[r][c] == False:
                covered_squares += 1

    bad_squares = bombs + covered_squares
    if bad_squares > 0:
        return 'ongoing'
    if bombs != 0:
        # if bombs is not equal to zero, set the game state to defeat and
        # return 0
        return 'defeat'
    if covered_squares == 0:
        return 'victory'
    
# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing
    """
    # Replaced both loops for the creation of the board and mask 2D array representations by a helper function.
    board, mask = board_and_mask(num_rows, num_cols, bombs)
    
    for r in range(num_rows):
        for c in range(num_cols):
            if board[r][c] == 0:
            # Eliminated the sequence of loops and replaced it with a helper function that checks the value 
            # of the square.
                value = check_square_number(board, r, c)
                board[r][c] = value
                
    return {
        'dimensions': (num_rows, num_cols),
        'board': board,
        'mask': mask,
        'state': 'ongoing'}


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat
    """
    if game['state'] == 'defeat' or game['state'] == 'victory':
        game['state'] = game['state']  # keep the state the same
        return 0

    if game['board'][row][col] == '.':
        game['mask'][row][col] = True
        game['state'] = 'defeat'
        return 1
    
    # Replaced loop to determine state of the game by helper function.
    state = check_state(game['board'], game['mask'], game['dimensions'][0], game['dimensions'][1])
    if state != 'ongoing':
        game['state'] = state
        return 0

    if game['mask'][row][col] != True:
        game['mask'][row][col] = True
        revealed = 1
    else:
        return 0
    
    spaces = [-1, 0, 1]
    if game['board'][row][col] == 0:
        # Replaced the repeating if statements by a loop for each adjacent tile to (row, column)  
        # and a helper function that checks the desired conditions.
        for r in spaces:
            for c in spaces:
                if checks_conditions(game, row + r, col + c):
                    revealed += dig_2d(game, row + r, col + c)
                    
    # Replaced loop to determine state of the game by helper function.
    state = check_state(game['board'], game['mask'], game['dimensions'][0], game['dimensions'][1])
    if state != 'defeat':
        game['state'] = state
        return revealed


def render_2d_locations(game, xray = False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['mask'] indicates which squares should be visible.  If xray
    is True (the default is False), game['mask'] is ignored and all cells are
    shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    locations_map = []
    board = game['board']
    mask = game['mask']
    
    # If xray is True, it shows all the tiles.
    # Iterates over each row and then each tile in the row, and adds the corresponding value to a 
    # temporary row list, which is then added to the 2D array (locations_map).
    if xray:
        for row in range(len(board)):
            row_list = []
            for column in range(len(board[row])):
                if board[row][column] != 0:
                    row_list.append(str(board[row][column]))
                else:
                    row_list.append(' ')
            locations_map.append(row_list)
    
    # If xray is False, it reveals the tiles according to mask boolean values.
    # Iterates over each tile in each row, creates a row list and adds the corresponding values.
    # This row list is then added to a 2D array (locations_map).
    else: 
        for row in range(len(board)):
            row_list = []
            for column in range(len(board[row])):
                if mask[row][column] == False:
                    row_list.append('_')
                else:
                    if board[row][column] != 0:
                        row_list.append(str(board[row][column]))
                    else:
                        row_list.append(' ')
            locations_map.append(row_list)
    return locations_map


def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'mask':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    board = game['board']
    mask = game['mask']
    
    board_map = render_2d_locations(game, xray)
    board_ASCII = ''
    
    for row in range(len(board_map)):
        for column in range(len(board_map[row])):
            board_ASCII += board_map[row][column]
        if row != len(board_map) - 1:
            board_ASCII += "\n"
            
    return board_ASCII


# N-D HELPER FUNCTIONS

def get_value(n_array, coord):
    """ 
    Returns the value present at certain coordinates of the n-dimensional array.
    
    Parameters:
        n_array (list): N-dimensional list of lists.
        coord (tuple): tuple of length N.
    """
    if len(coord) == 1:
        return n_array[coord[0]]
    else:
        array = n_array[coord[0]]
        return get_value(array, coord[1:])
    
def set_value(n_array, coord, value):
    """ 
    Sets the value present at certain coordinates of the n-dimensional array.
    
    Parameters:
        n_array (list): N-dimensional list of lists.
        coord (tuple): tuple of length N.
        value (int or String): value that we want to set.
    """
    if len(coord) == 1:
        n_array[coord[0]] = value
    else:
        array = n_array[coord[0]]
        set_value(array, coord[1:], value)

def create_n_array(dimensions, value):
    """
    Returns a N-dimensional array where all the values are the same.
    
    Parameters:
        dimensions (tuple): A tuple of N elements (int)s that give the dimensions of the array.
        value: Any value of any data type.
    """
    if len(dimensions) == 1:
        temp_list = []
        for i in range(dimensions[0]):
            temp_list.append(value)
        return temp_list
    else:
        temp_list = []
        for i in range(dimensions[0]):
            inner_list = create_n_array(dimensions[1:], value)
            temp_list.append(inner_list)
        return temp_list
    
def coord_list(dimensions):
    """ 
    Returns a list with all the possible coordinates for a N-dimensional array of the given dimensions.
    
    Parameters:
        dimensions (tuple): A tuple of N elements (int)s that give the dimensions of the array.
    """
    if len(dimensions) == 1:
        temp_list = []
        for number in range(dimensions[0]):
            temp_list.append(number)
        return temp_list
    
    else:
        inner_list = coord_list(dimensions[:-1])
        temp_list = []
        for i in range(dimensions[-1]):
            for j in inner_list:
                if type(j) == int:
                    value = [j]
                else:
                    value = list(j)
                value.append(i)
                temp_list.append(value)
        return temp_list

def check_square_neighbors(board, coord, dimension, dimensions):
    """
    Returns the list of coordinates of the neighbors of a given coordinate coord.
    
    Parameters:
        board (list): N-dimensional list of lists describing the current state of the board.
        coord (tuple): A tuple giving the coordinates of the tile from which we want to find the neighbors.
        dimension (int): Number of dimensions - 1.
        dimensions (tuple): A tuple giving the dimensions of the N-dimensional board.
    """
    spaces = [-1, 0, 1]
    if dimension == 0:
        temp_list = []
        for j in spaces:
            if coord[dimension] + j >= 0 and coord[dimension] + j < dimensions[dimension]:
                new_coord = list(coord).copy()
                new_coord[dimension] = coord[dimension] + j
                temp_list.append(tuple(new_coord))
        return temp_list
    else:
        inner_list = check_square_neighbors(board, coord, dimension - 1, dimensions)
        temp_list = []
        for i in inner_list:
            for j in spaces:
                if i[dimension] + j >= 0 and i[dimension] + j < dimensions[dimension]:
                    new_coord = list(i).copy()
                    new_coord[dimension] = i[dimension] + j
                    temp_list.append(tuple(new_coord))
        return temp_list

def check_n_state(game, bombs=0, covered_squares=0):
    """ 
    Returns the state of a given game.
    
    Parameters:
        game (dict): dictionary containing all the information (dimensions, board, mask, etc) about the game.
    """
    if bombs == 0 and covered_squares == 0:
        coordinates = coord_list(game['dimensions'])
        for coord in coordinates:
            if get_value(game['board'], coord) == '.':
                if get_value(game['mask'], coord) == True:
                    bombs += 1
            elif get_value(game['mask'], coord) == False:
                covered_squares += 1

    bad_squares = bombs + covered_squares
    if bad_squares > 0:
        return 'ongoing'
    if bombs != 0:
        # if bombs is not equal to zero, set the game state to defeat and
        # return 0
        return 'defeat'
    if covered_squares == 0:
        return 'victory'

def bombs_and_squares(game):
    bombs = 0
    covered_squares = 0
    coordinates = coord_list(game['dimensions'])
    for coord in coordinates:
        if get_value(game['board'], coord) == '.':
            if get_value(game['mask'], coord) == True:
                bombs += 1
        elif get_value(game['mask'], coord) == False:
            covered_squares += 1
    return (bombs, covered_squares)

# N-D IMPLEMENTATION


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    # Replaced both loops for the creation of the board and mask 2D array representations by a helper function.
    board = create_n_array(dimensions, 0)
    mask = create_n_array(dimensions, False)
    
    for coordinate in bombs:
        set_value(board, coordinate, '.')
    
    #####coordinate_list = coord_list(dimensions)
    
    bomb_neighbors = []
    for coordinate in bombs:
        neighbors = check_square_neighbors(board, coordinate, len(dimensions) - 1, dimensions)
        for neighbor in neighbors:
            bomb_neighbors.append(neighbor)
            
    for coordinate in bomb_neighbors:
        if get_value(board, coordinate) == 0:
            neighbors = check_square_neighbors(board, coordinate, len(dimensions) - 1, dimensions)
            value = 0
            for neighbor in neighbors:
                if get_value(board, neighbor) == '.':
                    value += 1
            set_value(board, coordinate, value)   
    
    """for coordinate in coordinate_list:
        if get_value(board, coordinate) == 0:
            neighbors = check_square_neighbors(board, coordinate, len(dimensions) - 1, dimensions)
            value = 0
            for neighbor in neighbors:
                if get_value(board, neighbor) == '.':
                    value += 1
            set_value(board, coordinate, value)"""
            
    return {
        'dimensions': dimensions,
        'board': board,
        'mask': mask,
        'state': 'ongoing'
        }


def dig_nd(game, coordinates, bombs=0, covered_squares=0):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """
    bombs, covered_squares = bombs_and_squares(game)
    
    if game['state'] == 'defeat' or game['state'] == 'victory':
        game['state'] = game['state']  # keep the state the same
        return 0
    
    if get_value(game['board'], coordinates) == '.':
        set_value(game['mask'], coordinates, True)
        bombs += 1
        covered_squares += -1
        game['state'] = 'defeat'
        return 1
    
    # Replaced loop to determine state of the game by helper function.
    state = check_n_state(game)
    if state != 'ongoing':
        game['state'] = state
        return 0
    
    if get_value(game['mask'], coordinates) != True:
        set_value(game['mask'], coordinates, True)
        covered_squares += -1
        revealed = 1
    else:
        return 0

    if get_value(game['board'], coordinates) == 0:
        neighbors = check_square_neighbors(game['board'], coordinates, len(coordinates) - 1, game['dimensions'])
        for neighbor in neighbors:
            if get_value(game['board'], neighbor) != '.' and get_value(game['mask'], neighbor) == False:
                revealed += dig_nd(game, neighbor, bombs, covered_squares)
                    
    # Replaced loop to determine state of the game by helper function.
    state = check_n_state(game)
    if state != 'defeat':
        game['state'] = state
        return revealed

def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    board = game['board']
    mask = game['mask']
    dimensions = game['dimensions']
    
    temp_board = create_n_array(dimensions, None)
    coordinate_list = coord_list(game['dimensions'])
    
    for coord in coordinate_list:
        if get_value(mask, coord) == False and xray == False:
            set_value(temp_board, coord, '_')
        else:
            if get_value(board, coord) == 0:
                set_value(temp_board, coord, ' ')
            else:
                value = str(get_value(board, coord))
                set_value(temp_board, coord, value)
                    
    return temp_board


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    #doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    game = new_game_nd((15, 15, 12, 10), [(0,0,0, 3)])
    boole = check_n_state(game)
    print(boole)
    doctest.run_docstring_examples(
        new_game_nd,
        globals(),
        optionflags=_doctest_flags,
        verbose=False
     )

"""6.009 Lab 10: Snek Is You Video Game"""

import doctest

# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
NOUNS = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
WORDS = NOUNS | PROPERTIES | {"AND", "IS"}

# Maps a keyboard direction to a (delta_row, delta_column) vector.
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, where UPPERCASE
    strings represent word objects and lowercase strings represent regular
    objects (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['snek'], []],
        [['SNEK'], ['IS'], ['YOU']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """            
    positions = {}
    board = []
    for row in range(len(level_description)):
        new_row = []
        for col in range(len(level_description[0])):
            tile = []
            if level_description[row][col]:
                for elem in level_description[row][col]:
                    value = Tile(elem, (row, col))
                    if elem in positions.keys():
                        positions[elem].append(value)
                    else:
                        positions[elem] = [value]
                    tile.append(value)
                new_row.append(tile)
            else:
                new_row.append(tile)
        board.append(new_row)
    
    rules = find_rules(board)
    effects = perform_rules(rules, positions)

    game = {
        'board': board,
        'rules': rules,
        'dimensions': (len(level_description), len(level_description[0])),
        'state': 'current',
        'positions': positions,
        'effects': effects
        }
    return game


def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user's
    input is given by direction, which is one of the following:
    {'up', 'down', 'left', 'right'}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """
    direction = direction_vector[direction]
    if 'YOU' not in game['effects'].keys():
        game['state'] = 'defeat'
        return False
    
    ######################
    print_board(game)
    print()
    ######################
    
    
    for player in game['effects']['YOU']:
        move(player, direction, game)
        
    game['rules'] = find_rules(game['board'])
    game['effects'] = perform_rules(game['rules'], game['positions'])
    handle_defeat(game)
    handle_win(game)
    ####################
    print_board(game)
    print()
    print()
    ####################
    result = is_win(game['state'])
    return result


def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    canonical_rep = to_canonical(game['board'])
    return canonical_rep


#############################################################################
# FUNCTIONING OF THE GAME ITSELF
#############################################################################
def is_win(state):
    """ 
    Given a certain state of the board, returns a boolean whether the game has been won or not.
    """
    if state == "win":
        return True
    else:
        return False
    
    
def find_rules(board):
    """ 
    Given a game board, this function will scan all the rows and columns and check for the formation of
    rules.
    It ultimately returns a list of rules for the specific state of the game.
    """
    uppers = []
    # Check the board horizontally
    for row in range(len(board)):
        upper_words = []
        for col in range(len(board[0])):
            if board[row][col]:
                for elem in board[row][col]:
                    if elem.name.isupper():
                        upper_words.append(elem.name)
        uppers.append(upper_words)
    
    # Check the board vertically
    for col in range(len(board[0])):
        upper_words = []
        for row in range(len(board)):
            if board[row][col]:
                for elem in board[row][col]:
                    if elem.name.isupper():
                        upper_words.append(elem.name)
        uppers.append(upper_words)
        
        
    new_uppers = []
    for i in range(len(uppers)):
        if len(uppers[i]) != 0:
            new_uppers.append(uppers[i])
                
    possible_rules = []
    for lst in new_uppers:
            p_rule = []
            for i in range(len(lst)):
                if len(p_rule) == 0:
                    if lst[i] in NOUNS:
                        p_rule.append(lst[i])
                else:
                    if p_rule[-1] in NOUNS:
                        if lst[i] != 'IS' and lst[i] != 'AND':
                            p_rule = []
                            continue
                        else:
                            p_rule.append(lst[i])
                            continue
                    if p_rule[-1] in PROPERTIES:
                        if lst[i] != 'AND' and lst[i] not in NOUNS:
                            possible_rules.append(p_rule)
                            new_uppers.append(lst[i:])
                            p_rule = []
                            continue
                        elif lst[i] in NOUNS:
                            possible_rules.append(p_rule)
                            new_uppers.append(lst[i:])
                            p_rule = []
                            continue
                        else:
                            p_rule.append(lst[i])
                            continue
                    if p_rule[-1] == 'IS':
                        if lst[i] == 'AND' or lst[i] == 'IS':
                            p_rule = []
                            continue
                        else:
                            p_rule.append(lst[i])
                            continue
                    if p_rule[-1] == 'AND':
                        if lst[i] == 'AND' or lst[i] == 'IS':
                            p_rule = []
                            continue
                        else:
                            p_rule.append(lst[i])
                            continue
                            
            if len(p_rule) != 0:
                possible_rules.append(p_rule)
    rules = []
    for sentence in possible_rules:
        rule = elaborate_rule(sentence)
        rules = rules + rule
    
    return rules


def elaborate_rule(possible_rule):
    left_side = []
    right_side = []
    flag = True
    for elem in possible_rule:
        if elem == 'IS':
            flag = False
        if elem != 'AND' and flag:
            left_side.append(elem)
        else:
            right_side.append(elem)
            
    rules = []
    for elem1 in left_side:
        for elem2 in right_side:
            rule = [elem1, 'IS', elem2]
            rules.append(rule)
    
    return rules


def perform_rules(rules, positions):
    """ 
    For every element in the board, this function performs the rules to each element.
    """
    effects = {}
    for rule in rules:
        noun = rule[0]
        properties = rule[2]
            
        for tile in positions[noun.lower()]:
            tile.update_state(properties)
            if properties not in effects.keys():
                effects[properties] = [tile]
            else:
                effects[properties].append(tile)
            
    return effects


def to_canonical(board):
    """ 
    Given a certain board, this function turns the board into its canonical representation.
    """
    new_board = []
    for row in range(len(board)):
        row_line = []
        for col in range(len(board[0])):
            if board[row][col]:
                can_tile = []
                for tile in board[row][col]:
                    can_tile.append(tile.name)
                row_line.append(can_tile)
            else:
                row_line.append([])
        new_board.append(row_line)
    return new_board


def print_board(game):
    board = game['board']
    for row in range(len(board)):
        print(board[row])


def is_valid(opp, game):
    r, c = opp
    if r < game['dimensions'][0] and c < game['dimensions'][1] and r >= 0 and c >= 0:
        if game['board'][r][c]:
            return True
        else:
            return False
    else:
        return False


def move(tile, direction, game):
    """ 
    This function makes a move of an element to the tile in the direction given.
    """
    board = game['board']
    new_pos = tuple([sum(x) for x in zip(tile.position, direction)])
    opp_pos = tuple([x - y for x, y in zip(tile.position, direction)])
    r, c = tile.position
    r1, c1 = new_pos
    r2, c2 = opp_pos
    
    if r1 >= game['dimensions'][0] or c1 >= game['dimensions'][1] or r1 < 0 or c1 < 0:
        return
         
    else:
        # Check if the tile where to move is empty            
        if not board[r1][c1]:
            if not is_valid(opp_pos, game):
                board[tile.position[0]][tile.position[1]].remove(tile)
                tile.update_pos(new_pos)
                board[r1][c1].append(tile)
            else:
                board[tile.position[0]][tile.position[1]].remove(tile)
                tile.update_pos(new_pos)
                board[r1][c1].append(tile)
                for elem in board[r2][c2]:
                    if 'PULL' in elem.states:
                        make_pull(tile, direction, game, elem, (r, c))
        # Tile is not empty
        else:
            if not is_valid(opp_pos, game):
                for elem in board[r1][c1]:
                    if 'STOP' in elem.states and 'PUSH' not in elem.states:
                        continue
                    elif 'PUSH' in elem.states:
                        make_push(tile, direction, game, elem)
                    else:
                        board[tile.position[0]][tile.position[1]].remove(tile)
                        tile.update_pos(new_pos)
                        board[r1][c1].append(tile)
            else:
                for elem in board[r1][c1]:
                    if 'STOP' in elem.states and 'PUSH' not in elem.states:
                        continue
                    elif 'PUSH' in elem.states:
                        make_push(tile, direction, game, elem)
                    else:
                        board[tile.position[0]][tile.position[1]].remove(tile)
                        tile.update_pos(new_pos)
                        board[r1][c1].append(tile)
                for elem in board[r2][c2]:
                    if 'PULL' in elem.states:
                        make_pull(tile, direction, game, elem, (r, c))


def make_push(tile, direction, game, pushed):
    board = game['board']
    new_pos = tuple([sum(x) for x in zip(tile.position, direction)])
    r1, c1 = new_pos
    
    x, y = tuple([sum(i) for i in zip(new_pos, direction)])
    if x >= game['dimensions'][0] or y >= game['dimensions'][1] or x < 0 or y < 0:
        return False
    
    if not board[x][y]:
        board[tile.position[0]][tile.position[1]].remove(tile)
        tile.update_pos(new_pos)
        board[r1][c1].append(tile)
            
        board[r1][c1].remove(pushed)
        pushed.update_pos((x, y))
        board[x][y].append(pushed)
        return True
    
    for elem in board[x][y]:
        if 'STOP' in elem.states and 'PUSH' not in elem.states:
            return False
    
    for elem in board[x][y]:
        if 'PUSH' in elem.states:
            val = make_push(pushed, direction, game, elem)
            if val:
                board[tile.position[0]][tile.position[1]].remove(tile)
                tile.update_pos(new_pos)
                board[r1][c1].append(tile)
                return True
            else:
                return False
        
    for elem in board[x][y]:
        if 'PUSH' not in elem.states:
            board[tile.position[0]][tile.position[1]].remove(tile)
            tile.update_pos(new_pos)
            board[r1][c1].append(tile)
            
            board[r1][c1].remove(pushed)
            pushed.update_pos((x, y))
            board[x][y].append(pushed)
            return True
        
    return False


def make_pull(tile, direction, game, pulled, t_pos):
    board = game['board']
    opp_pos = tuple([x - y for x, y in zip(t_pos, direction)])
    r2, c2 = opp_pos
    x, y = tuple([x - y for x, y in zip(opp_pos, direction)])
    
    if tile in board[t_pos[0]][t_pos[1]]:
        return
        
    for elem in board[t_pos[0]][t_pos[1]]:
        if 'STOP' in elem.states:
            return False
        
    if x >= game['dimensions'][0] or y >= game['dimensions'][1] or x < 0 or y < 0:
        board[r2][c2].remove(pulled)
        pulled.update_pos(t_pos)
        board[t_pos[0]][t_pos[1]].append(pulled)
        
        if board[r2][c2]:
            for elem in board[r2][c2]:
                if 'PULL' in elem.states:
                    board[r2][c2].remove(elem)
                    elem.update_pos(t_pos)
                    board[t_pos[0]][t_pos[1]].append(elem)
        return True
    
    if not board[x][y]:
        board[r2][c2].remove(pulled)
        pulled.update_pos(t_pos)
        board[t_pos[0]][t_pos[1]].append(pulled)
        
        if board[r2][c2]:
            for elem in board[r2][c2]:
                if 'PULL' in elem.states:
                    board[r2][c2].remove(elem)
                    elem.update_pos(t_pos)
                    board[t_pos[0]][t_pos[1]].append(elem)
        return True
    
    line = board[x][y].copy()
    val = None
    nostop = True
    for elem in line:
        if 'PULL' in elem.states:
            val = make_pull(tile, direction, game, elem, pulled.position)
        if 'STOP' in elem.states:
            nostop = False
    
    for elem in line:
        if val and nostop:
            if 'PUSH' in elem.states:
                board[x][y].remove(elem)
                elem.update_pos(opp_pos)
                board[r2][c2].append(elem)
            
    board[r2][c2].remove(pulled)
    pulled.update_pos(t_pos)
    board[t_pos[0]][t_pos[1]].append(pulled)
    return True


def handle_defeat(game):
    board = game['board']
    for row in range(len(board)):
        for col in range(len(board[0])):
            player_flag = False
            player_list = []
            defeat_flag = False
            for elem in board[row][col]:
                if 'YOU' in elem.states:
                    player_flag = True
                    player_list.append(elem)
                if 'DEFEAT' in elem.states:
                    defeat_flag = True
            if player_flag and defeat_flag:
                for elem in player_list:
                    game['positions'][elem.name].remove(elem)
                    board[elem.position[0]][elem.position[1]].remove(elem)
                    game['effects']['YOU'].remove(elem)
            
    if 'YOU' not in game['effects'].keys():
        game['state'] = 'defeat'


def handle_win(game):
    board = game['board']
    for row in range(len(board)):
        for col in range(len(board[0])):
            player_flag = False
            win_flag = False
            for elem in board[row][col]:
                if 'YOU' in elem.states:
                    player_flag = True
                if 'WIN' in elem.states:
                    win_flag = True
            if player_flag and win_flag:
                game['state'] = 'win'


class Tile:
    def __init__(self, name, position, states = None):
        self.name = name
        self.position = position
        self.states = set()
        if name.isupper():
            self.states = {'PUSH'}
        elif name.isupper() == set():
            pass
        else:
            self.states.add(states)
            
    def update_pos(self, position):
        self.position = position
    
    def update_state(self, state):
        self.states.add(state)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

    
if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    gom = new_game([[[], ['snek'], []],[['SNEK'], ['IS'], ['YOU']]])
    print()
    print(gom['positions'])
    print()
    print(gom['effects'])
    print()
    print_board(gom)
    print()
    print(step_game(gom, 'down'))
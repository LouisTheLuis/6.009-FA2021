# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 00:02:21 2021

@author: Louis Martinez
"""
class Env():
    """ 
    Environment class: it contains the variable assignments in a particular environment
    """
    def __init__(self, varis = (), vals = (), parent = None):
        """ 
        Constructor. It has the following arguments:
            varis (list, set): list/set of variable names (str) for which values/functions will be assigned
            vals (list, set): list/set of values (int, float) or functions assigned to a certain name
            parent (Env): the enclosing environment to this particular environment
            
        This constructir will store the following information:
            self.functions (dict): a dictionary containing variable : value assignments
            self.parent (Env): the enclosing environment
        """
        # If both varis and vals list are not empty, check if they have the same length
        # If they do, assign var:val pairs in the self.functions dictionary. If they don't, raise an error
        if varis != () and vals != ():
            if len(varis) == len(vals):
                self.functions = {}
                self.functions.update(zip(varis, vals))
            else:
                raise SnekEvaluationError
        # If both lists are empty the self.functions dictionary remains empty
        else:
            self.functions = {}
        self.parent = parent
    
    def look_var(self, var):
        """ 
        Given a variable, this function returns the dictionary of the environment where that variable has
        a value assigned.
        """
        # BASE CASE: If the variable is in the keys of this evironment, return it
        if var in self.functions.keys():
            return self.functions
        # RECURSIVE CASE: If not, check the parent environment. If there is not parent environment, raise an error
        else:
            if self.parent != None:
                return self.parent.look_var(var)
            else:
                raise SnekNameError
    
    def exists(self, var):
        """ 
        Given a variable, this function returns whether (a boolean) the variable has a value assigned or not.
        """
        # BASE CASE: If the variable is in the keys of this evironment, return True
        if var in self.functions.keys():
            return True
        # RECURSIVE CASE: If not, check the parent environment. If there is not parent environment, raise an error
        else:
            if self.parent != None:
                return self.parent.exists(var)
            else:
                return False
            
            
class SnekError(Exception):
    """
    A type of exception to be raised if there is an error with a Snek
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """
    pass


class SnekSyntaxError(SnekError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """
    pass


class SnekNameError(SnekError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """
    pass


class SnekEvaluationError(SnekError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SnekNameError.
    """
    pass

def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            if x != "#t" and x != "#f" and x != "nil":
                return x
            else:
                if x == "#t":
                    return True
                elif x == "#f":
                    return False
                else:
                    return None


def tokenize(source):
    #print(source)
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Snek
                      expression
    """
    # Gets a list with everything separated
    initial = source.replace('(', ' ( ').replace(')', ' ) ').replace('\n', ' \\n ').replace(';', ' ; ').split()
    
    # Removes the line breaks and the comments
    tokenized = []
    flag = False
    for token in initial:
        if flag:
            if token != '\\n':
                continue
            flag = False
            continue
        if token == ';':
            flag = True
            continue
        if token != '\\n':
            tokenized.append(token)
    return tokenized


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    # If there is a mismatched number of open and closed parentheses, raise a SyntaxError
    if tokens.count("(") != tokens.count(")"):
        raise SnekSyntaxError
        
    # If the list is longer than a single element and there are no parentheses, raise a SyntaxError
    elif len(tokens) > 1 and (tokens[0] != "(" and tokens[-1] != ")"):
        raise SnekSyntaxError
        
    def parse_expression(index):
        """ 
        Given an index, it recursively constructs a parsed LISP expression from its tokenized list.
        """
        # BASE CASE
        # If the element at index is a closed parentheses, that is a SyntaxError
        if tokens[index] == ")":
            raise SnekSyntaxError
        # If the element at index is not an open parentheses, return a tuple (element, index + 1)
        elif tokens[index] != "(":
            return (number_or_symbol(tokens[index]), index + 1)
        
        
        # RECURSIVE CASE
        # if tokens[index] == "(":
        else:           
            branch = []
            last_index = index + 1
            # Create a new branch and check recursively all the following elements until you reach a closed
            # parentheses. Append those checked elements to the current branch
            while tokens[last_index] != ")":
                val = parse_expression(last_index)
                branch.append(val[0])
                last_index = val[1]
                
            # Skip the closed parentheses
            last_index += 1
            
            # If the branch is empty, ignore
            if len(branch) == 0:
                pass
            
            ###########################
            # If the first element of the branch is a special form, check that is structure is correct:
            #   define: the second element must be a string or a non-empty list of strings
            #   lambda: the second element must be a list of strings
            # If these conditions are not met, raise a SyntaxError
            ###########################
            elif branch[0] == "define":
                if len(branch) == 3:
                    if isinstance(branch[1], str):
                        pass
                    elif isinstance(branch[1], list):
                        if len(branch[1]) != 0:
                            for elem in branch[1]:
                                if isinstance(elem, str):
                                    pass
                                else:
                                    raise SnekSyntaxError
                        else:
                            raise SnekSyntaxError
                    else:
                        raise SnekSyntaxError
                else:
                    raise SnekSyntaxError
            
            elif branch[0] == "lambda":
                if len(branch) == 3:
                    if isinstance(branch[1], list):
                        for elem in branch[1]:
                            if isinstance(elem, str):
                                pass
                            else:
                                raise SnekSyntaxError
                    else:
                        raise SnekSyntaxError
                else:
                    raise SnekSyntaxError
            
            elif branch[0] == "if":
                if len(branch) == 4:
                    pass
                else:
                    raise SnekSyntaxError
            
            # Return a tuple (branch list, last index)
            return (branch, last_index)
            
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

tree = "(let ((x 5) (y 3)) (+ x y z))"
rel = parse(tokenize(tree))
print(rel)
local = rel[1]
body = rel[2]
varis = []
vals = []
for pair in local:
    varis.append(pair[0])
    vals.append(pair[1])
    
    
print(varis)
print(vals)

new_env = Env(varis, vals)
print(new_env.functions)
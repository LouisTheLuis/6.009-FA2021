#!/usr/bin/env python3
"""6.009 Lab 8: Snek Interpreter"""

import doctest

# NO ADDITIONAL IMPORTS!

###########################
# Snek-related Exceptions #
###########################


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


######################
# Built-in Functions #
######################


def mul(args):
    """ 
    Given a list of arguments, it will perform the product of all of its elements.
    """
    # If there are no elements in the list return 1
    if len(args) == 0:
        return 1
    # If there is a single element in the list return that element
    elif len(args) == 1:
        return args[0]
    # Recursive call: multiply the first element by the product of the rest of the elements
    else:
        return args[0] * mul(args[1:])
    

def div(args):
    """ 
    Given a list of arguments, it will perform the quotient of the first element by the rest. 
    """
    # If there are no elements in the list raise a SyntaxError
    if len(args) == 0:
        raise SyntaxError
    # If there is a single non-zero element in the list, return 1/element. Else, raise ZeroDivisionError
    if len(args) == 1:
        if args[0] != 0:
            return 1/args[0]
        else:
            raise ZeroDivisionError
    # If there are two elements on the list and the second is non-zero, return first/second. Else, raise an error
    if len(args) == 2:
        if args[1] != 0:
            return args[0]/args[1]
        else:
            raise ZeroDivisionError
    # Recursive call: divide the first element iteratively by the following non-zero elements
    # If there is a zero element, raise an error
    else:
        current = args[0]
        for arg in args[1:]:
            if arg != 0:
                current = current / arg
            else:
                raise ZeroDivisionError
        return current


snek_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": mul,
    "/": div
}


######################
# Environments Class #
######################


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

    def update(self, name, args, env):
        """ 
        Given a name, a list of arguments and a environment, this function will update the environment
        self.functions dictionary to assign the name to the arguments.
        """
        self.functions[name] = evaluate(args, env)
        return self.functions[name]
    
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
                raise SnekEvaluationError


# We create an environment for the built-in functions
built_ins = Env()
built_ins.functions.update(snek_builtins)


class Function():
    """ 
    Function class: it stores a particular function procedure.
    """
    def __init__(self, variables, proc, environment):
        """ 
        Constructor. It has the following arguments (and stored information):
            variables (list/set): a list/set of variable names (str) for which values will be assigned
            environment (Env): the environment where the function is defined
            proc (list): parsed list describing a certain procedure in LISP
        """
        self.variables = variables
        self.environment = environment
        self.proc = proc
    
    def __call__(self, args):
        """ 
        Given, a list of arguments, 
        this function works when the instance is called. It evaluates the procedure in a new environment
        that has the current Function environment as its parent and with var:vals assignments.
        """
        return evaluate(self.proc, Env(self.variables, args, self.environment))


############################
# Tokenization and Parsing #
############################


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
            return x


def tokenize(source):
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
            
            # Return a tuple (branch list, last index)
            return (branch, last_index)
            
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression


##############
# Evaluation #
##############


def evaluate(tree, environment = None):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
        environment (Env class)
    """
    # If there is no enclosing environment, create one with the built-ins as parents
    if environment == None:
        environment = Env((), (), built_ins)
        
    # If the tree is a number, return it
    if isinstance(tree, int) or isinstance(tree, float):
        return tree
    
    # If the tree is a string, look up its value on the environment (raising an error if it's not there)
    elif isinstance(tree, str):
        return environment.look_var(tree)[tree]
            
    # IF THE TREE IS A LIST
    # If its first element contains a 'define'        
    elif tree[0] == "define":
        # If the second element is a list, then it is a function definition
        # Take the name (first element of that list) and the variables (rest of elements of that list)
        # and create a list in proper function form: [lambda, variables, procedure]
        # Set the name to contain that function definition in the environment
        if isinstance(tree[1], list):
            name = tree[1][0]
            variables = tree[1][1:]
            arguments = ['lambda', variables, tree[2]]
            return environment.update(name, arguments, environment)
        # If the second element is a string, take the name (2nd element) and its argument (3rd element)
        # and set the name to contain that argument in the environment
        else:
            name = tree[1]
            arguments = tree[2]
            return environment.update(name, arguments, environment)
    
    # If the first element contains a 'lambda'
    # Take its variables (2nd element) and its procedure (3rd element) and create a Function instance in the
    # current environment
    elif tree[0] == "lambda":
        variables = tree[1]
        procedure = tree[2]
        return Function(variables, procedure, environment)
    
    # If the first element is a list
    # Then, this tree represents a function call. Evaluate it first element to get the function and 
    # the rest of the elements to get the arguments. Then, return the function call with those same
    # arguments
    if isinstance(tree[0], list):
        func = evaluate(tree[0], environment)
        args = [evaluate(arg, environment) for arg in tree[1:]]
        return func(args)
    
    # If the tree contains no special forms, then it is also a function call
    else:
        # Check if the function name is in the environment or parent environments
        # If it is, get the function procedure, the arguments, and call it
        if environment.exists(tree[0]):
            func = evaluate(tree[0], environment)
            args = [evaluate(arg, environment) for arg in tree[1:]]
            return func(args)
    

def REPL():
    """
    The REPL of Snek. It runs until it gets to an exception, in which case, it reruns again.
    It stops when it is input QUIT.
    """
    n = 0
    environment = Env((), (), built_ins)
    flag = True
    while flag:
        try:
            statement = input(" in >> ")
            if statement != "QUIT":
                result = evaluate(parse(tokenize(statement)), environment)
                print("out >> " + str(result))
            else:
                flag = False
        except Exception as e:
            print(repr(e))


def result_and_env(tree, environment = None):
    """ 
    Given a tree and an environment (unless it doesn't have one, in which case is the global), it returns
    a tuple with the evaluated expression and the environment where it happened.
    """
    
    if environment == None:
        environment = Env((), (), built_ins)
    evaluated_exp = evaluate(tree, environment)
    result = (evaluated_exp, environment)
    return result


######################################################
# Main (where functions are run, including the REPL) #
######################################################


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    REPL()
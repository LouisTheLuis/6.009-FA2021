"""6.009 Lab 9: Snek Interpreter Part 2"""

import sys
sys.setrecursionlimit(10_000)

import doctest
# NO ADDITIONAL IMPORTS!
####################
# Helper Functions #
####################


def is_list(var):
    """ 
    Checks if the variable given is an instance of a list in Snek. Returns True if it is, and False if it is not.
    """
    # Checks if the instance is a Pair variable. If its tail is None, it's a list. If its tail is a Pair
    # instance, recursively check its tail. If the head is None, return False. And if the tail is not None,
    # return False
    if isinstance(var, Pair):
        if var.get_tail() == None:
            return True
        elif isinstance(var.get_tail(), Pair):
            return is_list(var.get_tail())
        elif var.get_head() == None:
            return False
        else:
            return False
    # If the variable is None (our representation of nil) then return True (it would be an empty list)
    elif var == None:
        return True
    # If the variable is not None or a Pair instance, return False
    return False


def evaluate_file(filename, environment = None):
    """ 
    This function allows us to read snek files in a given environment. 
    """
    if environment == None:
        environment = Env((), (), built_ins)
    with open(filename, mode='r') as file:
        data = file.read()
        return evaluate(parse(tokenize(data)), environment)


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


def equal_to(args):
    """ 
    Give a list of arguments, it will check whether they are all equal.
    """
    # If less than 2 elements are given, raise an Error
    if len(args) < 2:
        raise SnekEvaluationError
    # Check all the argument pairs; if any pair is not mutually equal, then return False. Else, return True.
    else:
        for i in range(len(args) - 1):
            if args[i] == args[i + 1]:
                pass
            else:
                return False
        return True


def decreasing(args):
    """ 
    Given a list of arguments, it will check whether they are in decreasing order.
    """
    # If less than 2 elements are given, raise an Error
    if len(args) < 2:
        raise SnekEvaluationError
    # Check all the argument pairs; if any pair is not strictly decreasing, then return False. Else, return True.
    else:
        for i in range(len(args) - 1):
            if args[i] > args[i + 1]:
                pass
            else:
                return False
        return True


def nonincreasing(args):
    """ 
    Given a list of arguments, it will check whether they are in nonincreasing order.
    """
    # If less than 2 elements are given, raise an Error.
    if len(args) < 2:
        raise SnekEvaluationError
    # Check all the argument pairs; if any pair is not succesively greater or equal to the next, return False.
    # Else, return True.
    else:
        for i in range(len(args) - 1):
            if args[i] >= args[i + 1]:
                pass
            else:
                return False
        return True
    

def increasing(args):
    """ 
    Given a list of arguments, it will check whether they are in increasing order.
    """
    # If less than 2 elements are given, raise an Error
    if len(args) < 2:
        raise SnekEvaluationError
    # Check all the argument pairs; if any pair is not strictly increasing, return False. Else, return True.
    else:
        for i in range(len(args) - 1):
            if args[i] < args[i + 1]:
                pass
            else:
                return False
        return True


def nondecreasing(args):
    """ 
    Given a list of arguments, it will check whether they are in nondecreasing order.
    """
    # If less than 2 elements are given, raise an Error.
    if len(args) < 2:
        raise SnekEvaluationError 
    # Check all the argument pairs; if any pair is not succesively smaller or equal to the next, return False.
    # Else, return True.
    else:
        for i in range(len(args) - 1):
            if args[i] <= args[i + 1]:
                pass
            else:
                return False
        return True


def negation(args):
    """ 
    Given an argument, it returns the opposite boolean.
    """
    # Checks if the list of arguments has length 1. If it doesn't, it raises an Error.
    if len(args) != 1:
        raise SnekEvaluationError
    else:
        result = not args[0]
        return result


def pair(args):
    """ 
    Given two arguments, it returns a Pair instance, with the first element being its head and the second
    being its tail.
    """
    # Checks if the list of arguments has length 2. If it doesn't, it raises an Error.
    if len(args) != 2:
        raise SnekEvaluationError
    else:
        return Pair(args[0], args[1])


def head(args):
    """ 
    Given a Pair instance, it returns its head.
    """
    # Checks if the list has length 1 or is not an instance of a Pair class. If it's neither, it raises an Error.
    if len(args) != 1 or not isinstance(args[0], Pair):
        raise SnekEvaluationError
    else:
        return args[0].get_head()


def tail(args):
    """ 
    Given a Pair instance, it returns its tail.
    """
    # Checks if the list has length 1 or is not an instance of a Pair class. If it's neither, it raises an Error.
    if len(args) != 1 or not isinstance(args[0], Pair):
        raise SnekEvaluationError
    else:
        return args[0].get_tail()


def listo(args):
    """ 
    Given a list of arguments, it returns a linked list of all its elements.
    """
    # BASE CASE
    # If the list of arguments has length 0, return None.
    if len(args) == 0:
        return None
    # RECURSIVE CASE
    # Returns a Pair instance, with the first element as its head, and a list of the rest of arguments
    # as its tail.
    else:
        return Pair(args[0], listo(args[1:]))
    

def length(lst):
    """ 
    Given a Snek list, it returns the length of that list.
    """
    # If the argument list has length other than 1, raises an error. Else, we take its only element as the 
    # list variable.
    if len(lst) != 1:
        raise SnekEvaluationError
    else:
        variable = lst[0]
    # If the list variable is not a Pair instance or None, raise an Error.
    if not isinstance(variable, Pair) and variable != None:
        raise SnekEvaluationError 
    # RECURSIVE FUNCTION:
    # If the variable is None, returns 0. If the tail is None, return 1. If it's another Pair variable, then
    # return 1 plus the length of the rest of the list.
    # If none of these conditions are held, then we don't have a list, and we raise an Error.
    else:
        if variable == None:
            return 0
        if variable.get_tail() == None:
            return 1
        if isinstance(variable.get_tail(), Pair):
            return 1 + length([variable.get_tail()])
        else:
            raise SnekEvaluationError


def nth(args, current_ind = 0):
    """ 
    Given a Snek list and an index, we return the element at that index.
    """
    # If the list of arguments is not 2, we raise an Error. Else, we check if the first argument 
    # is a list (otherwise raising an Error) and take the second argument as the index.
    if len(args) != 2:
        raise SnekEvaluationError 
    else:
        lst = args[0]
        index = args[1]
    if not isinstance(lst, Pair):
        raise SnekEvaluationError
    else:
        # If the tail is ever not None nor a Pair instance and the index is not 0, we raise an Error.
        if lst.get_tail() != None and not isinstance(lst.get_tail(), Pair) and index != 0:
            raise SnekEvaluationError
        # BASE CASE
        # If the index corresponds to the current index, we return the head.
        if index == current_ind:
            return lst.get_head()
        # RECURSIVE CASE
        # We call nth in the tail (given that it's a Pair instance) with the rest of the list.
        else:
            if lst.get_tail() != None:
                return nth([lst.get_tail(), index], current_ind + 1)
            else:
                raise SnekEvaluationError


def concat(args):
    """ 
    Given multiple Snek lists, we return a single new concatenated list.
    """
    # If the length of the argument list is 0, return None.
    if len(args) == 0:
        return None
    
    else:
        # We initialize a new list, a pointer for the arguments and a pointer for the new list.
        new_lst = None
        p_args = None
        p_new = None
        
        # For every list in the arguments...
        for lst in args:
            # If the list is nil, ignore it.
            if lst == None:
                continue
            
            # If the element is not a list, raise an Error.
            if not is_list(lst):
                raise SnekEvaluationError 
                
            else:
                # If the new list is still None, turn it into a Pair instance with a placeholder.
                # We turn the new list pointer to this new_list instance.
                if new_lst == None:
                    new_lst = Pair(lst.head, 'placeholder')
                    p_new = new_lst
                
                # If the new list is not None, we turn its tail into a Pair instance, with the lst head as its 
                # head. Then we turn the new list pointer to this new tail.
                else:
                    p_new.tail = Pair(lst.head, None)
                    p_new = p_new.tail
                
                # We turn the pointer for the arguments to point at the beginning of the current list.
                p_args = lst
                
                # Then, until the argument pointer has None as its tail...
                while p_args.tail != None:
                    # We set the argument pointer to its tail
                    p_args = p_args.tail
                    # We introduce a new tail to the new list by taking the head of the argument pointer
                    p_new.tail = Pair(p_args.head, None)
                    # We change the new list pointer to point to this new tail
                    p_new = p_new.tail
                
                # If the new list still has a placeholder, change that placeholder to None.
                if new_lst.tail == 'placeholder':
                    new_lst.tail = None
                    
        return new_lst


def mapping(args):
    """ 
    Given a function and a Snek list, it returns a new Snek list containing the result of applying
    the function to each element of the list.
    """
    # Checks if the list of arguments is not 2, in that case raising an Error. 
    if len(args) != 2:
        raise SnekEvaluationError
    else:
        function = args[0]
        lst = args[1]
        
    # If the first element is not a list and the second is not a function, raise an Error too.
    if not is_list(lst) or (not isinstance(function, Function) and not callable(function)):
        raise SnekEvaluationError 
    
    # If the list is nil, return None.
    if lst == None:
        return None
    
    # Using a pointer that checks every element of the list and a direction pointer that adds new elements to 
    # the new list, we check every element of the Snek list and add a new element equal to the function
    # applied to the element at that index in the Snek list.
    else:
        new_list = None
        direction = None
        pointer = lst
        for i in range(length([lst])):
            if i == 0:
                new_list = Pair(function([pointer.get_head()]), None)
                direction = new_list
                pointer = lst.get_tail()
            else:
                direction.set_tail(Pair(function([pointer.get_head()]), None))
                direction = direction.get_tail()
                pointer = pointer.get_tail()
        return new_list


def filtering(args):
    """ 
    Given a boolean function and a Snek list, it returns a new list only containing those elements
    for which the boolean function returns True.
    """
    # Checks if the list of arguments is not 2, in that case raising an Error. 
    if len(args) != 2:
        raise SnekEvaluationError
    else:
        function = args[0]
        lst = args[1]
    
    # If the first element is not a list and the second is not a function, raise an Error too.
    if not is_list(lst) or (not isinstance(function, Function) and not callable(function)):
        raise SnekEvaluationError
    
    # Using the same method as in mapping, we check every element on the Snek list, this time only adding them
    # to the new list when the function returns True for the current element of the list.
    else:
        new_list = None
        direction = None
        pointer = lst
        for i in range(length([lst])):
            if new_list == None:
                if function([pointer.get_head()]):
                    new_list = Pair(pointer.get_head(), None)
                    direction = new_list
                    pointer = pointer.get_tail()
                else:
                    pointer = pointer.get_tail()
            else:
                if function([pointer.get_head()]):
                    direction.set_tail(Pair(pointer.get_head(), None))
                    direction = direction.get_tail()
                    pointer = pointer.get_tail()
                else:
                    pointer = pointer.get_tail()
        return new_list


def reducing(args):
    """ 
    Given a function, a Snek list, and an initial value, it returns the result of succesively applying
    this function to all elements of this list.
    """
    # If the argument list does not have length 3, raise an Error. Else, we take the first element as the
    # function, the second as the list, and the third as the initial value.
    if len(args) != 3:
        raise SnekEvaluationError
    else:
        function = args[0]
        lst = args[1]
        initval = args[2]
    # If the second arguments is not a list, or the first element not a function, we raise an Error.
    if not is_list(lst) or (not isinstance(function, Function) and not callable(function)):
        raise SnekEvaluationError
    # We take the result to be the initial value. Then, we get a pointer that will succesively point to every
    # following element of the Snek list until reaching its end. For every element in the Snek list, we apply
    # the function with the previous result.
    # Finally, we return that result.
    else:
        result = initval
        pointer = lst
        while pointer != None:
            result = function([result, pointer.get_head()])
            pointer = pointer.get_tail()
        return result
    
    
def beginning(args):
    """ 
    Given a list of arguments, it returns the last one.
    """
    return args[-1]


snek_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": mul,
    "/": div,
    "=?": equal_to,
    ">": decreasing,
    ">=": nonincreasing,
    "<": increasing,
    "<=": nondecreasing,
    "not": negation,
    "pair": pair,
    "head": head,
    "tail": tail,
    "list": listo,
    "length": length,
    "nth": nth,
    "concat": concat,
    "map": mapping,
    "filter": filtering,
    "reduce": reducing,
    "begin": beginning
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
        # RECURSIVE CASE: If not, check the parent environment. If there is not parent environment, return False
        else:
            if self.parent != None:
                return self.parent.exists(var)
            else:
                return False


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


class Pair():
    """
    Pair class: it stores a pair (head, tail). Used for list representations in Snek.
    """
    def __init__(self, head, tail):
        """ 
        Constructor. It has the following arguments (and stored information):
            head = head element of the Pair
            tail = tail element of the Pair
        """
        self.head = head
        self.tail = tail
    
    # The following are functions used to modify a certain pair.
    def get_head(self):
        return self.head
    
    def get_tail(self):
        return self.tail
    
    def set_head(self, new_head):
        self.head = new_head
    
    def set_tail(self, new_tail):
        self.tail = new_tail
    
    def get_last(self):
        """ 
        If a function is a linked list of elements, this list will return the last element of that list
        or raise an Error if it is not a linked list.
        """
        if self.tail == None:
            return self
        elif isinstance(self.tail, Pair):
            return self.tail.get_last()
        else:
            raise SnekEvaluationError


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
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Snek
                      expression
    """
    #print(source)
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
    if tree == []:
        raise SnekEvaluationError
        
    # If there is no enclosing environment, create one with the built-ins as parents
    if environment == None:
        environment = Env((), (), built_ins)
    
    # If the tree is a number, return it
    if isinstance(tree, int) or isinstance(tree, float) or tree == None:
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
        if isinstance(tree[1], type([])):
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
    
    # If the first element contains a 'if'
    # Take the condition, the consequence if True and the consequence if False
    # Then, return the evaluation of the corresponding consequence of the condition
    elif tree[0] == "if":
        condition = tree[1]
        conseq = tree[2]
        els_conseq = tree[3]
        exp = conseq if evaluate(condition, environment) else els_conseq
        return evaluate(exp, environment)
    
    # If the first element contains an 'and'
    # Take every following condition and evaluate them. If any of them is False, return False. Else, return
    # True.
    elif tree[0] == "and":
        flag = True
        for condition in tree[1:]:
            if evaluate(condition, environment):
                pass
            else: 
                flag = False
                break
        return flag
    
    # If the first element contains an 'or'
    # Take every following condition and evaluate them. If any of them is True, return True. Else, return False.
    elif tree[0] == "or":
        flag = False
        for condition in tree[1:]:
            if evaluate(condition, environment):
                flag = True
                break
            else: 
                pass
        return flag
    
    # If the first element contains a 'del'
    # Take the variable given, and check if it is in the current environment. If it is, deleted it and return it.
    # Else, raise a Name Error.
    elif tree[0] == "del":
        var = tree[1]
        if tree[1] in environment.functions:
            return environment.functions.pop(tree[1])
        else:
            raise SnekNameError
    
    # If the first element contains a 'let'
    # Take the pair elements in local and the body function. Then, create a new environment with the
    # local pair bindings and evaluate the body in that environment.
    elif tree[0] == "let":
        local = tree[1]
        body = tree[2]
        varis = []
        vals = []
        for pair in local:
            varis.append(pair[0])
            vals.append(evaluate(pair[1], environment))
        new_env = Env(varis, vals, environment)
        return evaluate(body, new_env)
    
    # If the first element contains a 'set!'
    # Evaluate the third element (the body) in the current environment. Then, set the given variable
    # to be equal to the result of the previous evaluation in the closest enclosing environment.
    elif tree[0] == "set!":
        var = tree[1]
        val = evaluate(tree[2], environment)
        environment.look_var(var)[var] = val
        return val
        
    # If the first element is a list
    # Then, this tree represents a function call. Evaluate it first element to get the function and 
    # the rest of the elements to get the arguments. Then, return the function call with those same
    # arguments
    if isinstance(tree[0], type([])):
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
        # If not, check if it is a name, if it is, raise a Name Error
        # If it's not a name, raise an Evaluation Error
        else:
            if isinstance(tree[0], str):
                raise SnekNameError
            else:
                raise SnekEvaluationError
    

def REPL(environment = None):
    """
    The REPL of Snek. It runs until it gets to an exception, in which case, it reruns again.
    It stops when it is input QUIT.
    """
    if environment == None:
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
            #raise e

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
"""new_env = Env((), (), built_ins)

# This is the thing that allows Python to open snek files in the command-line
if 'test.py' not in sys.argv:
    if len(sys.argv) > 1:
        global_env = Env((), (), built_ins)
        args = sys.argv[1:]
        for arg in args:
             evaluate_file(arg, new_env)

REPL(new_env)"""

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    pass
    #REPL()
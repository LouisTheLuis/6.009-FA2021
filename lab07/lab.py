import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.

### HELPER FUNCTION ####
significants = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
symbols = {"+", "-", "/", '*', "(", ")"}
op = {"+", "-", "/", "*"}
alphabet = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 
            'h', 'i', 'j', 'k', 'l', 'm', 'n', 
            'o', 'p', 'q', 'r', 's', 't', 'u', 
            'v', 'w', 'x', 'y', 'z', 'A', 'B', 
            'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 
            'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}


def tokenize(formula):
    """ 
    Takes a string representing a formula and returns a list with every single element of that formula
    separated.
    """
    tokens = []
    # Temporary string used to append elements of several characters (negative numbers, etc)
    temp = ""
    # For every element in the formula...
    for i in range(len(formula)):
        # Ignore white spaces
        if formula[i] == " ":
            pass
        # If the element is a digit, check if the next digit is a digit too. If it is, then append 
        # it to the temporary string. If not, then append the temporary string to the tokenized list and
        # restart the temporary string.
        elif formula[i] in significants:
            if i < len(formula) - 1 and formula[i + 1] in significants:
                temp += formula[i]
            else:
                temp += formula[i]
                tokens.append(temp)
                temp = ""
        # If the element is a minus sing, check if the next element is a digit. If it is, then append to
        # the temporary string. If not, then append the sign to the tokenized list.
        elif formula[i] == "-" and i > 0 and i < len(formula) - 1:
            if formula[i + 1] in significants:
                temp += formula[i]
            else:
                tokens.append(formula[i])
        # Append all other elements to the tokenized list.
        else:
            tokens.append(formula[i])
    
    # Loop through all elements in the tokenized list to look for double * to join.
    j = 0
    while j < len(tokens):
        if j < len(tokens) - 1:
            if tokens[j] == "*" and tokens[j + 1] == "*":
                tokens[j] = "**"
                tokens.pop(j + 1)
        j += 1
    return tokens

def is_number(expression):
    """ 
    Given a string expression, this function will return whether the expression is an integer or not.
    """
    try:
        result = int(expression)
        return True
    except:
        return False

def parse(tokens):
    """
    Given a tokenized list, it returns the parsed Symbol expression.
    """
    def parse_expression(index):
        """ 
        Given an index, it recursively constructs a parsed Symbol expression from the tokenized list.
        """
        # BASE CASES
        # CASE 1: THE EXPRESSION IS A NUMBER
        # If the token at index is an integer, return it with the next index.
        if is_number(tokens[index]):
            return (Num(int(tokens[index])), index + 1)
        # CASE 2: THE EXPRESSION IS A VARIABLE
        # If the token at index is a variable, return it with the next index.
        if tokens[index] in alphabet:
            return (Var(tokens[index]), index + 1)
        # RECURSIVE CASE: THE EXPRESSION IS AN OPERATION
        # Activated if the token at index is an open parentheses.
        if tokens[index] == "(":
            # Parse the left part of the expression recursively.
            left_value = parse_expression(index + 1)
            right_value = None
            operation = ""
            
            # Get the last index of the left part. The last index must be after the last parenthesis of the
            # left part, corresponding to the operation connecting the left part and right part.
            last_index = left_value[1]
            while tokens[last_index] == ")":
                last_index += 1
            operation = tokens[last_index]
            
            # Parse the right part (index after the operation) of the expression recursively.
            right_value = parse_expression(last_index + 1)
            
            # Check which operation to perform and returns that operation with the last index.
            if operation == "+":
                return (Add(left_value[0], right_value[0]), right_value[1])
            elif operation == "-":
                return (Sub(left_value[0], right_value[0]), right_value[1])
            elif operation == "*":
                return (Mul(left_value[0], right_value[0]), right_value[1])
            elif operation == "/":
                return (Div(left_value[0], right_value[0]), right_value[1])
            else:
                return (Pow(left_value[0], right_value[0]), right_value[1])
            
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

def sym(expression):
    """ 
    Given a symbolic String expression, it returns a parsed Symbol expression representing it.
    """
    # Tokenizes the expression and parses it through helper functions.
    new = tokenize(expression)
    return parse(new)

class Symbol:
    ##### OPERATOR FUNCTIONS #####
    # Including the reverse versions, which appropriately call their original function reversed.
    def __add__(self, other):
        return Add(self, other)
    
    def __radd__(self, other):
        if type(other) == str:
            return Add(Var(other), self)
        else:
            return Add(Num(other), self)
    
    def __sub__(self, other):
        return Sub(self, other)
    
    def __rsub__(self, other):
        if type(other) == str:
            return Sub(Var(other), self)
        else:
            return Sub(Num(other), self)
    
    def __mul__(self, other):
        return Mul(self, other)
    
    def __rmul__(self, other):
        if type(other) == str:
            return Mul(Var(other), self)
        else:
            return Mul(Num(other), self)
    
    def __truediv__(self, other):
        return Div(self, other)
    
    def __rtruediv__(self, other):
        if type(other) == str:
            return Div(Var(other), self)
        else:
            return Div(Num(other), self)
    
    def __pow__(self, other):
        return Pow(self, other)
    
    def __rpow__(self, other):
        if type(other) == str:
            return Pow(Var(other), self)
        else:
            return Pow(Num(other), self)
    #####################################
        
    def deriv(self, var):
        """ 
        Performs the derivative of the self Symbol with respect to the var variable, returning a 
        new Symbol expression.
        """
        # Derivative of a constant is 0
        if (isinstance(self, Var) and str(self) != var) or isinstance(self, Num):
            return Num(0)
        # Derivative of a variable is 1
        elif isinstance(self, Var) and str(self) == var:
            return Num(1)
        # Sum rule 
        elif isinstance(self, Add):
            return Add(self.left.deriv(var), self.right.deriv(var))
        # Difference rule
        elif isinstance(self, Sub):
            return Sub(self.left.deriv(var), self.right.deriv(var))
        # Product rule
        elif isinstance(self, Mul):
            left = Mul(self.left, self.right.deriv(var))
            right = Mul(self.right, self.left.deriv(var))
            return Add(left, right)
        # Division rule
        elif isinstance(self, Div):
            left = Mul(self.right, self.left.deriv(var))
            right = Mul(self.left, self.right.deriv(var))
            up = Sub(left, right)
            down = Mul(self.right, self.right)
            return Div(up, down)
        # Power rule
        elif isinstance(self, Pow):
            if not isinstance(self.right, Num):
                raise TypeError
            else:
                left = Mul(self.right, Pow(self.left, self.right - 1))
                right = self.left.deriv(var)
            return Mul(left, right)
    
    def eval(self, mapping):
        left = self.left
        right = self.right
        
        # Base Case:
        # If both sides are either Num or Var, check the sides. For each variable contained in the 
        # dictionary, replace it with the value and perform an operation if possible.
        if (isinstance(left, Num) or isinstance(left, Var)) and (isinstance(right, Num) or isinstance(right, Var)):
            if isinstance(left, Var) and isinstance(right, Var):
                if left.name in mapping.keys() and right.name in mapping.keys():
                    return self.oper(mapping[left.name], mapping[right.name])
                else:
                    return self.oper(left, right)
            elif isinstance(left, Var):
                if left.name in mapping.keys():
                    return self.oper(mapping[left.name], right.n)
                else:
                    return self.oper(left, right)
            elif isinstance(right, Var):
                if right.name in mapping.keys():
                    return self.oper(left.n, mapping[right.name])
                else:
                    return self.oper(left, right)
            else:
                return self.oper(left.n, right.n)
            
        # Recursive Step
        if isinstance(self, Add):   
            return (left.eval(mapping) + right.eval(mapping))
        if isinstance(self, Sub):
            return (left.eval(mapping) - right.eval(mapping))
        if isinstance(self, Mul):
            return (left.eval(mapping) * right.eval(mapping))
        if isinstance(self, Div):
            return (left.eval(mapping) / right.eval(mapping))
        if isinstance(self, Pow):
            return (left.eval(mapping) ** right.eval(mapping))
    
    def getorder(self):
        return self.order
        
class BinOp(Symbol):
    def __init__(self, left, right):
        """ 
        Initializer. Stores a left expression and a right expression of the binary operation.
        For each side expression, it checks whether it is a Number, a Variable, or another expression in itself.
        """
        if type(left) == int or type(left) == float:
            self.left = Num(left)
        elif type(left) == str:
            self.left = Var(left)
        else:
            self.left = left
            
        if type(right) == int or type(right) == float:
            self.right = Num(right)
        elif type(right) == str:
            self.right = Var(right)
        else:
            self.right = right

    def __str__(self, operand):
        """ 
        Returns the string representation of the binary operator.
        """
        # Gets the order of operations of the left side, right side, and of the operand itself (orig).
        # The order of operations is registered as follows: 
        # 99 for Num and Var, 3 for Pow, 2 for Mul and Div, 1 for Add and Sub.
        lorder = self.left.getorder()
        rorder = self.right.getorder()
        orig = self.getorder()
        # Recursively calls the str function on the left and right expressions.
        left = str(self.left)
        right = str(self.right)
        
        # Checks whether either side has lower order of operations than the operand. If a side has, then it 
        # is enclosed in parentheses.
        if lorder < orig:
            left = "(" + str(self.left) + ")"
        if rorder < orig:
            right = "(" + str(self.right) + ")"
        # Special case: if the operand is a division or a substraction and the operand has similar order of
        # operations as the right side, then enclose the right side in parentheses.
        if operand in {"-", "/"} and rorder == orig:
            right = "(" + str(self.right) + ")"
        # If the operand is an exponentiation and the left side is not a Num or a Var, then the left side
        # is enclosed in parentheses.
        if orig == 3 and lorder <= orig:
            left = "(" + str(self.left) + ")"
                
        return left + " " + operand + " " + right
    
    def __repr__(self, operation):
        """ 
        Returns the repr of the binary operation.
        """
        return operation + "(" + repr(self.left) + ", " + repr(self.right) + ")"

    def simplify(self, operation):
        simp_left = self.left.simplify()
        simp_right = self.right.simplify()
        
        if operation == "+":
            # If both sides are numbers, add them up.
            if isinstance(simp_left, Num) and isinstance(simp_right, Num):
                return Num(simp_left.n + simp_right.n)
            # If the left side is 0, return the right side. If not, keep returning the sum.
            elif isinstance(simp_left, Num):
                if simp_left.n == 0:
                    return simp_right.simplify()
                else:
                    return Add(simp_left, simp_right.simplify())
            # If the right side is 0, return the right side. If not, keep returning the sum. 
            elif isinstance(simp_right, Num):
                if simp_right.n == 0:
                    return simp_left.simplify()
                else:
                    return Add(simp_left.simplify(), simp_right)
            # If both sides are not Num, then return the Add expression.
            else:
                return Add(simp_left.simplify(), simp_right.simplify())
        
        elif operation == "-":
            # If both sides are numbers, substract them.
            if isinstance(simp_left, Num) and isinstance(simp_right, Num):
                return Num(simp_left.n - simp_right.n)
            # If THE RIGHT SIDE is 0, then return the left side. Else, return the simplified Sub expression.
            elif isinstance(simp_right, Num):
                if simp_right.n == 0:
                    return simp_left.simplify()
                else:
                    return Sub(simp_left.simplify(), simp_right)
            # If neither are numbers, just return the simplified Sub expression.
            else:
                return Sub(simp_left.simplify(), simp_right.simplify())
        
        elif operation == "*":
            # If both sides are numbers, multiply them.
            if isinstance(simp_left, Num) and isinstance(simp_right, Num):
                return Num(simp_left.n * simp_right.n)
            # If the left side is 0, return 0. If the left side is 1, return the right side. Else, return the
            # simplified Mul expression.
            elif isinstance(simp_left, Num):
                if simp_left.n == 0:
                    return Num(0)
                elif simp_left.n == 1:
                    return simp_right.simplify()
                else:
                    return Mul(simp_left, simp_right.simplify())
            # If the right side is 0, return 0. If the right side is 1, return the left side. Else, return the
            # simplified Mul expression.
            elif isinstance(simp_right, Num):
                if simp_right.n == 0:
                    return Num(0)
                elif simp_right.n == 1:
                    return simp_left.simplify()
                else:
                    return Mul(simp_left.simplify(), simp_right)
            # If neither side is a number, return the simplified Mul expression.
            else:
                return Mul(simp_left.simplify(), simp_right.simplify())
        
        elif operation == "/":
            # If both sides are numbers and the right side is not 0, then divide them.
            if isinstance(simp_left, Num) and isinstance(simp_right, Num):
                if simp_right.n != 0:
                    return Num(simp_left.n / simp_right.n)
            # If the left side is 0, return 0.
            elif isinstance(simp_left, Num):
                if simp_left.n == 0:
                    return Num(0)
                else:
                    return Div(simp_left, simp_right.simplify())
            # If the right side is 1, return the left side.
            elif isinstance(simp_right, Num):
                if simp_right.n == 1:
                    return simp_left.simplify()
                else:
                    return Div(simp_left.simplify(), simp_right)
            # Else, return the simplified Div expression.
            else:
                return Div(simp_left.simplify(), simp_right.simplify())
        
        else:
            # If both sides are numbers and none are 0 and the right side is not 1, return left ** right.
            if isinstance(simp_left, Num) and isinstance(simp_right, Num):
                if simp_right.n != 0 and simp_right.n != 1 and simp_left.n != 0:
                    return Num(simp_left.n ** simp_right.n)
            # If the right side is 0, return 1. If the right side is 1, return the left side.
            if isinstance(simp_right, Num):
                if simp_right.n == 0:
                    return Num(1)
                if simp_right.n == 1:
                    return simp_left.simplify()
            # If the left side is 0, return 0.
            if isinstance(simp_left, Num):
                if simp_left.n == 0:
                    return Num(0)
            # Else, return the simplified Pow expression.
            else: 
                return Pow(simp_left.simplify(), simp_right.simplify())
            
    
    def oper(self, left, right):
        if isinstance(self, Add):   
            return left + right
        if isinstance(self, Sub):
            return left - right
        if isinstance(self, Mul):
            return left * right
        if isinstance(self, Div):
            if right != 0:
                return left / right
        if isinstance(self, Pow):
            return left ** right
    
""" 
All following classes define binary operations that can be performed in expressions (except for Num and Var).
These all call the parent class' definition for __str__ and __repr__ with a parameter corresponding to their
particular class for simplicity. 

Each of the following classes contains:
    * simplify method that returns a simplified version of their expression following 
    the rules for each operation.
    * eval method that, given a dictionary mapping variables to values, will evaluate the expression by
    replacing the variables with the values and performing the operations.

"""

class Add(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.order =  1
        
    def __str__(self):
        return super().__str__("+")
    
    def __repr__(self):
        return super().__repr__("Add")
    
    def simplify(self):
        return super().simplify("+")
        
    def eval(self, mapping):
        return super().eval(mapping)
    
class Sub(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.order =  1
        
    def __str__(self):
        return super().__str__("-")
    
    def __repr__(self):
        return super().__repr__("Sub")
    
    def simplify(self):
        return super().simplify("-")

    def eval(self, mapping):
        return super().eval(mapping)

class Mul(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.order =  2
    
    def __str__(self):
        return super().__str__("*")
    
    def __repr__(self):
        return super().__repr__("Mul")
    
    def simplify(self):
        return super().simplify("*")
    
    def eval(self, mapping):
        return super().eval(mapping)

class Div(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.order =  2
        
    def __str__(self):
        return super().__str__("/")
    
    def __repr__(self):
        return super().__repr__("Div")
    
    def simplify(self):
        return super().simplify("/")

    def eval(self, mapping):
        return super().eval(mapping)
    
class Pow(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.order =  3
        
    def __str__(self):
        return super().__str__("**")
    
    def __repr__(self):
        return super().__repr__("Pow")
    
    def simplify(self):
        return super().simplify("**")

    def eval(self, mapping):
        return super().eval(mapping)

class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n
        self.order = 99

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Var(" + repr(self.name) + ")"
    
    def simplify(self):
        return self
    
    def eval(self, mapping):
        if self.name in mapping.keys():
            return mapping[self.name]

class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n
        self.order = 99

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"
    
    def simplify(self):
        return self
    
    def eval(self, mapping):
        return self.n


if __name__ == "__main__":
    doctest.testmod()
    y = "(x + (y*(3+4)))"
    equation = sym(y)    
    print(repr(equation))
#!/usr/bin/env python3
"""6.009 Lab 6 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

# HELPER FUNCTIONS

def CNF_simplify(formula, assignment):
    """ 
    Given an assignment of a variable to a boolean (ex. 'a' = True), it returns a simplified CNF formula. In the 
    case of the following simplified formula evaluating to True or False, it will return either of those booleans.
    
    Parameters:
        formula (list): a list representation of a CNF formula.
        assignment (tuple): a tuple containing the variable and its assignment (ex. ('a', True)).
    """
    # Initializing new formula to be returned
    new_formula = []
    
    for clause in formula:
        new_clause = []
        # This flag is turned True when a variable assignment results in False
        false_flag = False
        # This flag is turned True when a variable assignment results in False, thus causing a True clause
        del_flag = False
        
        for literal in clause:
            # If the literal corresponds to the variable
            if literal[0] == assignment[0]:
                # If the assignment results in True, stops the loop through the clause
                if literal[1] == assignment[1]:
                    new_clause.append(literal)
                    del_flag = True
                    break
                # If the assignment results in False, continue with the next literal
                else:
                    false_flag = True
                    continue
            else:
                new_clause.append(literal)
                
        if not del_flag and len(new_clause) != 0:
            # Only adds clauses if these do not evaluate to True and have length greater than 0
            new_formula.append(new_clause)
            
        elif len(new_clause) == 0 and false_flag == True:
            # If the only literal in a clause is False due to an assignment, then the clause is False
            # and thus, the entire formula is False
            return False
    
    if len(new_formula) == 0:
        # If the length of the formula is 0, then all the clauses are True, and thus the formula is True
        return True
    return new_formula


def subsets(students, number):
    """ 
    Given a list of students and a number < len(students), it will return all the subsets of this list with
    size of subset equal to number.
    
    Parameters:
        students (list): list of student names
        number (int): number = room capacity + 1
    """
    # If the the size of the subsets is equal to 0, it returns only the empty set
    if number == 0:
        return [[]]
    
    result = []
    # For every student, it will add the subsets that involve the current student i and the rest of the students
    # such that it satisfies the size number
    for i in range(len(students)):
        student = students[i]
        rest = students[i + 1 : len(students)]
        
        # For every recursive call, the program creates a list of smaller subsets which progressively get
        # bigger until involving every subset of size number
        for stud in subsets(rest, number - 1):
            smaller_sub = [student] + stud
            result.append(smaller_sub)
    return result


############################################################################################################
# **********************************************************************************************************
############################################################################################################


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    # If the formula has no clauses, then return an empty dictionary
    if len(formula) == 0:
        return {}
    
    # Either the variable to check is the first one of the formula, or we arbitrarily choose a variable
    # from a clause with only one literal
    variable = formula[0][0][0]
    for clause in range(len(formula)):
        if len(formula[clause]) == 1:
            # If we find a clause with length 1, we take its literal as variable and stop the loop
            variable = formula[clause][0][0]
            break
    
    # We evaluate the two results from setting this variable to True and False, respectively
    F1_true = CNF_simplify(formula, (variable, True))
    F1_false = CNF_simplify(formula, (variable, False))
    
    formulas = [F1_true, F1_false]
    bools = [True, False]
    
    # BASE CASES: either a formula turns out to be True (and return the variable assignment), or we find out that 
    # both are False (in which case, we return None as there is no solution through this path)
    if F1_true == True:
        return {variable : True}
    elif F1_false == True:
        return {variable : False}
    elif F1_true == False and F1_false == False:
        return None
    
    for i in range(len(formulas)):
        # We check the True formula, if it's False, then we continue to test the False formula
        if formulas[i] == False:
            continue
        # Recursive call: either returns a dictionary of variable assignments, or None
        new_result = satisfying_assignment(formulas[i])
        # If the recursive call is not None, it adds the variable assignment to the result and returns it
        if new_result != None:
            result = {variable : bools[i]}
            result.update(new_result)
            return result
        # If the recursive call is None, continue to test the False formula (or end the loop)
        else:
            continue
    return None

def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    # We copy both a list with student names and a list with room names
    students = list(student_preferences.keys())
    rooms = list(room_capacities.keys())
    
    rule1 = []
    rule2 = []
    rule3 = []
    
    # RULE 1
    # For every student, at least one of their desired room must be assigned (aka. must be True)
    for student in students:
        clause = []
        for desired_room in student_preferences[student]:
            title = student + "_" + desired_room
            clause.append((title, True))
        rule1.append(clause)
    
    # RULE 2
    # For every student, no student can be in more than two rooms at the same time
    # In other words, for every pair of rooms, at least one the assignments must be False
    for student in students:
        checked_dict = {room:set() for room in room_capacities.keys()}
        for room1 in rooms:
            for room2 in rooms:
                if room2 not in checked_dict[room1] and room1 != room2:
                    checked_dict[room1].add(room2)
                    checked_dict[room2].add(room1)
                    title1 = student + "_" + room1
                    title2 = student + "_" + room2
                    rule2.append([(title1, False), (title2, False)])
    
    # RULE 3
    # For every room, no more students than their capacity can be assigned. In other words, for every subset
    # of room capacity + 1 students, at least one of the assignments must be False
    for room in rooms:
        if room_capacities[room] < len(students):
            student_subsets = subsets(students, room_capacities[room] + 1)
            for subset in student_subsets:
                clause = []
                for student in subset:
                    title = student + "_" + room
                    clause.append((title, False))
                rule3.append(clause)
    
    # The final formula will then be a combination of these three aforementioned rules
    final_formula = rule1 + rule2 + rule3
    return final_formula

if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)

# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 22:44:52 2021

@author: Louis Martinez
"""


form = [
    [('a', True), ('b', True), ('c', True)],
    [('a', False), ('f', True)],
    [('d', False), ('e', True), ('a', True), ('g', True)],
    [('h', False), ('c', True), ('a', False), ('f', True)],
]

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
        false_flag = False
        del_flag = False
        
        for literal in clause:
            if literal[0] == assignment[0]:
                if literal[1] == assignment[1]:
                    new_clause.append(literal)
                    del_flag = True
                    break
                else:
                    false_flag = True
                    continue
            else:
                new_clause.append(literal)
                
        if not del_flag and len(new_clause) != 0:
            new_formula.append(new_clause)
            
        elif len(new_clause) == 0 and false_flag == True:
            return False
    
    if len(new_formula) == 0:
        return True
    return new_formula

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
    print(formula)
    if len(formula) == 0:
        return {}
    
    variable = formula[0][0][0]
    F1_true = CNF_simplify(formula, (variable, True))
    F1_false = CNF_simplify(formula, (variable, False))
    
    formulas = [F1_true, F1_false]
    bools = [True, False]
    
    if F1_true == True:
        return {variable : True}
    elif F1_false == True:
        return {variable : True}
    elif F1_true == False and F1_false == False:
        return None
    
    for i in range(len(formulas)):
        if formulas[i] == False:
            continue
        new_result = satisfying_assignment(formulas[i])
        if new_result != None:
            result = {variable : bools[i]}
            result.update(new_result)
            return result
        else:
            continue
    return None

form = [
    [('a', True), ('b', True), ('c', True)],
    [('a', False), ('f', True)],
    [('d', False), ('e', True), ('a', True), ('g', True)],
    [('h', False), ('c', True), ('a', False), ('f', True)],
]

form2 = [[('a', True), ('a', False)], 
         [('b', True), ('a', True)], [('b', True)], 
         [('b', False), ('b', False), ('a', False)], [('c', True), ('d', True)], [('c', True), ('d', True)]]

#result = CNF_simplify(form, ('a', True))
result2 = CNF_simplify(form2, ('a', False))






def subsets(students, number):
    """ 
    """
    if number == 0:
        return [[]]
    result = []
    for i in range(len(students)):
        student = students[i]
        rest = students[i + 1 : len(students)]
        
        for stud in subsets(rest, number - 1):
            result.append([student] + stud)
    return result

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
    students = list(student_preferences.keys())
    rooms = list(room_capacities.keys())
    
    rule1 = []
    rule2 = []
    rule3 = []
    
    for student in students:
        clause = []
        for desired_room in student_preferences[student]:
            title = student + "_" + desired_room
            clause.append((title, True))
        rule1.append(clause)
    
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
                    
    for room in rooms:
        if room_capacities[room] < len(students):
            student_subsets = subsets(students, room_capacities[room] + 1)
            for subset in student_subsets:
                clause = []
                for student in subset:
                    title = student + "_" + room
                    clause.append((title, False))
                rule3.append(clause)
    
    final_formula = rule1 + rule2 + rule3
    return final_formula
    
result = boolify_scheduling_problem({'Alice': {'basement', 'penthouse'},
                            'Bob': {'kitchen'},
                            'Charles': {'basement', 'kitchen'},
                            'Dana': {'kitchen', 'penthouse', 'basement'}},
                           {'basement': 1,
                            'kitchen': 2,
                            'penthouse': 4})

print(result[0])
print()
print(result[1])
print()
print(result[2])
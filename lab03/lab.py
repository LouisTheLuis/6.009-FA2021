#!/usr/bin/env python3

import pickle
# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for this lab will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).  See the following page for more
# information: https://py.mit.edu/fall21/notes/style

######################################## HELPER FUNCTIONS ONLY ##################################################

def merge_sets(set_list):
    """
    Automatically merges a list of sets. Returns the merged set.
    """
    result = set()
    for set_0 in range(len(set_list)):
        result.update(set_list[set_0])
    return result

def find_names(set_list):
    """ 
    Given a set of actor's ID's, it returns a set with their names (in String type).
    """
    if type(set_list) == list:
        with open('resources/names.pickle', 'rb') as g:
            names = pickle.load(g)
            new_list = []
            for ID in set_list:
                key = ""
                for i in names.keys():
                    if names[i] == ID:
                        key = i
                new_list.append(key)
            return new_list
    with open('resources/names.pickle', 'rb') as g:
        names = pickle.load(g)
        new_set = set()
        for ID in set_list:
            key = ""
            for i in names.keys():
                if names[i] == ID:
                    key = i
            new_set.add(key)
        return new_set

def find_movies(set_list):
    """ 
    Given a set of movies' ID's, it returns a set with their names (in String type).
    """
    if type(set_list) == list:
        with open('resources/movies.pickle', 'rb') as g:
            names = pickle.load(g)
            new_list = []
            for ID in set_list:
                key = ""
                for i in names.keys():
                    if names[i] == ID:
                        key = i
                new_list.append(key)
            return new_list
    with open('resources/movies.pickle', 'rb') as g:
        names = pickle.load(g)
        new_set = set()
        for ID in set_list:
            key = ""
            for i in names.keys():
                if names[i] == ID:
                    key = i
            new_set.add(key)
        return new_set

#################################################################################################################

def transform_data(raw_data):
    """ 
    Given a database of the form of a list of tuples (actor 1, actor 2, movie), it will return a dictionary with
    the following information given in the keys as described below:
        
        int actor ID: it has a set of all the people that worked with the actor that has this ID.
        
        String actor ID: it contains a dictionary of the form {String actor* ID: movie}, where actor* is someone
        that worked with the actor of the key. This information is stored so that we can easily return the movie
        where two actors participated together.
        
        movies (dictionary):
            int movie ID: it contains a set of all the actors that worked in the movie with this ID.
    """
    data = {'movies': {}}
    for i in range(len(raw_data)):
        actor_1 = raw_data[i][0]
        actor_2 = raw_data[i][1]
        movie = raw_data[i][2]
        if actor_1 not in data.keys():
            data[actor_1] = {actor_2}
            data[str(actor_1)] = {}
            data[str(actor_1)][str(actor_2)] = movie
        else:
            data[actor_1].add(actor_2)
            if str(actor_1) in data.keys():
                data[str(actor_1)][str(actor_2)] = movie
            else:
                data[str(actor_1)] = {}
                data[str(actor_1)][str(actor_2)] = movie
            
        if actor_2 not in data.keys():
            data[actor_2] = {actor_1}
            data[str(actor_2)] = {}
            data[str(actor_2)][str(actor_1)] = movie
        else:
            data[actor_2].add(actor_1)
            if str(actor_2) in data.keys():
                data[str(actor_2)][str(actor_1)] = movie
            else:
                data[str(actor_2)] = {}
                data[str(actor_2)][str(actor_1)] = movie
              
        ################################## !!!!!!!!!!!!!!!!!!!!!!!! ####################################
        # THE DATABASE *WILL* CONFUSE MOVIE IDS WITH ACTOR IDS IF I KEEP THEM IN THE SAME DICTIONARY
        # I LITERALLY SPENT 6 HOURS STUCK IN THIS BS NEVER DOING IT *AGAIN*
        ################################## !!!!!!!!!!!!!!!!!!!!!!!! ####################################
        if movie not in data['movies'].keys():
            data['movies'][movie] = {actor_1, actor_2}
        else:
            data['movies'][movie].update({actor_1, actor_2})
    return data


def acted_together(transformed_data, actor_id_1, actor_id_2):
    """
    Given a dictionary of various lists (actor ID #1, actor ID #2, movie ID) and two actor ID's,
    it returns a boolean: True if the actors were together in a movie, False if not. 
    """
    # If both actors are the same, it returns True.
    if actor_id_1 == actor_id_2:
        return True
    # If actor 2 is in the list of people actor 1 worked with, it returns True.
    if actor_id_2 in transformed_data[actor_id_1]:
        return True
    return False

def actors_with_bacon_number(transformed_data, n, kevin_id = 4724):
    """
    Given a number n, it returns a set with all the actors that have a Bacon number n.
    """
    # The following list will append the sets of bacon numbers 0, 1, 2, 3, ..., n
    various_bacons = []
    i = 0
    while i <= n:
        if i == 0:
            # Adds only Kevin Bacon's ID for n = 0
            temp_set = {kevin_id}
            various_bacons.append(temp_set)
            i += 1
        elif i == 1:
            # Adds only the set of people who acted with Kevin Bacon's for n = 1
            temp_set = transformed_data[kevin_id]
            various_bacons.append(temp_set)
            i += 1
        else:
            # Creates a set for all the people with Bacon number less than i
            previous_bacons = merge_sets(various_bacons)
            # Creates a set with all the people who acted with people with Bacon number i - 1
            temp_set = set()
            for actor in (various_bacons[i - 1]):
                temp_set.update(transformed_data[actor])
            # Extracts people who already have Bacon number lower than i
            copy = temp_set.copy()
            for person in temp_set:
                if person in previous_bacons:
                    copy.remove(person)
            various_bacons.append(copy)
            # Prevents the program from running forever given a large Bacon number
            if len(temp_set) == 0:
                return set()
            i += 1
    bacon_n = various_bacons[n]
    return bacon_n


def bacon_path(transformed_data, actor_id_1, actor_id_2 = 4724):
    """ 
    Given an actor's ID, it returns a list with the least number of actors that connects the actor
    with Kevin Bacon.
    """
    # This prevents the program from running forever when given a non-existant ID.
    if actor_id_1 not in transformed_data.keys():
        return None
    
    # If the IDs of both the beginning and end actors are the same, it just returns a list with the actor in it.
    if actor_id_1 == actor_id_2:
        return [actor_id_1]  

    # Initializes a list of checked ID's and possible paths. Both are initialized with the starting ID on it.
    checked = {actor_id_2}
    paths = []
    paths.append([actor_id_2])
    i = 0
    # The program will stop when there are no more paths to check; that is, when the index i is greater than the
    # length of the list of paths.
    while i < len(paths):
        # Retrieves the last ID ("current actor") from the path we're checking.
        path = paths[i]
        current_actor = path[-1]
        # Finds the ID's of the actors that worked with the current actor ("friends" of the current actor).
        friends_of_actor = transformed_data[current_actor]
        # Now that we have all the info we need, we add the current actor to the list of checked ID's.
        checked.add(current_actor)
        for friend in friends_of_actor:
            # For every "friend" of the current actor, it creates a new path that adds the "friend" to the end. 
            # This new path is appended to the list of paths to check later.
            # The friends are also checked.
            if friend not in checked:
                checked.add(friend)
                new_path = list(path)
                new_path.append(friend)
                paths.append(new_path)
            # If one of these friends turn out to be the final actor we are looking for, we know that is
            # the final path, so we return it.
            if friend == actor_id_1:
                return new_path
        i += 1
    # Returns None if no path was found.
    return None
    

def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """ 
    Given the IDs of two actors, it returns a list with the least number of actors that connects
    actor 1 with actor 2.
    It uses the structure of bacon_path, replacing the default value (Kevin's ID) for the 1st actor's ID.
    """
    return bacon_path(transformed_data, actor_id_2, actor_id_1)  


def movie_connect(transformed_data, actor_id_1, actor_id_2):
    """ 
    Given two actors that were on the same movie, it returns the ID of the movie where they both acted.
    """
    with open('resources/movies.pickle', 'rb') as g:
        movies = pickle.load(g)
        key = ""
        # Searches for the movie ID where both actor 1 and actor 2 acted.
        movie_ID = transformed_data[str(actor_id_1)][str(actor_id_2)]
        for i in movies.keys():
            if movies[i] == movie_ID:
                key = i
        return key
    
def movie_path(transformed_data, actor_id_1, actor_id_2):
    """
    Given a path of actors between two actors 1 and 2, it returns a list with the path of movies that
    connect both actors.
    """
    # Creates an actor path between actor 1 and actor 2.
    actor_path = actor_to_actor_path(transformed_data, actor_id_1, actor_id_2)
    # Initializes a movie path.
    movie_path = []
    # Finds the movie that connects every two actors in the actor path and then adds it to the movie path.
    for actor in range(1, len(actor_path), 1):
        movie_connection = movie_connect(transformed_data, actor_path[actor - 1], actor_path[actor])
        movie_path.append(movie_connection)
    return movie_path


def actor_path(transformed_data, actor_id, goal_test_function):
    """ 
    Given a starting actor ID and a goal test function (a final condition), 
    the program will construct an actor path that will end
    with the actor that satisfies (aka. returns True to the goal test function) the final condition.
    """
    # This prevents the program from running forever when given a non-existant ID.
    if actor_id not in transformed_data.keys():
        return None
    
    # If the first actor already satisfies the final condition, it returns a list with only that actor.
    if goal_test_function(actor_id):
        return [actor_id]  

    checked = {actor_id}
    paths = []
    paths.append([actor_id])
    i = 0
    while i < len(paths):
        path = paths[i]
        actor = path[-1]
        friends_of_actor = transformed_data[actor]
        checked.add(actor)
        for friend in friends_of_actor:
            if friend not in checked:
                checked.add(friend)
                new_path = list(path)
                new_path.append(friend)
                paths.append(new_path)
            # The structure of the program is similar to bacon_path, but the satisfying condition is given
            # by the goal test function.
            if goal_test_function(friend):
                return new_path
        i += 1
    # Returns None if no path was found.
    return None

def actors_connecting_films(transformed_data, film1, film2):
    """ 
    Given two films Film 1 and Film 2, it returns the shortest path of actors between those two films.
    """
    # Creates a helper function that takes the set of actors that worked on Film 2.
    # The function, given an actor, checks whether the actor worked on Film 2 or not (returning a boolean).
    actors = transformed_data['movies'][film2]
    def from_second_film(actor, actors_second = actors):
        if actor in actors_second:
            return True
        return False
    
    # Iterates through the actors that worked in Film 1. For each one, it creates a possible path using
    # the condition given by the previous helper function. 
    # If the length of the path is not 'None' and the shorter than "shortest", it will replace "shortest" (this
    # is to record the shortest path as we iterate).
    shortest = None
    for actor_1 in transformed_data['movies'][film1]:
        possible_path = actor_path(transformed_data, actor_1, from_second_film)
        if possible_path != None:
            if shortest != None:
                if len(possible_path) < len(shortest):
                    shortest = possible_path
            else:
                shortest = possible_path
    
    # If there is a valid shortest path, it is returned.
    if shortest != None:
        return shortest
    # Else, it returns None.
    return None


if __name__ == '__main__':
    with open('resources/small.pickle', 'rb') as f:
        with open('resources/names.pickle', 'rb') as g:
            smalldb = pickle.load(f)
            names = pickle.load(g)
            key = ""
            for i in names.keys():
                if names[i] == 27390:
                    key = i
                    break
        # HOW TO GET THE NAME OF AN ACTOR
    with open('resources/tiny.pickle', 'rb') as d:
        tiny = pickle.load(d)
        tiny2 = transform_data(tiny)
        print(bacon_path(tiny2, 1640))
    with open('resources/large.pickle', 'rb') as f:
        large = pickle.load(f)
        large_real = transform_data(large)
        tuples = []
        for i in range(700):
            value = (i, i+1, 0)
            tuples.append(value)
        #print(tuples)
        tuples_t = transform_data(tuples)
        path = actor_to_actor_path(tuples_t, 0, 699)
        #movie_path = movie_path(large_real, 58567, 1338716)
        #print(movie_path(large_real, 58567, 1338716))
        #path = actor_to_actor_path(large_real, 1199143, 56614)
        #print(path)
        #print(find_names(path))
        #path = actor_to_actor_path(large_real, , )
    with open('resources/large.pickle', 'rb') as f:
        with open('resources/names.pickle', 'rb') as g:
            largedb = pickle.load(f)
            names = pickle.load(g)
            key = ""
            for i in names.keys():
                if names[i] == 27390:
                    key = i
                    break        
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    pass

"""key = ""
for i in smalldb.keys():
   if smalldb[i] == 104573:
       key = i"""

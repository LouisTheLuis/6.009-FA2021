# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self, keytype):
        self.value = None
        self.key_type = keytype
        self.children = {}
    
    def _get_node(self, key):
        """ 
        Helper function that looks for a certain node in the trie and returns it.
        """
        # If the type of the key does not match the type of the Trie, it raises TypeError
        if type(key) is not self.key_type:
            raise TypeError
        
        # BASE CASE
        # If the key is of length 0, that is, it's a string "" or a tuple (), then it returns the node
        if len(key) == 0:
            return self
        
        # Takes the first element of the key; if there isn't a node with that element in the children
        # then it raises a KeyError
        element = key[0:1]
        if element not in self.children.keys():
            raise KeyError
            
        # RECURSIVE CALL
        # Looks for a node for the rest of the elements of the key
        return self.children[element]._get_node(key[1:])

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        # If the type of the key does not match the type of the trie, it raises TypeError
        if type(key) is not self.key_type:
            raise TypeError
        
        # For every index, we take the last (len(key) - index) elements as a 'prefix'
        for i in range(len(key)):
            prefix = key[i : i + 1]
            # If the prefix is not in the children of the current key, then we create a Trie for that prefix
            # Then WE CHANGE THE POINTER OF SELF TO THE CHILDREN TRIE WITH THE PREFIX
            # If it is the last element of the key, we set the value of the last Trie to the desired value
            if prefix not in self.children.keys():
                self.children[prefix] = Trie(self.key_type)
                self = self.children[prefix]
                if i == len(key) - 1:
                    self.value = value
                    
            # If the prefix is in the children of the current key, then we just CHANGE THE POINTER OF SELF
            # TO THE CHILDREN TRIE WITH THE PREFIX
            # If it is the last element of the key, we set the value of the last Trie to the desired value
            else:
                if i == len(key) - 1:
                    self = self.children[prefix]
                    self.value = value
                else:
                    self = self.children[prefix]

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        >>> t = Trie(str)
        >>> t['bass'] = 1600
        >>> print(t['bass'])
        1600
        >>> t['bass'] = 1700
        >>> print(t['bass'])
        1700
        >>> print(t['b'])
        None
        """
        # We use the get node helper function to get the node of a certain key. Then, we return its value
        return self._get_node(key).value

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        >>> t = Trie(str)
        >>> t['bass'] = 1600
        >>> del t['bass']
        """
        # Specific case: if the key is an empty tuple, then it returns KeyError (no children will ever be
        # empty tuples)
        if key == ():
            raise KeyError
            
        # If the node at key has children, then we set its value to None
        if self._get_node(key).children:
            self._get_node(key).value = None
            
        # Else, we eliminate the node with key corresponding to the last element of the key
        else:
            self._get_node(key[:-1]).children.pop(key[len(key) - 1 : len(key)])

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.  If the given key is of
        the wrong type, raise a TypeError.
        """
        # If the node at the key exists, then it checks if it has a value. If it has, it returns True; if not
        # it returns False
        try:
            current = self._get_node(key)
            if current.value == None:
                return False
            else:
                return True
        
        # If the node at the key doesn't exist (the helper function would raise a KeyError then) it will
        # return False
        except KeyError:
            return False
            
    def __iter__(self, orig = ''):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """
        # Specific case: if the Trie type is a tuple, then we set the original iterator to be of type tuple
        if self.key_type is tuple and len(orig) == 0:
            orig = ()
        
        # MIDDLE CASE
        # For every key in the children, append the original iterator with the key and, if the key has 
        # a value, yield a tuple of the appended key and the value
        for key in self.children.keys():
            val = orig + key
            if self.children[key].value != None:
                yield (val, self.children[key].value)
        
        # RECURSIVE CASE
        # If the node has children, for every key in it we yield from its children
        if self.children:
            for key in self.children.keys():
                yield from self.children[key].__iter__(orig + key)
        
        # BASE CASE
        # If the node has no children, return
        else:
            return

def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    # We get a list of sentences
    sentences = tokenize_sentences(text)
    
    # Initialize a dictionary of word frequencies, of the form  word : frequency
    words_frequencies = {}
    
    # For every word in every sentence, we check if the word is in the dictionary. If it is not, we
    # add it with initial frequency 1. If it is, we add 1 to its frequency value
    for sentence in sentences:
        for word in sentence.split():
            if word not in words_frequencies.keys():
                words_frequencies[word] = 1
            else:
                words_frequencies[word] += 1
    
    # We initialize a String Trie
    # For every word in the dictionary, we set a key equal to its frequency value in the word Trie
    word_trie = Trie(str)
    for word in words_frequencies.keys():
        word_trie[word] = words_frequencies[word]
        
    return word_trie


def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    # We get a list of sentences
    sentences = tokenize_sentences(text)
    # We create a tuple of sentences, where every sentence is a tuple of words
    phrases = (tuple(sentence.split()) for sentence in sentences)
    
    # Initialize a dictionary of phrase frequencies
    phrase_frequencies = {}
    
    # For every phrase in the tuple of sentences, we check if the phrase is in the dictionary. If it is not,
    # we add it with initial frequency 1. If it is, we add 1 to its frequency value
    for phrase in phrases:
        if phrase not in phrase_frequencies.keys():
            phrase_frequencies[phrase] = 1
        else:
            phrase_frequencies[phrase] += 1
    
    # We initialize a tuple Trie
    # For every phrase in the dictionary, we set a key equal to its frequency value in the phrase Trie
    phrase_trie = Trie(tuple)
    for phrase in phrase_frequencies.keys():
        phrase_trie[phrase] = phrase_frequencies[phrase]
        
    return phrase_trie


def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    """
    # If the type of the prefix does not match the type of the Trie, it raises a TypeError
    if type(prefix) is not trie.key_type:
        raise TypeError
    
    # Initialize a dictionary and an answer list to return
    results = {}
    answer = []
    
    # If the prefix is in the Trie, set the Trie node equal to a variable. 
    # If it doesn't, then returns an empty list
    try: 
        new_node = trie._get_node(prefix)
    except KeyError:
        return []
    
    # If the Trie node of the prefix has a value, then set the prefix in the dictionary equal to
    # that same value
    if new_node.value != None:
        results[prefix] = new_node.value
    
    # For every key, value pair connected to the node of the prefix: if the key has a proper value, then it
    # sets a prefix + key combination equal to the frequency value at that combination
    for key, value in trie._get_node(prefix):
        if value != None:
            results[prefix + key] = value
    
    # If there are no elements with the prefix, return the empty initialized list
    if not results:
        return answer
    
    # If there is no max count, then just set it to be the number of elements in the dictionary
    if max_count == None:
        max_count = len(results.keys())
    
    # We check the word with maximum frequency max count times and that word to the answer list in 
    # every iteration. If we run out of words in the process, then return the answer list directly
    while max_count > 0:
        if not results:
            return answer
        else:
            max_word = max(results, key = results.get)
            answer.append(max_word)
            results.pop(max_word)
            max_count -= 1
    
    return answer


def autocorrect(trie, prefix, max_count = None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 
                'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
    # Initialize a dictionary of suggestions
    suggestions = {}
    # Get a list of the max_count most frequent words with a certain prefix
    results = autocomplete(trie, prefix, max_count)
    
    # Insertion
    # For every letter in the alphabet, insert that letter in an index of the prefix 
    # If the new word is in the Trie, set that new word equal to its Trie frequency value in the dictionary
    for i in range(len(prefix)):
        for letter in alphabet:
            new_word = prefix[:i] + letter + prefix[i:]
            if new_word in trie:
                suggestions[new_word] = trie[new_word]
                    
    # Deletion
    # For evert index of the prefix, we eliminate a letter at that same index
    # If the new word is in the Trie, set that new word equal to its Trie frequency value in the dictionary
    for i in range(len(prefix)):
        new_word = prefix[:i] + prefix[i + 1:]
        if new_word in trie:
            suggestions[new_word] = trie[new_word]
        
    # Replacement
    # For every index in the prefix, we replace the letter at that index with a letter of the alphabet
    # If the new word is in the Trie, set that new word equal to its Trie frequency value in the dictionary
    for i in range(len(prefix)):
        for letter2 in alphabet:
            new_word = prefix[:i] + letter2 + prefix[i + 1:]
            if new_word in trie:
                suggestions[new_word] = trie[new_word]
        
    # Transpose
    # For every index in the prefix, we switch the letter at the index with the next letter
    # If the new word is in the Trie, set that new word equal to its Trie frequency value in the dictionary
    for i in range(len(prefix) - 1):
        pref = list(prefix)
        pref[i], pref[i + 1] = pref[i + 1], pref[i]
        new_word = "".join(pref)
        if new_word in trie:
            suggestions[new_word] = trie[new_word]
    
    # If the max count is a proper number, then for every remaining word not obtained from the autocomplete
    # we get the word from the suggestions dictionary with highest value frequency and add it to the result
    # list
    if max_count != None:
        counter = max_count - len(results)
        while counter > 0:
            if not suggestions:
                return results
            else:
                max_word = max(suggestions, key = suggestions.get)
                results.append(max_word)
                suggestions.pop(max_word)
                counter -= 1
        return results
    
    # If the max count is None, then we append all suggestions to the result list
    else:
        for key in suggestions.keys():
            if key not in results:
                results.append(key)
                
        return results

def filter_helper(trie, pattern):
    """ 
    Returns list of only words in the trie that match the pattern searched.
    This helper function is used by the word filter function in order
    to get the words, which then will be assigned in tuples (word, frequency).
    """
    # Initialize a list of answer words
    real_answer = []
    
    # BASE CASE
    # If the length of the pattern prefix is 0, return an empty string
    if len(pattern) == 0:
        return ""
    
    else:
        # Obtain the first element of the pattern
        letter = pattern[0]
        # Initialize a temporary answer list
        temp_answer = []
        
        # If the letter is an *, then we check the following:
            # If the pattern only has the asterisk, then it appends all keys in the Trie to the temp list
            # If the pattern has more letters, we check its next value. If the next value is a normal alphabet
            # letter, then it returns all keys
        if letter == "*":
            if len(pattern) == 1:
                for key in autocomplete(trie, ""):
                    temp_answer.append(key)
            else:
                letter2 = pattern[1]
                #if letter2 != "*":
                  #  for key, value in trie:
                   #     if value != None:
                    #        temp_answer.append(key)
                if letter2 != "?" and letter2 != "*":
                    for key, value in trie:
                        if key[-1] == letter2:
                            temp_answer.append(key[:-1])
                elif letter2 == "?":
                    for key, value in trie:
                        if value != None:
                            temp_answer.append(key)
                else:
                    temp_answer.append("")
        
        # If the letter is a ?, we append all keys in the children of the current node to the temp list
        elif letter == "?":
            for key in trie.children.keys():
                temp_answer.append(key)
        
        # If the letter is an alphabet letter, we check if it is in the children of the current node. If it 
        # is, then we append it to the temp list
        else:
            if letter in trie.children.keys():
                temp_answer.append(letter)
        
        # For every key in the temp answer list, we check RECURSIVELY the filtered words from the node
        # at the key with the pattern omitting its first letter
        # If there are filtered words from the recursion, we append a combination of the key from the current
        # call with every key from the recursive call to the real answer list
        for word1 in temp_answer:
            alt = filter_helper(trie._get_node(word1), pattern[1:])
            if alt:
                for word2 in alt:
                    real_answer.append(word1 + word2)
                    
            # If there are no filtered words from the recursion, we check if the key is longer or equal
            # to the current pattern without *. If it is, we append it to the real answer list
            else:
                if len(word1) >= len(pattern.replace("*", "")):
                    real_answer.append(word1)
            
    return real_answer

def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    # We obtain a list of words matching the pattern from the helper function and initialize a list of
    # answers
    result = filter_helper(trie, pattern)
    answer = []
    
    # For every key in the list of words, if the key has a value, then we append a tuple (key, value)
    # to the answer list
    for key in result:
        if trie[key] != None:
            answer.append((key, trie[key]))
    return answer
    
# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
    with open("tale_of_two.txt", encoding="utf-8") as f:
        text = f.read()
        tro = make_word_trie(text)
        print(word_filter(tro, "r?c*t"))
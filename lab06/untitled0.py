# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 20:20:23 2021

@author: Louis Martinez
"""
from text_tokenize import tokenize_sentences

class Trie:
    def __init__(self, keytype):
        self.value = None
        self.key_type = keytype
        self.children = {}
    
    def _get_node(self, key):
        """ 
        Helper function that looks for a certain node in the trie.
        """
        if type(key) is not self.key_type:
            raise TypeError
        
        if len(key) == 0:
            return self
        
        letter = key[0:1]
        if letter not in self.children.keys():
            raise KeyError

        return self.children[letter]._get_node(key[1:])

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        if type(key) is not self.key_type:
            raise TypeError
        
        for i in range(len(key)):
            prefix = key[i : i + 1]
            if prefix not in self.children.keys():
                self.children[prefix] = Trie(self.key_type)
                self = self.children[prefix]
                if i == len(key) - 1:
                    self.value = value
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
        if key == ():
            raise KeyError
        if self._get_node(key).children:
            self._get_node(key).value = None
        else:
            self._get_node(key[:-1]).children.pop(key[len(key) - 1 : len(key)])

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.  If the given key is of
        the wrong type, raise a TypeError.
        """
        try:
            current = self._get_node(key)
            if current.value == None:
                return False
            else:
                return True
        except KeyError:
            return False
            
    def __iter__(self, orig = ''):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """
        if self.key_type is tuple and len(orig) == 0:
            orig = ()
            
        for key in self.children.keys():
            val = orig + key
            if self.children[key].value != None:
                yield (val, self.children[key].value)
    
        if self.children:
            for key in self.children.keys():
                yield from self.children[key].__iter__(orig + key)
        else:
            return
                
def dictify(t):
    assert set(t.__dict__) == {'value', 'key_type', 'children'}, "Trie instances should only contain the three instance attributes mentioned in the lab writeup."
    out = {'value': t.value, 'children': {}}
    for ch, child in t.children.items():
        out['children'][ch] = dictify(child)
    return out

def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    sentences = tokenize_sentences(text)
    words_frequencies = {}
    for sentence in sentences:
        for word in sentence.split():
            if word not in words_frequencies.keys():
                words_frequencies[word] = 1
            else:
                words_frequencies[word] += 1
    
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
    sentences = tokenize_sentences(text)
    phrases = (tuple(sentence.split()) for sentence in sentences)
    phrase_frequencies = {}
    
    for phrase in phrases:
        if phrase not in phrase_frequencies.keys():
            phrase_frequencies[phrase] = 1
        else:
            phrase_frequencies[phrase] += 1
    
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
    if type(prefix) is not trie.key_type:
        raise TypeError
        
    results = {}
    answer = []
    try: 
        new_node = trie._get_node(prefix)
    except KeyError:
        return []
    
    if new_node.value != None:
        results[prefix] = new_node.value
        
    for key, value in trie._get_node(prefix):
        if value != None:
            results[prefix + key] = value
    
    if not results:
        return answer
    
    if max_count == None:
        max_count = len(results.keys())
        
    while max_count > 0:
        if not results:
            return answer
        else:
            max_word = max(results, key = results.get)
            answer.append(max_word)
            results.pop(max_word)
            max_count -= 1
    
    return answer

def filter_helper(trie, pattern):
    real_answer = []
    if len(pattern) == 0:
        return ""
    
    else:
        letter = pattern[0]
        answer = []
        if letter == "*":
            if len(pattern) == 1:
                for val in autocomplete(trie, ""):
                    answer.append(val)
            else:
                letter2 = pattern[1]
                if letter2 != "?" and letter2 != "*":
                    for key, value in trie:
                        if key[-1] == letter2:
                            answer.append(key[:-1])
                elif letter2 == "?":
                    for key, value in trie:
                        if value != None:
                            answer.append(key)
                else:
                    answer.append("")
                            
        elif letter == "?":
            for key in trie.children.keys():
                answer.append(key)
                
        else:
            if letter in trie.children.keys():
                answer.append(letter)
        
        for word1 in answer:
            alt = filter_helper(trie._get_node(word1), pattern[1:])
            if alt:
                for word2 in alt:
                    real_answer.append(word1 + word2)
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
    result = filter_helper(trie, pattern)
    answer = []
    for key in result:
        if trie[key] != None:
            answer.append((key, trie[key]))
    return answer


trie = make_word_trie("man mat mattress map me met a man a a a map man met")
result = word_filter(trie, '**')
print(result)
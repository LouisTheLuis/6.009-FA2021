#!/usr/bin/env python3
import os.path
import lab
import json
import types
import pickle

import sys
sys.setrecursionlimit(10000)

import pytest

TEST_DIRECTORY = os.path.dirname(__file__)


# convert trie into a dictionary...
def dictify(t):
    assert set(t.__dict__) == {'value', 'key_type', 'children'}, "Trie instances should only contain the three instance attributes mentioned in the lab writeup."
    out = {'value': t.value, 'children': {}}
    for ch, child in t.children.items():
        out['children'][ch] = dictify(child)
    return out

# ...and back
def from_dict(d):
    type_ = str
    for k,v in d.items():
        type_ = type(k)
        break
    t = lab.Trie(type_)
    for k, v in d.items():
        t[k] = v
    return t

# make sure the keys are not explicitly stored in any node
def any_key_stored(trie, keys):
    keys = [tuple(k) for k in keys]
    for i in dir(trie):
        try:
            val = tuple(getattr(trie, i))
        except:
            continue
        for j in keys:
            if j == val:
                return repr(i), repr(j)
    for child in trie.children.values():
        key_stored = any_key_stored(child, keys)
        if key_stored:
            return key_stored
    return None

# read in expected result
def read_expected(fname):
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', fname), 'rb') as f:
        return pickle.load(f)

def test_trie_set():
    trie = lab.Trie(str)
    trie['cat'] = 'kitten'
    trie['car'] = 'tricycle'
    trie['carpet'] = 'rug'
    expect = read_expected('1.pickle')
    #print(expect)
    assert dictify(trie) == expect, "Your trie is incorrect."
    assert any_key_stored(trie, ('cat', 'car', 'carpet')) is None

    t = lab.Trie(str)
    t['a'] = 1
    t['an'] = 1
    t['ant'] = 0
    t['anteater'] = 1
    t['ants'] = 1
    t['a'] = 2
    t['an'] = 2
    t['a'] = 3
    expect = read_expected('2.pickle')
    assert dictify(t) == expect, "Your trie is incorrect."
    assert any_key_stored(t, ('an', 'ant', 'anteater', 'ants')) is None
    with pytest.raises(TypeError):
        t[(1, 2, 3)] = 20

    t = lab.Trie(str)
    t['man'] = ''
    t['mat'] = 'object'
    t['mattress'] = ()
    t['map'] = 'pam'
    t['me'] = 'you'
    t['met'] = 'tem'
    t['a'] = '?'
    t['map'] = -1000
    expect = read_expected('3.pickle')
    assert dictify(t) == expect, "Your trie is incorrect."
    assert any_key_stored(t, ('man', 'mat', 'mattress', 'map', 'me', 'met', 'map')) is None
    with pytest.raises(TypeError):
        t['something',] = 'pam'


def test_trie_get():
    d = {'name': 'John', 'favorite_numbers': [2, 4, 3], 'age': 39, 'children': 0}
    t = from_dict(d)
    assert dictify(t) == read_expected('person.pickle')
    assert all(t[k] == d[k] for k in d)
    assert any_key_stored(t, tuple(d)) is None

    c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige', 'storage space': ''}
    t = from_dict(c)
    assert dictify(t) == read_expected('car.pickle')
    assert all(t[k] == c[k] for k in c)
    assert any_key_stored(t, tuple(c)) is None
    for i in ('these', 'keys', 'dont', 'exist'):
        with pytest.raises(KeyError):
            x = t[i]
    with pytest.raises(TypeError):
        x = t[(1, 2, 3)]


def test_trie_contains():
    d = {'name': 'John', 'favorite_numbers': [2, 4, 3], 'age': 39, 'children': 0}
    t = from_dict(d)
    assert dictify(t) == read_expected('person.pickle')
    assert all(i in t for i in d)
    with pytest.raises(TypeError):
        (1, 2, 3) in t

    c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige', 'storage space': ''}
    t = from_dict(c)
    assert dictify(t) == read_expected('car.pickle')
    assert all(i in t for i in c)
    badkeys = ('these', 'keys', 'dont', 'exist', 'm', 'ma', 'mak', 'mo',
               'mod', 'mode', 'ye', 'yea', 'y', '', 'car.pickle')
    assert all(i not in t for i in badkeys)


def test_trie_iter():
    t = lab.Trie(str)
    t['man'] = ''
    t['mat'] = 'object'
    t['mattress'] = ()
    t['map'] = 'pam'
    t['me'] = 'you'
    t['met'] = 'tem'
    t['a'] = '?'
    t['map'] = -1000
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    expected = [('a', '?'), ('man', ''), ('map', -1000), ('mat', 'object'),
                ('mattress', ()), ('me', 'you'), ('met', 'tem')]
    assert sorted(list(t)) == expected


def test_trie_delete():
    c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige', 'storage space': ''}
    t = from_dict(c)
    assert dictify(t) == read_expected('car.pickle')
    del t['color']
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    with pytest.raises(KeyError):
        del t['color'] # can't delete again
    assert set(t) == set(c.items()) - {('color', 'beige')}
    t['color'] = 'silver'  # new paint job
    for i in t:
        if i[0] != 'color':
            assert i in c.items()
        else:
            assert i[1] == 'silver'

    for i in ('cat', 'dog', 'ferret', 'tomato'):
        with pytest.raises(KeyError):
            del t[i]

    with pytest.raises(TypeError):
        del t[1,2,3]

    t = lab.Trie(str)
    t['man'] = ''
    t['mat'] = 'object'
    t['mattress'] = ()
    t['map'] = 'pam'
    t['me'] = 'you'
    t['met'] = 'tem'
    t['a'] = '?'
    t['map'] = -1000
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    expected = [('a', '?'), ('man', ''), ('map', -1000), ('mat', 'object'),
                ('mattress', ()), ('me', 'you'), ('met', 'tem')]
    assert sorted(list(t)) == expected
    del t['mat']
    expected = [('a', '?'), ('man', ''), ('map', -1000),
                ('mattress', ()), ('me', 'you'), ('met', 'tem')]
    assert sorted(list(t)) == expected


def test_tuple_set():
    trie = lab.Trie(tuple)
    trie[(1, 2, 3)] = 'kitten'
    trie[(1, 2, 0)] = 'tricycle'
    trie[(1, 2, 0, 1)] = 'rug'
    expect = read_expected('4.pickle')
    assert dictify(trie) == expect, "Your trie is incorrect."
    assert any_key_stored(trie, ((1, 2, 3), (1, 2, 0), (1, 2, 0, 1))) is None

    t = lab.Trie(tuple)
    t[(7, 8, 9)] = 1
    t[(7, 8, 9, 'hello')] = 1
    t[(7, 8, 9, 'hello', (1, 2))] = 1
    t[(1, )] = 0
    t[(7, )] = 1
    t[(7, 8, 9)] = 2
    t[(-1, -2, -3)] = 2
    t[('a', )] = 3
    expect = read_expected('5.pickle')
    assert dictify(t) == expect, "Your trie is incorrect."
    res = any_key_stored(t, ((7, 8, 9), (7, 8, 9, 'hello'),
                             (7, 8, 9, 'hello', (1, 2)), (1, ),
                             (7, ), (-1, -2, -3), ('a', )))
    assert res is None


def test_tuple_get():
    d = {'name': 'John', 'favorite_numbers': [2, 4, 3], 'age': 39, 'children': 0}
    d = {tuple(k): v for k,v in d.items()}
    t = from_dict(d)
    assert dictify(t) == read_expected('tuple_person.pickle')
    assert all(t[k] == d[k] for k in d)
    assert any_key_stored(t, tuple(d)) is None
    with pytest.raises(TypeError):
        t['string'] = 20

    c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige', 'storage space': ''}
    c = {tuple(k): v for k,v in c.items()}
    t = from_dict(c)
    assert dictify(t) == read_expected('tuple_car.pickle')
    assert all(t[k] == c[k] for k in c)
    assert any_key_stored(t, tuple(c)) is None
    for i in ('these', 'keys', 'dont', 'exist'):
        with pytest.raises(KeyError):
            x = t[tuple(i)]
    with pytest.raises(TypeError):
        t[('yarn', 'twine', 'thread')[0]] = 20


def test_tuple_contains():
    d = {'name': 'John', 'favorite_numbers': [2, 4, 3], 'age': 39, 'children': 0}
    d = {tuple(k): v for k,v in d.items()}
    t = from_dict(d)
    assert dictify(t) == read_expected('tuple_person.pickle')
    assert all(i in t for i in d)
    with pytest.raises(TypeError):
        x = t['string']
    with pytest.raises(TypeError):
        'name' in t

    c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige', 'storage space': ''}
    c = {tuple(k): v for k,v in c.items()}
    t = from_dict(c)
    assert dictify(t) == read_expected('tuple_car.pickle')
    assert all(i in t for i in c)
    badkeys = ('these', 'keys', 'dont', 'exist', 'm', 'ma', 'mak', 'mo',
               'mod', 'mode', 'ye', 'yea', 'y', '', 'car.pickle')
    assert all(tuple(i) not in t for i in badkeys)
    with pytest.raises(TypeError):
        x = t[('yarn', 'twine', 'thread')[0]]


def test_tuple_iter():
    t = lab.Trie(tuple)
    t[(7, 8, 9)] = 1
    t[(7, 8, 9, 'hello')] = 1
    t[(7, 8, 9, 'hello', (1, 2))] = 1
    t[(1, )] = 0
    t[(7, )] = 1
    t[(7, 8, 9)] = 2
    t[(-1, -2, -3)] = 2
    t[(2, )] = 3
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    expected = [((-1, -2, -3), 2), ((1,), 0), ((2,), 3), ((7,), 1),
                ((7, 8, 9), 2), ((7, 8, 9, 'hello'), 1), ((7, 8, 9, 'hello', (1, 2)), 1)]
    assert sorted(list(t)) == expected


def test_tuple_delete():
    c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige', 'storage space': ''}
    c = {tuple(k): v for k,v in c.items()}
    t = from_dict(c)
    assert  dictify(t) == read_expected('tuple_car.pickle')
    del t[tuple('color')]
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    assert set(t) == set(c.items()) - {(tuple('color'), 'beige')}
    t[tuple('color')] = 'silver'  # new paint job
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    for i in t:
        if i[0] != tuple('color'):
            assert i in c.items()
        else:
            assert i[1] == 'silver'

    for i in (('cat', 'dog'), (), ('ferret',), tuple('tomato')):
        with pytest.raises(KeyError):
            del t[i]

    with pytest.raises(TypeError):
        del t["foo"]

    t = lab.Trie(tuple)
    t[(7, 8, 9)] = 1
    t[(7, 8, 9, 'hello')] = 1
    t[(7, 8, 9, 'hello', (1, 2))] = 1
    t[(1, )] = 1
    t[(7, )] = 1
    t[(7, 8, 9)] = 2
    t[(-1, -2, -3)] = 2
    t[(2, )] = 3
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    expected = [((-1, -2, -3), 2), ((1,), 1), ((2,), 3), ((7,), 1),
                ((7, 8, 9), 2), ((7, 8, 9, 'hello'), 1), ((7, 8, 9, 'hello', (1, 2)), 1)]
    assert sorted(list(t)) == expected
    del t[(7, 8, 9)]
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    expected = [((-1, -2, -3), 2), ((1,), 1), ((2,), 3), ((7,), 1),
                ((7, 8, 9, 'hello'), 1), ((7, 8, 9, 'hello', (1, 2)), 1)]
    assert sorted(list(t)) == expected


def test_word_trie():
    # small test
    l = lab.make_word_trie('toonces was a cat who could drive a car very fast until he crashed.')
    assert dictify(l) == read_expected('6.pickle')

    l = lab.make_word_trie('a man at the market murmered that he had met a mermaid. '
                           'mark didnt believe the man had met a mermaid.')
    assert dictify(l) == read_expected('7.pickle')

    l = lab.make_word_trie('what happened to the cat who had eaten the ball of yarn?  she had mittens!')
    assert dictify(l) == read_expected('8.pickle')


def test_phrase_trie():
    # small test
    l = lab.make_phrase_trie('toonces was a cat who could drive a car very fast until he crashed.')
    assert dictify(l) == read_expected('9.pickle')

    l = lab.make_phrase_trie('a man at the market murmered that he had met a mermaid. '
                             'i dont believe that he had met a mermaid.')
    assert dictify(l) == read_expected('10.pickle')

    l = lab.make_phrase_trie(('What happened to the cat who ate the ball of yarn?  She had mittens!  '
                               'What happened to the frog who was double parked?  He got toad!  '
                               'What happened yesterday?  I dont remember.'))
    assert dictify(l) == read_expected('11.pickle')


@pytest.mark.parametrize('bigtext', ['holmes', 'earnest', 'frankenstein'])
def test_big_corpora(bigtext):
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', '%s.txt' % bigtext), encoding='utf-8') as f:
        text = f.read()
        w = lab.make_word_trie(text)
        p = lab.make_phrase_trie(text)

        w_e = read_expected('%s_words.pickle' % bigtext)
        p_e = read_expected('%s_phrases.pickle' % bigtext)

        assert w_e == dictify(w), 'word trie does not match for %s' % bigtext
        assert p_e == dictify(p), 'phrase trie does not match for %s' % bigtext


def test_autocomplete_small():
    # Autocomplete on simple tries with less than N valid words
    trie = lab.make_word_trie("cat car carpet")
    result = lab.autocomplete(trie, 'car', 3)
    assert set(result) == {"car", "carpet"}

    trie = lab.make_word_trie("a an ant anteater a an ant a")
    result = lab.autocomplete(trie, 'a', 2)
    assert set(result) in [{"a", "an"}, {"a", "ant"}]

    trie = lab.make_word_trie("man mat mattress map me met a man a a a map man met")
    result = lab.autocomplete(trie, 'm', 3)
    assert set(result) == {"man", "map", "met"}

    trie = lab.make_word_trie("hello hell history")
    result = lab.autocomplete(trie, 'help', 3)
    assert result == []
    with pytest.raises(TypeError):
        result = lab.autocomplete(trie, ('tuple', ), None)


def test_autocomplete_big_1():
    alphabet = a = "abcdefghijklmnopqrstuvwxyz"

    word_list = ["aa" + l1 + l2 + l3 + l4 for l1 in a for l2 in a for l3 in a for l4 in a]
    word_list.extend(["apple", "application", "apple", "apricot", "apricot", "apple"])
    word_list.append("bruteforceisbad")

    trie = lab.make_word_trie(' '.join(word_list))
    for i in range(1000):
        result1 = lab.autocomplete(trie, 'ap', 1)
        result2 = lab.autocomplete(trie, 'ap', 2)
        result3 = lab.autocomplete(trie, 'ap', 3)
        result4 = lab.autocomplete(trie, 'ap')

        assert set(result1) == {'apple'}
        assert set(result2) == {'apple', 'apricot'}
        assert set(result4) == set(result3) == {'apple', 'apricot', 'application'}


def test_autocomplete_big_2():
    nums = {'t': [0, 1, 25, None],
            'th': [0, 1, 21, None],
            'the': [0, 5, 21, None],
            'thes': [0, 1, 21, None]}
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
        text = f.read()
    w = lab.make_word_trie(text)
    for i in sorted(nums):
        for n in nums[i]:
            result = lab.autocomplete(w, i, n)
            expected = read_expected('frank_autocomplete_%s_%s.pickle' % (i, n))
            assert len(expected) == len(result), ('missing' if len(result) < len(expected) else 'too many') + ' autocomplete results for ' + repr(i) + ' with maxcount = ' + str(n)
            assert set(expected) == set(result), 'autocomplete included ' + repr(set(result) - set(expected)) + ' instead of ' + repr(set(expected) - set(result)) + ' for ' + repr(i) + ' with maxcount = '+str(n)
    with pytest.raises(TypeError):
        result = lab.autocomplete(w, ('tuple', ), None)


def test_autocomplete_big_3():
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
        text = f.read()
    w = lab.make_word_trie(text)
    the_word = 'accompany'
    for ix in range(len(the_word)+1):
        test = the_word[:ix]
        result = lab.autocomplete(w, test)
        expected = read_expected('frank_autocomplete_%s_%s.pickle' % (test, None))
        assert len(expected) == len(result), ('missing' if len(result) < len(expected) else 'too many') + ' autocomplete results for ' + repr(test) + ' with maxcount = ' + str(None)
        assert set(expected) == set(result), 'autocomplete included ' + repr(set(result) - set(expected)) + ' instead of ' + repr(set(expected) - set(result)) + ' for ' + repr(test) + ' with maxcount = '+str(None)
    with pytest.raises(TypeError):
        result = lab.autocomplete(w, ('tuple', ), None)


def test_autocomplete_big_phrase():
    nums = {('i', ): [0, 1, 2, 5, 11, None],
            ('i', 'do'): [0, 1, 2, 5, 8, None],
            ('i', 'do', 'not', 'like', 'them'): [0, 1, 2, 4, 100, None],
            ('i', 'do', 'not', 'like', 'them', 'here'): [0, 1, 2, 100, None]}
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'seuss.txt'), encoding='utf-8') as f:
        text = f.read()
    p = lab.make_phrase_trie(text)
    for i in sorted(nums):
        for n in nums[i]:
            result = lab.autocomplete(p, i, n)
            expected = read_expected('seuss_autocomplete_%s_%s.pickle' % (len(i), n))
            assert len(expected) == len(result), ('missing' if len(result) < len(expected) else 'too many') + ' autocomplete results for ' + repr(i) + ' with maxcount = ' + str(n)
            assert set(expected) == set(result), 'autocomplete included ' + repr(set(result) - set(expected)) + ' instead of ' + repr(set(expected) - set(result)) + ' for ' + repr(i) + ' with maxcount = '+str(n)

    with pytest.raises(TypeError):
        result = lab.autocomplete(p, 'string', None)


def test_autocorrect_small():
    # Autocorrect on cat in small corpus
    trie = lab.make_word_trie("cats cattle hat car act at chat crate act car act")
    result = lab.autocorrect(trie, 'cat',4)
    assert set(result) == {"act", "car", "cats", "cattle"}

def test_autocorrect_big():
    nums = {'thin': [0, 8, 10, None],
            'tom': [0, 2, 4, None],
            'mon': [0, 2, 15, 17, 20, None]}
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
        text = f.read()
    w = lab.make_word_trie(text)
    for i in sorted(nums):
        for n in nums[i]:
            result = lab.autocorrect(w, i, n)
            expected = read_expected('frank_autocorrect_%s_%s.pickle' % (i, n))
            print(result)
            print(expected)
            print()
            assert len(expected) == len(result), ('missing' if len(result) < len(expected) else 'too many') + ' autocorrect results for ' + repr(i) + ' with maxcount = ' + str(n)
            assert set(expected) == set(result), 'autocorrect included ' + repr(set(result) - set(expected)) + ' instead of ' + repr(set(expected) - set(result)) + ' for ' + repr(i) + ' with maxcount = '+str(n)


def test_filter_small():
    # Filter to select all words in trie
    trie = lab.make_word_trie("man mat mattress map me met a man a a a map man met")
    result = lab.word_filter(trie, '*')
    assert isinstance(result, list)
    result.sort()
    assert result == [("a", 4), ("man", 3), ("map", 2), ("mat", 1), ("mattress", 1), ("me", 1), ("met", 2)]

    # All three-letter words in trie
    result = lab.word_filter(trie, '???')
    assert isinstance(result, list)
    result.sort()
    assert result == [("man", 3), ("map", 2), ("mat", 1), ("met", 2)]

    # Words beginning with 'mat'
    result = lab.word_filter(trie, 'mat*')
    assert isinstance(result, list)
    result.sort()
    assert result == [("mat", 1), ("mattress", 1)]

    # Words beginning with 'm', third letter is t
    result = lab.word_filter(trie, 'm?t*')
    assert isinstance(result, list)
    result.sort()
    assert result == [("mat", 1), ("mattress", 1), ("met", 2)]

    # Words with at least 4 letters
    result = lab.word_filter(trie, '*????')
    assert isinstance(result, list)
    result.sort()
    assert result == [("mattress", 1)]

    # All words
    result = lab.word_filter(trie, '**')
    assert isinstance(result, list)
    result.sort()
    assert result == [("a", 4), ("man", 3), ("map", 2), ("mat", 1), ("mattress", 1), ("me", 1), ("met", 2)]


def test_filter_big_1():
    alphabet = a = "abcdefghijklmnopqrstuvwxyz"

    word_list = ["aa" + l1 + l2 + l3 + l4 for l1 in a for l2 in a for l3 in a for l4 in a]
    word_list.extend(["apple", "application", "apple", "apricot", "apricot", "apple"])
    word_list.append("bruteforceisbad")

    trie = lab.make_word_trie(' '.join(word_list))
    for i in range(1000):
        result = lab.word_filter(trie, "ap*")
        expected = {('apple', 3), ('apricot', 2), ('application', 1)}
        assert len(expected) == len(result), 'incorrect word_filter of ap*'
        assert set(expected) == set(result), 'incorrect word_filter of ap*'


def test_filter_big_2():
    patterns = ('*ing', '*ing?', '****ing', '**ing**', '????', 'mon*',
                '*?*?*?*', '*???')
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
        text = f.read()
    w = lab.make_word_trie(text)
    for ix, i in enumerate(patterns):
        result = lab.word_filter(w, i)
        expected = read_expected('frank_filter_%s.pickle' % (ix, ))
        assert len(expected) == len(result), 'incorrect word_filter of %r' % i
        assert set(expected) == set(result), 'incorrect word_filter of %r' % i


if __name__ == '__main__':
    import os
    import sys
    import json
    import pickle
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--gather", action='store_true')
    parser.add_argument("--server", action='store_true')
    parser.add_argument("--initial", action='store_true')
    parser.add_argument("args", nargs="*")

    parsed = parser.parse_args()


    class TestData:
        def __init__(self, gather=False):
            self.alltests = None
            self.results = {'passed': []}
            self.gather = gather

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtestloop(self, session):
            yield

        def pytest_runtest_logreport(self, report):
            if report.when != 'call':
                return
            self.results.setdefault(report.outcome, []).append(report.head_line)

        def pytest_collection_finish(self, session):
            if self.gather:
                self.alltests = [i.name for i in session.items]


    pytest_args = ['-v', __file__]

    if parsed.server:
        pytest_args.insert(0, '--color=yes')

    if parsed.gather:
        pytest_args.insert(0, '--collect-only')

    testinfo = TestData(parsed.gather)
    res = pytest.main(
        ['-k', ' or '.join(parsed.args), *pytest_args],
        **{'plugins': [testinfo]}
    )

    if parsed.server:
        _dir = os.path.dirname(__file__)
        if parsed.gather:
            with open(os.path.join(_dir, 'alltests.json'), 'w' if parsed.initial else 'a') as f:
                f.write(json.dumps(testinfo.alltests))
                f.write('\n')
        else:
            with open(os.path.join(_dir, 'results.json'), 'w' if parsed.initial else 'a') as f:
                f.write(json.dumps(testinfo.results))
                f.write('\n')

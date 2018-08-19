import marisa_trie
import re
import random

"""
nomenclature
a cell is a string combination of ABCD and 1234 i.e. "A1"
a path is a ordered list of cells that are adjacent to each other
"""

# constants
rows = "ABCD"
cols = "1234"
alphabet = 'abcdefghijklmnopqrstuvwxyz'
words = open('dictionary.txt').read().splitlines()
trie = marisa_trie.Trie(words)


def randomize_grid():
    """
    Create a grid with max 2 wildcard chars.
    May need to retry if the randomized grid has no solutions
    """
    cells = {}
    for row in rows:
        for col in cols:
            cells[row+col] = random.choice(alphabet)
    num_wildcards = random.randint(0, 2)
    if num_wildcards > 0:
        first_wildcard_cell = random.choice(list(cells.keys()))
        cells[first_wildcard_cell] = "*"
        # grid is less difficult if wildcards are not adjacent
        if num_wildcards == 2:
            second_wildcard_cell = random.choice(list(cells.keys()))
            while second_wildcard_cell in adjacent(first_wildcard_cell):
                second_wildcard_cell = random.choice(list(cells.keys()))
            cells[second_wildcard_cell] = "*"

    return cells


def adjacent(cell):
    """
    Given a cell, return adjacent cells.
    """
    i, j = rows.find(cell[0]), cols.find(cell[1])
    possible_rows = [rows[i] + cell[1] for i in [i+1, i-1] if i in range(4)]
    possible_cols = [cell[0] + cols[j] for j in [j+1, j-1] if j in range(4)]
    return possible_rows + possible_cols


def prune_substrings(strings):
    """
    Given a list of strings, remove substrings that are already represented by a longer string
    i.e. ["abc", "abcd"] -> ["abcd"]
    """
    # sort by length to reduce number of comparisons, because substring has to be shorter than the real string
    strings = sorted(strings, key=len)
    rtn = []
    for idx, val in enumerate(strings):
        if all(val not in k for k in strings[idx + 1:]):
            rtn.append(val)
    if len([j for i,j in enumerate(strings) if all(j == k or (j not in k) for k in strings[i+1:])]) != len(rtn):
        print(len([j for i,j in enumerate(strings) if all(j == k or (j not in k) for k in strings[i+1:])]), len(rtn))
    return [j for i,j in enumerate(strings) if all(j == k or (j not in k) for k in strings[i+1:])]


def path_to_letters(path, cells):
    """
    List of cells -> string
    """
    return "".join([cells[x] for x in path])


def wildcard_matches(letters, early_termination=True):
    """
    Given a sequence of letters, either return a boolean value if the sequence has a prefix
    or return all valid words
    """
    prefix_idx = letters.find("*")
    matches = set()

    # this can be slow
    if prefix_idx == 0:
        next_wildcard_idx = letters[1:].find("*")
        postfix = letters[1:] if next_wildcard_idx == -1 else letters[1:next_wildcard_idx]
        possibilities = []
        for c in alphabet:
            possibilities += trie.keys(c + postfix)
        possibilities = [w[next_wildcard_idx+1:] for w in possibilities]
        regex = re.compile(letters[next_wildcard_idx+1:].replace("*", "."))
        for possibility in possibilities:
            if re.match(regex, possibility):
                if early_termination:
                    return True
                word = letters[:prefix_idx] + possibility
                word = word[:len(letters)]
                if word in trie:
                    matches.add(word)

    else:
        possibilities = [w[prefix_idx:] for w in trie.keys(letters[:prefix_idx])]
        regex = re.compile(letters[prefix_idx:].replace("*", "."))
        for possibility in possibilities:
            if re.match(regex, possibility):
                if early_termination:
                    return True
                word = letters[:prefix_idx] + possibility
                word = word[:len(letters)]
                if word in trie:
                   matches.add(word)

    if early_termination:
        return False
    else:
        return list(matches)


def has_keys_with_prefix_and_wildcard(letters):
    """
    Supplement to marisa-trie's has_keys_with_prefix, but with wildcard support
    """
    prefix_idx = letters.find("*")

    if len(letters) == 1:
        return True
    # only 1 wildcard and its at the end
    elif prefix_idx == (len(letters) - 1):
        return trie.has_keys_with_prefix(letters[:-1])
    # wildcard at the start
    else:
        return wildcard_matches(letters)
    return False


def generate_longest_paths(cells):
    """
    Using depth-first search, explore all possible paths until each path
    cannot form a valid word
    """

    def iter(path):
        if path == []:
            possibilities = [k for k, v in cells.items()]
        else:
            letters = path_to_letters(path, cells)
            matches = (has_keys_with_prefix_and_wildcard(letters) if "*" in letters else
                        trie.has_keys_with_prefix(letters))

            # terminate useless paths early
            if matches:
                possibilities = [c for c in adjacent(path[-1]) if c not in path]
            else:
                possibilities = []

        if len(possibilities) == 0:
            # dead end means no more possibilities
            dead_end = path[:-1]
            sequence = path_to_letters(dead_end, cells)
            if sequence in paths:
                if dead_end not in paths[sequence]:
                    paths[sequence].append(dead_end)
            else:
                paths[sequence] = [dead_end]
            return

        for cell in possibilities:
            iter(path+[cell])

    paths = {}
    iter([])
    return(paths)


def solve(cells):
    """
    Take in a 4x4 grid of cells and returns the solutions.
    Solutions are returned as a dict with key-value pair of
    word and paths respectively.
    """

    # a path can be a sequence of letters "throwers"
    # and contain the valid words "throw", "thrower", "throwers"
    longest_paths = generate_longest_paths(cells)
    # cull the search space. if there is a path "throw" and "throwers",
    # we don't need to search "throw"
    unique_paths = {k: longest_paths[k] for k in prune_substrings(longest_paths.keys())}
    word_path_tuples = [(wildcard_matches(letters, early_termination=False), paths)
                        for letters, paths in unique_paths.items()]

    solutions = {}
    for words, paths in word_path_tuples:
        for word in words:
            for path in paths:
                if word in solutions:
                    solutions[word].append(path)
                else:
                    solutions[word] = [path]
    return solutions


def search(letters):
    """
    Using depth-first search, find all paths that match a given sequence of letters
    """

    def iter(letters, path):
        if len(letters) == 0:
            paths.append(path)
            return

        criteria = lambda v: v == "*" or v == letters[0]
        if path == []:
            possible_cells = [k for k, v in cells.items() if criteria(v)]
        else:
            adjacent_cells = {cell: cells[cell] for cell in adjacent(path[-1])}
            possible_cells = [k for k, v in adjacent_cells.items() if criteria(v)]
        if len(possible_cells) == 0:
            return

        for cell in possible_cells:
            iter(letters[1:], path+[cell])

    paths = []
    iter(letters, [])
    return(paths)


def tests():
    assert adjacent("B2") == ['C2', 'A2', 'B3', 'B1']
    assert adjacent("D4") == ['C4', 'D3']
    assert prune_substrings(["abc", "abcd"]) == ["abcd"]
    assert sorted(prune_substrings(['throw', 'throw*r', 'throw*rs'])) == sorted(["throw*rs"])
    assert sorted(prune_substrings(["abc", "abcd", "def", "deg"])) == sorted(["abcd", "def", "deg"])
    print ("All tests pass.")

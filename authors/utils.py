import re
from functools import lru_cache


ENCODING_ERRORS = {
    'Ã¡': 'á',
    'â€™': "'",
    'MarÃ­a': 'María',
    'fÃ¼r': "für",
    'KÃ¶nigstuhl': 'Königstuhl',
    'IngenierÃ­a': 'Ingeniería',
    'IbÃ¡Ã±ez': 'Ibáñez',
    'PeÃ±alolÃ©n': 'Peñalolén'
}


def argmin(seq):
    return min(range(len(seq)), key=lambda x : seq[x])

def argmax(seq):    
    return max(range(len(seq)), key=lambda x : seq[x])

def argsort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)


def lev_dist(a: str, b: str) -> float:
    """
    Calculates the Levenshtein distance between two input strings `a` and `b`

    Args:
        a, b (str) : The two strings to be compared

    Returns:
        The distance between string `a` and `b`.

    Examples:
        >>> lev_dist('stamp', 'stomp')
        1.0
    """

    @lru_cache(None)  # for memorization
    def min_dist(s1, s2):
        if s1 == len(a) or s2 == len(b):
            return len(a) - s1 + len(b) - s2
        # no change required
        if a[s1] == b[s2]:
            return min_dist(s1 + 1, s2 + 1)
        return 1 + min(
            min_dist(s1, s2 + 1),      # insert character
            min_dist(s1 + 1, s2),      # delete character
            min_dist(s1 + 1, s2 + 1),  # replace character
        )
    return min_dist(0, 0)


def bitapSearch(haystack, needle, maxErrors):
    """Bitap (Shift-Or) fuzzy searching algorithm with Wu-Manber modifications.
    http://habrahabr.ru/post/114997/
    http://habrahabr.ru/post/132128/
    http://ru.wikipedia.org/wiki/Двоичный_алгоритм_поиска_подстроки

    Search needle(pattern) in haystack(real word from text) with maximum alterations = maxErrors.
    If maxErrors equal 0 - execute precise searching only.

    Return approximately place of needle in haystack and number of alterations.
    If needle can't find with maxErrors alterations, return tuple of empty string and -1.
    """
    haystackLen = len(haystack)
    needleLen = len(needle)

    def _generateAlphabet(needle, haystack):
        """Genarating mask for each letter in haystack.
        This mask shows presence letter in needle.
        """
        alphabet = {}
        for letter in haystack:
            if letter not in alphabet:
                letterPositionInNeedle = 0
                for symbol in needle:
                    letterPositionInNeedle = letterPositionInNeedle << 1
                    letterPositionInNeedle |= int(letter != symbol)
                alphabet[letter] = letterPositionInNeedle
        return alphabet

    alphabet = _generateAlphabet(needle, haystack)

    table = [] # first index - over k (errors count, numeration starts from 1), second - over columns (letters of haystack)
    emptyColumn = (2 << (needleLen - 1)) - 1

    #   Generate underground level of table
    underground = []
    [underground.append(emptyColumn) for i in range(haystackLen + 1)]
    table.append(underground)
    # _printTable(table[0], needleLen)

    #   Execute precise matching
    k = 1
    table.append([emptyColumn])
    for columnNum in range(1, haystackLen + 1):
        prevColumn = (table[k][columnNum - 1]) >> 1
        letterPattern = alphabet[haystack[columnNum - 1]]
        curColumn = prevColumn | letterPattern
        table[k].append(curColumn)
        if (curColumn & 0x1) == 0:
            place = haystack[columnNum - needleLen : columnNum]
            return (place, k - 1)
    # _printTable(table[k], needleLen)

    #   Execute fuzzy searching with calculation Levenshtein distance
    for k in range(2, maxErrors + 2):
        # print("Errors =", k - 1)
        table.append([emptyColumn])

        for columnNum in range(1, haystackLen + 1):
            prevColumn = (table[k][columnNum - 1]) >> 1
            letterPattern = alphabet[haystack[columnNum - 1]]
            curColumn = prevColumn | letterPattern
            
            insertColumn = curColumn & (table[k - 1][columnNum - 1])
            deleteColumn = curColumn & (table[k - 1][columnNum] >> 1)
            replaceColumn = curColumn & (table[k - 1][columnNum - 1] >> 1)
            resColumn = insertColumn & deleteColumn & replaceColumn
            
            table[k].append(resColumn)
            if (resColumn & 0x1) == 0:
                startPos = max(0, columnNum - needleLen - 1) # taking in account Replace operation
                endPos = min(columnNum + 1, haystackLen) # taking in account Replace operation
                place = haystack[startPos : endPos]
                return (place, k - 1)
            
        # _printTable(table[k], needleLen)
    return ("", -1)


def closest_author(author, authors, closest=1, distance='bitap'):
    if distance == 'bitap':
        d = [bitapSearch(a, author, len(a))[1] for a in authors]
        return [authors[i] for i in argsort(d)[:closest]]


def find_bracket_last_name(name):
    last_name = None
    # can use "{last name}" to specify part of name which should not be changed
    if '{' in name and '}' in name:
        match = re.findall(r'\{(\w.+)\}', name)
        if len(match) == 1:
            last_name = match[0]
            name = name.replace('{' + match[0] + '}', '')
        return name, last_name

    # can also use "[last name]" to specify part of name which should not be changed
    if '[' in name and ']' in name:
        match = re.findall(r'\[(\w.+)\]', name)
        if len(match) == 1:
            last_name = match[0]
            name = name.replace('[' + match[0] + ']', '')
        return name, last_name

    return name, last_name


def name_to_last(name):
    if ' ' not in name:
        return name
    name, last_name = find_bracket_last_name(name)
    if last_name is not None:
        return last_name
    name = name.replace('  ', ' ')
    names = name.split(' ')
    return names[-1]


def name_to_initials_last(name):
    if ' ' not in name:
        return name

    name, last_name = find_bracket_last_name(name)

    name = name.replace('  ', ' ')
    names = name.split(' ')
    initials = []
    for n in names[:-1]:
        if '-' in n:
            initials.append('-'.join([f'{p[0]}.' for p in n.split('-')]))
        else:
            initials.append(n[0] + '.')
    name = initials
    if last_name is None:
        name.append(names[-1])
    else:
        name.append(last_name)
    return ' '.join(name)


def name_to_initials(name):
    name = name.replace('  ', ' ')
    names = name.split(' ')
    inititals = [n[0] for n in names]
    return inititals


def text_replace_dict(text, convert):
    regex = re.compile('|'.join(
        re.escape(str(key))
        for key in sorted(convert.keys(), key=lambda item: -len(item))))
    return regex.sub(lambda match: convert[match.group()], text)


def tex_escape(text):
    """ Escape `text` so it appears correctly in LaTeX """
    conv = {
        '&': r'\&',
        '|': r'$\|$',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        # '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    return text_replace_dict(text, conv)


def tex_deescape(text):
    """ De-escape `text` from TeX characters """
    conv = {
        # symbols
        r"’": "'",
        #
        r"\'a": 'á', "\'a": 'á',
        r"\`a": 'à', #r"\`a": 'à',
        r"\~a": 'ã', #r"\~a": 'ã',
        #
        r"\'e": 'é', "\'e": 'é',
        r"\´e": 'é',
        r"\’e": 'é',
        r"\`e": 'è', #r"\`e": 'è',
        #
        r"\'i": 'í', "\'i": 'í',
        r"\`i": 'ì', #r"\`i": 'ì',
        #
        r"\'o": 'ó', "\'o": 'ó',
        r"\`o": 'ò', #r"\`o": 'ò',
        r"\"o": 'ö', "\"o": 'ö',
        #
        r"\'u": 'ú', "\'u": 'ú',
        r"\'{u}": 'ú', "\'{u}": 'ú',
        r"\`u": 'ù',
        r"\`{u}": 'ù',
        r'\"u': 'ü',
        r'\"{u}': 'ü',
        #
        r"\~{n}": 'ñ',
        #
        r'\,': ' ',
        r'\ ': ' ',
        r'\&': '&',
        r'${\rm \mid}$': '|',
        r'{\rm \&}': '&',
    }
    escaped = text_replace_dict(text, conv)
    if "\\" in escaped:
        print(f'some characters not escaped: {escaped}')
    return escaped


def substr_in_list(sub, lst):
    for i, item in enumerate(lst):
        if sub in item:
            return True, i
    return False, None


def fix_encoding_errors(file):
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
    text = text_replace_dict(text, ENCODING_ERRORS)
    with open(file, 'w', encoding='utf-8') as f:
        f.write(text)

def humanize_yaml(file):
    import fileinput
    for line in fileinput.FileInput(file, inplace=True, encoding='utf-8'):
        if not line.startswith(' '):
            print()
        print(line, end='')

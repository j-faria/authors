import re
from functools import lru_cache


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


def name_to_last(name):
    if ' ' not in name:
        return name
    name = name.replace('{', '').replace('}', '')
    name = name.replace('  ', ' ')
    names = name.split(' ')
    return names[-1]


def name_to_initials_last(name):
    if ' ' not in name:
        return name
    if '{' in name and '}' in name:
        return name
    name = name.replace('  ', ' ')
    names = name.split(' ')
    name = [n[0] + '.' for n in names[:-1]]
    name.append(names[-1])
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
        '\\': r'\textbackslash{}',
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
        r"\`a": 'à', "\`a": 'à',
        r"\~a": 'ã', "\~a": 'ã',
        #
        r"\'e": 'é', "\'e": 'é',
        r"\´e": 'é',
        r"\’e": 'é',
        r"\`e": 'è', "\`e": 'è',
        #
        r"\'i": 'í', "\'i": 'í',
        r"\`i": 'ì', "\`i": 'ì',
        #
        r"\'o": 'ó', "\'o": 'ó',
        r"\`o": 'ò', "\`o": 'ò',
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

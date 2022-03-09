import re


def name_to_initials_last(name):
    if ' ' not in name:
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
        r"\'a": 'á',
        r"\`a": 'à',
        r"\~a": 'ã',
        r"\'e": 'é',
        r"\`e": 'è',
        r"\'i": 'í',
        r"\`i": 'ì',
        r"\'o": 'ó',
        r"\`o": 'ò',
        r"\'u": 'ú',
        r"\'{u}": 'ú',
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

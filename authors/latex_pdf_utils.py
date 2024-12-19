import os
import subprocess

_here_ = os.path.abspath(os.path.dirname(__file__))


def preview_AandA(text):
    template = os.path.join(_here_, 'templates', 'aa', 'aa-template.tex')
    output = os.path.join(_here_, 'templates', 'aa', 'aa.tex')
    assert os.path.exists(template)
    with open(template, 'r', encoding='utf-8') as fin:
        with open(output, 'w', encoding='utf-8') as fout:
            for line in fin.readlines():
                if "!!authors-institutes!!" in line:
                    print(text, file=fout)
                else:
                    print(line, end='', file=fout)

    path = os.path.join(_here_, 'templates', 'aa')
    subprocess.call('latexmk -f -pdf aa.tex'.split(), cwd=path)
    pdf = os.path.join(_here_, 'templates', 'aa', 'aa.pdf')
    os.startfile(pdf)


def preview_MNRAS(text):
    pass

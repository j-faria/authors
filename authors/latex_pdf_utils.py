import os
import subprocess

_here_ = os.path.abspath(os.path.dirname(__file__))

def fill_in_template(text, template, output):
    with open(template, 'r', encoding='utf-8') as fin:
        with open(output, 'w', encoding='utf-8') as fout:
            for line in fin.readlines():
                if "!!authors-institutes!!" in line:
                    print(text, file=fout)
                else:
                    print(line, end='', file=fout)

def compile_latex(wd, texname, pdfname, open_pdf=True):
    # print('compiling LaTeX...')
    out = subprocess.check_output(f'latexmk -f -pdf {texname}'.split(), cwd=wd)
    pdf = os.path.join(wd, pdfname)
    if open_pdf:
        os.startfile(pdf)
    return pdf


def preview_AandA(text, longauth=False, open_pdf=True):
    template = os.path.join(_here_, 'templates', 'aa', 'aa-template.tex')
    output = os.path.join(_here_, 'templates', 'aa', 'aa.tex')
    assert os.path.exists(template)
    fill_in_template(text, template, output)

    # longauth option to aa class
    with open(output, 'r', encoding='utf-8') as fin:
        text = fin.read()
        if longauth:
            text = text.replace('[??longauth??]', '[longauth]')
        else:
            text = text.replace('[??longauth??]', '')
    with open(output, 'w', encoding='utf-8') as fout:
        fout.write(text)
    ##

    path = os.path.join(_here_, 'templates', 'aa')
    pdf = compile_latex(path, 'aa.tex', 'aa.pdf', open_pdf)
    return pdf


def preview_MNRAS(text, open_pdf=True):
    template = os.path.join(_here_, 'templates', 'mnras', 'mnras-template.tex')
    output = os.path.join(_here_, 'templates', 'mnras', 'mnras.tex')
    assert os.path.exists(template)
    fill_in_template(text, template, output)
    path = os.path.join(_here_, 'templates', 'mnras')
    pdf = compile_latex(path, 'mnras.tex', 'mnras.pdf', open_pdf)
    return pdf


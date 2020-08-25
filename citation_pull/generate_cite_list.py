import os
from pathlib import Path
from pybtex.database.input import bibtex

CUR_PATH = Path.cwd()

parser = bibtex.Parser()
bib_data = parser.parse_file(CUR_PATH.joinpath('..','citations.bib'))
keys = bib_data.entries.keys()

with open (CUR_PATH.joinpath('..','docs/','hidden_cite.md'), 'w') as file:
    for key in keys:
        file.write('{cite}' + f'`{key}`' + '\n\n')


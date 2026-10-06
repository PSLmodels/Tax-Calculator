"""
Creates API documentation markdown files for each taxcalc module listed
in the MODULES dictionary, using the docstrings in the module source code.

The source code is parsed (rather than imported) so that the signatures
and docstrings of the functions decorated with iterate_jit are documented
instead of those of the JIT wrapper functions.
"""
# CODING-STYLE CHECKS:
# pycodestyle make_api.py
# pylint --disable=locally-disabled make_api.py

import os
import sys
import ast

CURDIR_PATH = os.path.abspath(os.path.dirname(__file__))

TAXCALC_PATH = os.path.join(CURDIR_PATH, '../../..', 'taxcalc')
OUTPUT_PATH = os.path.join(CURDIR_PATH, '..')

SOURCE_URL = 'https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc'

# Dictionary of documented modules (in alphabetical order) with page titles.
MODULES = {
    'behresp': 'Behavioral Responses',
    'calcfunctions': 'CalcFunctions',
    'calculator': 'Calculator',
    'consumption': 'Consumption',
    'data': 'Data',
    'decorators': 'Decorators',
    'growdiff': 'GrowDiff',
    'growfactors': 'GrowFactors',
    'parameters': 'Parameters',
    'policy': 'Policy',
    'records': 'Records',
    'taxcalcio': 'IO',
    'utils': 'Utilities',
    'utilsprvt': 'Private Utilities',
}

INDEX_TEXT = """# Tax-Calculator Python API

The Tax-Calculator's core capabilities are in the Python package
called taxcalc, the source code for which is located in the
Tax-Calculator/taxcalc directory tree.

Here we provide a view of the Python API of the taxcalc
package with links to the source code.  Below is a list
of the taxcalc package modules (in alphabetical order) with
documentation about how to call each class method and function.
There is also a link to the source code for each documented member.

"""


def main():
    """
    Generates the API index markdown file and one markdown file per module.
    """
    text = INDEX_TEXT
    for module, title in MODULES.items():
        text += f'- [taxcalc.{module}]({module}.md)\n'
        write_file(module_text(module, title), module)
    write_file(text, 'public_api')
    # Normal return code
    return 0


def module_text(module, title):
    """
    Returns markdown text documenting the specified module, which contains
    a section for each top-level function and class (including each method
    of a class) that has a docstring.
    """
    with open(os.path.join(TAXCALC_PATH, module + '.py'),
              'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    text = f'# Tax-Calculator {title}\n\n'
    text += f'Documentation of the `taxcalc.{module}` module.\n'
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            text += member_text(module, node, node.name, '##')
        elif isinstance(node, ast.ClassDef):
            text += member_text(module, node, node.name, '##')
            for subnode in node.body:
                if isinstance(subnode, ast.FunctionDef):
                    text += member_text(
                        module, subnode, f'{node.name}.{subnode.name}', '###'
                    )
    return text


def member_text(module, node, name, heading):
    """
    Returns markdown text documenting the function or class in node,
    or an empty string if node has no docstring.
    """
    docstring = ast.get_docstring(node)
    if not docstring:
        return ''
    if isinstance(node, ast.ClassDef):
        signature = f'class {node.name}({class_args(node)})'
    else:
        args = ast.unparse(node.args)
        signature = f'def {node.name}({args})'
    url = f'{SOURCE_URL}/{module}.py#L{node.lineno}'
    return (
        f'\n{heading} {name}\n\n'
        f'```python\n{signature}\n```\n\n'
        f'[source]({url})\n\n'
        f'```text\n{docstring}\n```\n'
    )


def class_args(node):
    """
    Returns string containing the arguments of the class constructor,
    excluding the self argument.
    """
    for subnode in node.body:
        if isinstance(subnode, ast.FunctionDef) and subnode.name == '__init__':
            args = subnode.args
            args.args = args.args[1:]
            return ast.unparse(args)
    return ''


def write_file(text, file):
    """
    Writes text to the markdown file with the specified name.
    """
    outfile = os.path.join(OUTPUT_PATH, file + '.md')
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(text)


if __name__ == '__main__':
    sys.exit(main())

"""
Writes redirect pages into the jupyter-book HTML build so that the page
URLs used by jupyter-book versions before 2.0 (for example,
guide/policy_params.html) still work after jupyter-book 2.0 changed
them (for example, to guide/policy-params).

Each redirect page points to the new URL with a trailing slash (for
example, /usage/data/) because GitHub Pages serves a usage/data.html
file, when one exists, in response to a /usage/data request.  Without
the trailing slash, a redirect page whose old URL differs from its new
URL only by the .html extension would redirect to itself forever.

Execute this script in the docs folder after the jupyter-book build.
"""
# CODING-STYLE CHECKS:
# pycodestyle make_redirects.py
# pylint --disable=locally-disabled make_redirects.py

import os
import sys
import json
import yaml

CURDIR_PATH = os.path.abspath(os.path.dirname(__file__))
MYST_PATH = os.path.join(CURDIR_PATH, 'myst.yml')
HTML_PATH = os.path.join(CURDIR_PATH, '_build', 'html')

REDIRECT_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Redirecting...</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
</head>
<body>
<p>This page has moved to <a href="{url}">{url}</a>.</p>
</body>
</html>
"""


def main():
    """
    Writes a redirect page for each old page URL that has no page.
    """
    with open(MYST_PATH, 'r', encoding='utf-8') as f:
        toc = yaml.safe_load(f)['project']['toc']
    with open(os.path.join(HTML_PATH, 'myst.xref.json'),
              'r', encoding='utf-8') as f:
        xref = json.load(f)
    new_urls = {ref['url'] for ref in xref['references']
                if ref['kind'] == 'page'}
    for path in toc_files(toc):
        old_page = os.path.splitext(path)[0] + '.html'
        new_url = new_page_url(path)
        if new_url not in new_urls:
            sys.stderr.write(f'ERROR: no {new_url} page for {path}\n')
            return 1
        old_page_path = os.path.join(HTML_PATH, old_page)
        if os.path.exists(old_page_path):
            continue
        os.makedirs(os.path.dirname(old_page_path), exist_ok=True)
        with open(old_page_path, 'w', encoding='utf-8') as f:
            f.write(REDIRECT_PAGE.format(url=redirect_url(new_url)))
    # Normal return code
    return 0


def toc_files(toc):
    """
    Returns list of file paths in the myst.yml table of contents.
    """
    files = []
    for entry in toc:
        if 'file' in entry:
            files.append(entry['file'])
        files.extend(toc_files(entry.get('children', [])))
    return files


def new_page_url(path):
    """
    Returns jupyter-book 2.0 page URL for the specified source file path.
    """
    slug = os.path.splitext(path)[0].lower().replace('_', '-')
    if slug == 'index':
        return '/'
    if slug.endswith('/index'):
        slug = slug[:-len('/index')]
    return '/' + slug


def redirect_url(url):
    """
    Returns specified page URL with a trailing slash, which GitHub Pages
    maps only to the page's index.html file.
    """
    if url.endswith('/'):
        return url
    return url + '/'


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python
from wiki import Wiki

def scrape_category(category, include_subcats):
    wiki = Wiki('http://wiki.eveuniversity.org')
    pages, subcategories = wiki.pages_by_category(category, include_subcats)
    subcat_pages = {}
    for subcat in subcategories:
        sub_titles = wiki.pages_by_category(subcat, False)[0]
        subcat_pages[subcat] = sub_titles
    return pages, subcat_pages

def add_info(text, name, pages):
    print(pages)
    if name.startswith('Category:'):
        name = name[9:]
    text = text.replace('{{{name}}}', name)
    text = text.replace('{{{links}}}', '<br>\n'.join('[[%s]]' % i for i in pages))
    return text

def build_sidebar(name, pages, subcategories):
    with open('base.txt') as base_file:
        text = base_file.read()
    text = add_info(text, name, pages)
    subcat_texts = []
    if subcategories:
        with open('subcat.txt') as base_file:
            base_text = base_file.read()
        for subname, subpages in subcategories.items():
            if subpages:
                subcat_texts.append(add_info(base_text, subname, subpages))
    text = text.replace('{{{subcats}}}', '\n'.join(subcat_texts))
    return text

def category_sidebar(name, fetch_subcats):
    pages, subcats = scrape_category(name, fetch_subcats)
    sidebar = build_sidebar(name, pages, subcats)
    return sidebar

def print_help():
    print('Usage:')
    print('createtemplate.py [--no-subcats] category')
    print('category is name of the category to use (with or without Category:)')
    print('--no-subcats will mean sub-categories are not passed')
    print('Passing no arguments will enter interactive mode')

def main(args):
    if len(args) > 2:
        print('Wrong number of arguments')
        quit()
    elif len(args) == 0:
        print('Enter the category you would like to fetch')
        name = raw_input()
        print('Am fetching subcategories, to overwrite enter any text '
              'otherwise press enter')
        fetch_subcats = not bool(raw_input())
    else:
        fetch_subcats = True
        for arg in args:
            if arg == '--no-subcats':
                fetch_subcats = False
            elif arg.startswith('-'):
                print('Unknown option %s' % arg)
                quit()
            elif not name:
                name = arg
            else:
                print_help()
    print(category_sidebar(name, fetch_subcats))

if __name__ == '__main__':
    from sys import argv
    main(argv[1:])

# -*- coding: utf-8 -*-
import os

from itertools import product

# CSS_DICT_FILENAME = 'core/CSS-dict.txt'
CSS_DICT_FILENAME = 'CSS-dict.txt'

# парсер формата файла с css-правилами

COMMENT = '//'

def read_file(filename):
    filepath = os.path.join('.', filename)
    if os.path.exists(filepath):
        filename = filepath
    else:
        filename = os.path.join('.', 'core', filename)
    with open(filename) as file_dict:
        for line in file_dict:
            line = line.strip()
            # skip comments
            if line.lstrip().startswith(COMMENT):
                continue
            # added extra markup
            if not line:
                line = ':'
            # strip comment at the end line
            if COMMENT in line:
                line = line[:line.find(COMMENT)]
            yield line

FILE_DATA = list(read_file(CSS_DICT_FILENAME))

def parse_dict(lines):
    tokenize = ' '.join(lines).split(':')
    cleanup = [line.strip() for line in tokenize if line.strip()]
    properties = (tuple(p.strip() for p in prop.split(',') if p.strip()) for prop in cleanup[::2])
    values = (tuple(v.strip() for v in value.split('|')) for value in cleanup[1::2])
    parsed = zip(properties, values)
    del cleanup, properties, values, tokenize, lines

    css = []
    # TODO: заменить на functools
    for properties, values in parsed:
        for p in properties:
            for v in values:
                css.append((p, v))
    parsed_dict = {}
    for k, v in css:
        parsed_dict.setdefault(k, set()) # заменить на defaultdict?
        parsed_dict[k].add(v)
    return parsed_dict

def expand_values(parsed_dict, properties):
    if not properties:
        return parsed_dict
    prop = properties.pop()
    for name, values in parsed_dict.items():
        # todo: пересмотреть алгоритм
        if name in parsed_dict[prop] and name.startswith('<'):
            parsed_dict[prop] |= values
            properties.append(name)
    return expand_values(parsed_dict, properties)

def flat_dict(dict_):
    arr = []
    for k, v in dict_.items():
        arr.extend(product((k,), v))
    return arr

def props_dict():
    pd = parse_dict(FILE_DATA)
    new_dict = {}
    for k, val in pd.items():
        v = (i for i in val if '<' not in i and not i.startswith('.'))
        new_dict[k] = (list(v),)
    return new_dict

def flat_css_dict():
    """Возвращает список (свойство, возможное_значение)"""
    pd = parse_dict(FILE_DATA)
    all_pd = expand_values(pd, pd.keys())
    return flat_dict(all_pd)

if __name__ == '__main__':
    pd = parse_dict(FILE_DATA)
    all_pd = expand_values(pd, pd.keys())
    for p, v in flat_dict(all_pd):
        if v in ('<number>', '<attr>') or p == 'top':
            # print p, v
            pass

    di = [val for prop, val in flat_css_dict() if prop == 'caption-side']
    print di
    print len(di)
    print expand_values(pd, pd.keys())['caption-side']
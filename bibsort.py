#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from collections import OrderedDict
import codecs

class BibEntry:
    
    def __init__(self, **kwargs):
        self.data = {}
        for key, value in kwargs.iteritems():
            self.data[key] = value
    
    def entry(self):
        data = OrderedDict(sorted(self.data.items(), key=lambda t: t[0]))
        result = u'@{0}{{{1},\n'.format(self.data['type'].upper(), self.data['key'])
        for key, value in data.items():
            if key in ['type','key']:
                continue
            result += u'\t{0} = {{{1}}},\n'.format(key, value)
        result = result[:-2] + u'\n}\n'
        return result
        

 
def must_omit(i):
    return re.match("comment", i) or re.match("%%", i)

def entries_from_file(file):

    keywords = ['address', 'annote', 'author', 'booktitle', 'chapter', 'crossref',
                'doi', 'edition', 'editor', 'eprint', 'eprintclass', 'eprinttype',
                'howpublished', 'institution', 'journal', 'month', 'note', 'number', 
                'organization', 'pages', 'publisher', 'school', 'series', 'title', 
                'type', 'url', 'urldate', 'volume', 'year']

    with codecs.open(file, "r", "utf-8") as f:
        text = f.read()

    entries = []

    entry_blocks = [i for i in re.split("\n@", text) if not must_omit(i)]

    for entry in entry_blocks:
        
        entry_dict = {}
        
        search = re.match("(?P<type>.*){(?P<key>.*)", entry)
        if search:

            key = search.group("key")[:-1]

            if search.group("type").startswith('@'):
                type = search.group("type")[1:]
            else:
                type = search.group("type")

            entry_dict["key"] = key
            entry_dict["type"] = type

        for keyword in keywords:
            string = "\s*"+keyword+"\s*=\s*[{]?(?P<"+keyword+">\S.*),?\n"
            search = re.search(string, entry)
            if search:
                # Prohibits that 'eprinttype' overrides 'type'
                if keyword in entry_dict.keys():
                    continue
                value = search.group(keyword)
                if value.endswith(','):
                    value = value[:-1]
                if value.endswith('}}'):
                    value = value[:-1]
                if value.endswith('}') and not value.startswith('{'):
                    value = value[:-1]
                entry_dict[keyword] = value

        if entry_dict != {}:
            entries.append(BibEntry(**entry_dict))

    return entries


BibEntries = entries_from_file('bibliography.bib')
BibEntries.sort(key=lambda x: x.data['key'].lower())

for _ in BibEntries:
    print _.entry()
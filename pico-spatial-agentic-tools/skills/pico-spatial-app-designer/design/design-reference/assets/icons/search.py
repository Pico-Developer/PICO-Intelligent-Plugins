#!/usr/bin/env python3
"""Search the portable ICON 7.0 catalog. Python 3.9+; no dependencies."""

import argparse
from collections import Counter
import difflib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
STOP_WORDS = set('a an the to for of on in at with and or by from current selected icon icons please need want find me show that can be is it'.split())
QUERY_ALIASES = {
    'logout': 'sign out', 'signout': 'sign out', 'log out': 'sign out', 'login': 'sign in',
    'log in': 'sign in', 'wifi': 'wi fi', 'wi-fi': 'wi fi',
    'full screen': 'fullscreen', 'mic': 'microphone', 'bt': 'bluetooth',
    'preferences': 'settings', 'magnify': 'zoom in', 'sbs': 'side by side',
    'picture in picture': 'picture in picture', 'pip': 'picture in picture',
    'hmd': 'headset', 'pingpong': 'table tennis', 'ping pong': 'table tennis',
}


def normalize(value):
    return ' '.join(re.findall(r'[a-z0-9]+', value.lower()))


def stem(word):
    if len(word) > 4 and word.endswith('ies'):
        return word[:-3] + 'y'
    if len(word) > 4 and word.endswith('s') and not word.endswith(('ss', 'us')):
        return word[:-1]
    return word


def tokens(value):
    return [stem(t) for t in normalize(value).split() if t not in STOP_WORDS]


def expand_query(query):
    result = normalize(query)
    for alias, replacement in sorted(QUERY_ALIASES.items(), key=lambda p: -len(p[0])):
        result = re.sub(r'\b' + re.escape(normalize(alias)) + r'\b', replacement, result)
    return result


def searchable(entry):
    return ' '.join([entry['name'], entry['title'], entry['recommended_use'], entry['category'], entry['style'],
                     ' '.join(entry['keywords']), ' '.join(entry['aliases']), ' '.join(entry.get('visual_keywords', []))])


def search(query='', category=None, style=None, limit=10, icon_id=None):
    """Return ranked catalog entries with absolute paths and match evidence."""
    catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    entries = catalog['icons']
    docs = [Counter(tokens(searchable(e))) for e in entries]
    vocabulary = set().union(*(d.keys() for d in docs))
    expanded = expand_query(query)
    query_tokens = list(dict.fromkeys(tokens(expanded)))
    corrected = {}
    for word in query_tokens:
        if word not in vocabulary and len(word) >= 4:
            matches = difflib.get_close_matches(word, sorted(vocabulary), n=1, cutoff=0.84)
            if matches:
                corrected[word] = matches[0]
    effective = [corrected.get(w, w) for w in query_tokens]
    frequencies = Counter(w for d in docs for w in d)
    average_length = sum(sum(d.values()) for d in docs) / len(docs)
    results = []
    for entry, document in zip(entries, docs):
        if category and entry['category'] != category:
            continue
        if style and entry['style'] != style:
            continue
        if icon_id and entry['id'].lower() != icon_id.lower():
            continue
        exact = bool(query and any(normalize(query) == normalize(value) for value in [entry['id'], entry['name'], entry['path'], *entry['aliases']]))
        matched = sorted(set(effective).intersection(document))
        if query and not exact and (not effective or len(matched) != len(set(effective))):
            continue
        score = 0.0
        for word in set(effective):
            count = document[word]
            if count:
                inverse_frequency = math.log(1 + (len(entries) - frequencies[word] + 0.5) / (frequencies[word] + 0.5))
                score += inverse_frequency * count * 2.2 / (count + 1.2 * (0.25 + 0.75 * sum(document.values()) / average_length))
        if effective:
            score += 12 * len(matched) / len(set(effective))
            if len(matched) == len(set(effective)):
                score += 10
        if expanded and expanded in normalize(entry['recommended_use']):
            score += 18
        if expanded and expanded in normalize(entry['name'].removeprefix('ic_')):
            score += 14
            if expanded == normalize(entry['name'].removeprefix('ic_')):
                score += 30
        if expanded and any(expanded == normalize(k) for k in entry['keywords']):
            score += 12
        if exact:
            score += 1000
        results.append({**entry, 'absolute_path': str(ROOT / entry['path']),
                        'score': round(score, 4), 'matched_terms': matched,
                        'match_kind': 'exact' if exact or icon_id else ('fuzzy' if corrected else ('keyword' if query else 'browse'))})
    results.sort(key=lambda e: (-e['score'], e['name'], e['id']))
    return {'query': query, 'expanded_query': expanded, 'corrections': corrected,
            'total': len(results), 'returned': min(limit, len(results)),
            'results': results[:limit]}


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('must be greater than zero')
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', nargs='?', default='', help='English name, intent, keywords, or exact asset name')
    parser.add_argument('--id', dest='icon_id', help='Resolve one stable catalog ID, such as ICON7-P001')
    parser.add_argument('--category', choices=[c['name'] for c in json.loads((ROOT / 'catalog.json').read_text())['categories']])
    parser.add_argument('--style', choices=['filled', 'outline', 'unspecified'])
    parser.add_argument('--limit', type=positive_int, default=10)
    output = parser.add_mutually_exclusive_group()
    output.add_argument('--json', action='store_true', help='Return structured JSON for agents')
    output.add_argument('--paths', action='store_true', help='Print only resource paths')
    output.add_argument('--svg', action='store_true', help='Print SVG markup; requires --id')
    parser.add_argument('--absolute', action='store_true', help='Use absolute paths in text and --paths output')
    parser.add_argument('--list-categories', action='store_true')
    args = parser.parse_args()
    if args.list_categories:
        categories = json.loads((ROOT / 'catalog.json').read_text())['categories']
        print(json.dumps(categories, indent=2) if args.json else '\n'.join(f"{c['name']}\t{c['count']}" for c in categories))
        return 0
    if args.icon_id and args.query:
        parser.error('use either a query or --id')
    if args.svg and not args.icon_id:
        parser.error('--svg requires --id to select one unambiguous resource')
    result = search(args.query, args.category, args.style, args.limit, args.icon_id)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    elif args.svg:
        if result['results']:
            print((ROOT / result['results'][0]['path']).read_text(), end='')
    elif args.paths:
        for entry in result['results']:
            print(entry['absolute_path'] if args.absolute else entry['path'])
    else:
        print(f"{result['total']} matches; showing {result['returned']}.")
        if result['corrections']:
            print('Spelling suggestions: ' + ', '.join(f'{k} -> {v}' for k, v in result['corrections'].items()))
        for entry in result['results']:
            path = entry['absolute_path'] if args.absolute else entry['path']
            print(f"\n{entry['id']}  {entry['name']}  [{entry['category']} / {entry['style']}]")
            print('  ' + entry['recommended_use'])
            print('  ' + path)
            if entry['requires_confirmation']:
                print('  Meaning or interaction requires confirmation.')
        if not result['results']:
            print('No matching icons. Try a shorter English query or another category.', file=sys.stderr)
    return 0 if result['results'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

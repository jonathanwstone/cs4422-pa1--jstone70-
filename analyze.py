import argparse
import json
import collections
from urllib.parse import urlparse, parse_qsl
import re

parser = argparse.ArgumentParser(description='Web Crawler Analysis')

def loadJson(file):
    useable = []
    with open(file, "r", encoding= 'utf-8') as jsonFile:

        for line in jsonFile:
            line = line.strip()
            if not line:
                continue
            else:
                try:
                    line = json.loads(line)
                    useable.append(line)
                except json.JSONDecodeError:
                    continue
    return useable

def analyzeEvents(crawl):
    collect = collections.Counter([])
    for event in crawl:
        if event['event']:
            collect[event['event']]+=1
    return collect

def analyzeFailures(crawl):
    collect = collections.Counter([])
    for event in crawl:
        if event['event'] == 'error':
            collect[event['failure_reason']]+=1
    return collect.most_common( 5)

def analyzeDupes(pages):
    collect = collections.Counter([])
    for page in pages:
        if page['word_count'] != 0:
            collect[page['content_hash']]+=1
    return collect.most_common(5)

def countDuplicateGroups(pages):
    collect = collections.Counter([])
    duplicateGroups = 0
    for page in pages:
        if page['word_count'] > 0:
            collect[page['content_hash']]+=1
    for item in collect:
        if collect[item] > 1:
            duplicateGroups +=1
    return duplicateGroups

def countDuplicatePages(pages):
    counter = collections.Counter([])
    count = 0
    for page in pages:
        if page["word_count"] !=0:
            counter[page['content_hash']]+=1
    for object in counter:
        if counter[object]>1:
            count+=counter[object]
    return count

def duplicateHashCheck(pages, dupes):
    collect = []
    for dupe in dupes:
        for page in pages:
            if dupe[0] == page['content_hash']:
                pageInfo = {
                    'url': page['url_canonical'],
                    'canonical_link': page['canonical_link'],
                    'word_count': page['word_count']
                }
                collect.append(pageInfo)
    return collect


if __name__ == "__main__":
    parser.add_argument('--pages', default='artifacts/pages.jsonl',
                        help='Page file')
    parser.add_argument('--crawl', default='artifacts/crawl.log',
                        help='Crawl log file')
    parser.add_argument('--stats', default='artifacts/stats.jsonl',
                        help='Crawler final stats file')

    args = parser.parse_args()
    crawl = loadJson(args.crawl)
    pages = loadJson(args.pages)
    stats = loadJson(args.stats)

    crawlLog = analyzeEvents(crawl)
    failures = analyzeFailures(crawl)
    dupes = analyzeDupes(pages)
    hash = countDuplicateGroups(pages)
    print(duplicateHashCheck(pages, dupes))
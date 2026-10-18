import argparse
import json
import collections
import urllib
from urllib.parse import urlparse, parse_qsl
import re
from datetime import datetime
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
            if 'retrying' in event['failure_reason'] or event['url'].endswith("/robots.txt"):
                continue
            label = event['failure_reason']

            if label is not None:
              label = event['failure_reason'],event['status']

            collect[label]+=1
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

def getUrlPattern(url):
    temp = []
    pathUrl = urlparse(url).path
    queryUrl = urlparse(url).query
    repairedUrl = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '<id>', pathUrl)
    patchedUrl = re.sub(r'\d{4}-\d{2}-\d{2}' , '<date>', repairedUrl)
    cleansedUrl = re.sub(r'\d+', repl= '<num>', string = patchedUrl)
    pairs = parse_qsl(queryUrl)
    for key, value in pairs:
        temp.append(key)
    newQuery = '&'.join(temp)
    if newQuery != '':
        cleansedUrl = cleansedUrl + '?' + newQuery
    return cleansedUrl

def analyzeUrlPatterns(pages):
    patterns = {}
    Tracker =[]

    for page in pages:
        pattern = getUrlPattern(page['url_canonical'])
        if pattern not in patterns:
            patterns[pattern] = {
                'url': set(),
                'hashes': set()
            }
        patterns[pattern]["url"].add(page["url_canonical"])
        if page["word_count"] > 0:
            patterns[pattern]["hashes"].add(page["content_hash"])

    for pattern in patterns:
        Tracker.append((pattern,(len(patterns[pattern]["url"]),len(patterns[pattern]["hashes"]))))
    Tracker.sort(key =lambda patterns: patterns[1][0], reverse = True)
    Tracker = Tracker[0:9]
    return Tracker

def getShingles(text, k=3):
    words = text.lower().split()
    return set(" ".join(words[i: i + k]) for i in range(len(words) - k + 1))

def jaccardSim(text1,text2):
    A = getShingles(text1, k=3)
    B = getShingles(text2, k=3)
    top = len(A&B)
    bottom = len(A|B)

    if bottom == 0:
        return 0

    jaccard = top/bottom

    return jaccard

def analyzeFailureHosts(crawl):
    collect = collections.Counter([])
    for entry in crawl:
        if entry['status'] == 403 and not entry['url'].endswith("/robots.txt"):
            collect[urlparse(entry['url']).netloc] +=1
    return collect.most_common(5)

def analyzeGaps(crawl):
    storage = {}

    for item in crawl:
        if item['event'] != 'fetch' or item['url'].endswith("/robots.txt"):
            continue
        else:
            if urlparse(item['url']).netloc not in storage:
                timestamp = datetime.fromisoformat(item['time_stamp'])
                timestamp = datetime.timestamp(timestamp)
                host = urlparse(item['url']).netloc
                storage[host] = []
                storage[host].append(timestamp)

            else:
                name = urlparse(item['url']).netloc
                timestamp = datetime.fromisoformat(item['time_stamp'])
                timestamp = datetime.timestamp(timestamp)
                storage[name].append(timestamp)

    return storage

def floorGap(storage):

    exception = {
        "catalog.kennesaw.edu": 120,
        "bookstore.kennesaw.edu": 10.0
    }

    default = 1.0

    for host, times in storage.items():
        if len(times) < 2:
            continue
        sortTime = sorted(times)

        gap = [t2 -t1 for t1, t2 in zip(sortTime, sortTime[1:])]

        floor = exception.get(host, default)

        fetches = len(sortTime)
        smallestGap = min(gap)
        underFloor = sum(1 for item in gap if item < floor)

        print(f"Host: {host}", f" fetches: {fetches}", f" Smallest gap: {smallestGap:.3f}",f"Floor: {floor}" ,f" Under floor: {underFloor}")

def analyzeRobotsSkips(crawl):
    collection = collections.Counter([])
    for item in crawl:
        if item['event'] == 'skip':
            host = urlparse(item['url']).netloc
            if 'disallow' in item['failure_reason']:
                collection[(host, 'disallowed')]+=1
            if ('unavailable' in item['failure_reason']) or ('could not be retrieved' in item['failure_reason']):
                collection[(host, 'unavailable')]+=1
    print(collection.most_common())

def analyzeCrawlRate(crawl,stats):
    times =[]
    gaps = []
    for entry in crawl:
        time = datetime.fromisoformat(entry['ts']).timestamp()
        times.append(time)

    for i in range(len(times) - 1):
        gap = times[i + 1] - times[i]
        gaps.append(gap)
    largestGap = max(gaps)
    index = gaps.index(largestGap)
    pagesFetched = stats[0]['pages_fetched']
    timeTaken = stats[0]['Time_Taken']

    takenRate = pagesFetched/timeTaken
    adjustedRate = pagesFetched/(timeTaken - largestGap)

    return [largestGap, takenRate, crawl[index]['ts'], crawl[index+1]['ts'] ,adjustedRate]
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
    duplicateGroups = countDuplicateGroups(pages)
    duplicatePages = countDuplicatePages(pages)
    duplicateExamples = duplicateHashCheck(pages, analyzeDupes(pages))
    rate = analyzeCrawlRate(crawl, stats)
    urlPatterns = analyzeUrlPatterns(pages)

    print(len(pages))
    print(len(crawl))
    print(analyzeEvents(crawl))
    print(stats)
    print(urlPatterns)
    print(duplicateGroups)
    print(duplicatePages)
    print(analyzeFailures(crawl))
    print(duplicateExamples)
    analyzeRobotsSkips(crawl)
    floorGap(analyzeGaps(crawl))
    print(rate)
    print(analyzeFailureHosts(crawl))
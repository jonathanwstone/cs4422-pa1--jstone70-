import argparse
import json
import collections
import urllib
from urllib.parse import urlparse, parse_qsl
import re
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer

parser = argparse.ArgumentParser(description='Web Crawler Analysis')


def loadJson(file):
    useable = []
    with open(file, "r", encoding='utf-8') as jsonFile:

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
            collect[event['event']] += 1
    return collect


def analyzeFailures(crawl):
    collect = collections.Counter([])
    for event in crawl:
        if event['event'] == 'error':
            if 'retrying' in event['failure_reason'] or event['url'].endswith("/robots.txt"):
                continue
            label = event['failure_reason']

            if label is not None:
                label = event['failure_reason'], event['status']

            collect[label] += 1
    return collect.most_common(5)


def analyzeDupes(pages):
    collect = collections.Counter([])
    for page in pages:
        if page['word_count'] != 0:
            collect[page['content_hash']] += 1
    return collect.most_common(5)


def countDuplicateGroups(pages):
    collect = collections.Counter([])
    duplicateGroups = 0
    for page in pages:
        if page['word_count'] > 0:
            collect[page['content_hash']] += 1
    for item in collect:
        if collect[item] > 1:
            duplicateGroups += 1
    return duplicateGroups


def countDuplicatePages(pages):
    counter = collections.Counter([])
    count = 0
    for page in pages:
        if page["word_count"] != 0:
            counter[page['content_hash']] += 1
    for object in counter:
        if counter[object] > 1:
            count += counter[object]
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
    patchedUrl = re.sub(r'\d{4}-\d{2}-\d{2}', '<date>', repairedUrl)
    cleansedUrl = re.sub(r'\d+', repl='<num>', string=patchedUrl)
    pairs = parse_qsl(queryUrl)
    for key, value in pairs:
        temp.append(key)
    newQuery = '&'.join(temp)
    if newQuery != '':
        cleansedUrl = cleansedUrl + '?' + newQuery
    return cleansedUrl


def analyzeUrlPatterns(pages):
    patterns = {}
    Tracker = []

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
        Tracker.append((pattern, (len(patterns[pattern]["url"]), len(patterns[pattern]["hashes"]))))
    Tracker.sort(key=lambda patterns: patterns[1][0], reverse=True)
    Tracker = Tracker[0:10]
    return Tracker


def getShingles(text, k=3):
    words = text.lower().split()
    return set(" ".join(words[i: i + k]) for i in range(len(words) - k + 1))


def jaccardSim(text1, text2):
    A = getShingles(text1, k=3)
    B = getShingles(text2, k=3)
    top = len(A & B)
    bottom = len(A | B)

    if bottom == 0:
        return 0

    jaccard = top / bottom

    return jaccard


def analyzeFailureHosts(crawl):
    collect = collections.Counter([])
    for entry in crawl:
        if entry['status'] == 403 and not entry['url'].endswith("/robots.txt"):
            collect[urlparse(entry['url']).netloc] += 1
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

        gap = [t2 - t1 for t1, t2 in zip(sortTime, sortTime[1:])]

        floor = exception.get(host, default)

        fetches = len(sortTime)
        smallestGap = min(gap)
        underFloor = sum(1 for item in gap if item < floor)

        print(f"Host: {host}", f" fetches: {fetches}", f" Smallest gap: {smallestGap:.3f}", f"Floor: {floor}",
              f" Under floor: {underFloor}")


def analyzeRobotsSkips(crawl):
    collection = collections.Counter([])
    for item in crawl:
        if item['event'] == 'skip':
            host = urlparse(item['url']).netloc
            if 'disallow' in item['failure_reason']:
                collection[(host, 'disallowed')] += 1
            if ('unavailable' in item['failure_reason']) or ('could not be retrieved' in item['failure_reason']):
                collection[(host, 'unavailable')] += 1
    print(collection.most_common())


def analyzeCrawlRate(crawl, stats):
    times = []
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

    takenRate = pagesFetched / timeTaken
    adjustedRate = pagesFetched / (timeTaken - largestGap)

    return [largestGap, takenRate, crawl[index]['ts'], crawl[index + 1]['ts'], adjustedRate]


def topOutgoing(pages):
    counts = []
    for entry in pages:
        counts.append((len(entry['out_links']), entry['url_canonical']))
    counts.sort(reverse=True)
    return counts[0:5]


def topIncoming(pages):
    count = collections.Counter([])
    for entry in pages:
        for item in entry['out_links']:
            count[item] += 1
    return count.most_common(8)


def countZeroWordPages(pages):
    zeroWordCount = []
    for entry in pages:
        if int(entry['word_count']) == 0:
            zeroWordCount.append(entry['url_canonical'])
    print("There are " + str(len(zeroWordCount)) + " urls with a zero word count, examples are: " + str(
        zeroWordCount[0:3]))


def analyzeRepeatedLines(pages):
    repeatedLines = collections.Counter([])
    repeatSet = set()
    halfPages = len(pages) / 2

    for entry in pages:

        for line in {line.strip() for line in entry['text'].splitlines() if line.strip()}:
            if line:
                repeatedLines[line] += 1

    for line, count in repeatedLines.items():
        if count >= halfPages:
            repeatSet.add(line)
    return repeatSet


def removeBoilerplate(pageText, boilerplate):
    fullString = []
    for line in pageText.splitlines():
        line = line.strip()
        if line in boilerplate:
            continue
        else:
            fullString.append(line)
    sentence = "\n".join(fullString)
    return sentence


def meanOriginalWordCount(pages):
    originalLength = 0
    for page in pages:
        originalLength += len(page['text'].split())

    return originalLength / len(pages)


def meanPostRemoval(pages, boilerplate):
    meanLengthPostRemoval = 0
    for page in pages:
        pageMinusRemoved = removeBoilerplate(page['text'], boilerplate)
        meanLengthPostRemoval += len(pageMinusRemoved.split())
    return meanLengthPostRemoval / len(pages)


def longestPages(pages):
    pageLength = []

    for page in pages:
        newRecord = {
            'url': page['url_canonical'],
            'word_count': len(page['text'].split())
        }
        pageLength.append(newRecord)

    pageLength = sorted(pageLength, key=lambda item: item['word_count'], reverse=True)

    return pageLength[0:5]


def longestMinusBoilerplate(pages, boilerplate):
    wordCount = []

    for page in pages:
        cleanedText = removeBoilerplate(page['text'], boilerplate)
        wordCount.append({
            'url': page['url_canonical'],
            'word_count': len(cleanedText.split())
        })
    wordCount = sorted(wordCount, key=lambda item: item['word_count'], reverse=True)

    return wordCount[0:5]


def boilerComparison(pages, boilerplate):
    comparison = []
    longest = longestPages(pages)
    noBoilerplate = longestMinusBoilerplate(pages, boilerplate)
    for original in longest:
        for cleaned in noBoilerplate:
            if original['url'] == cleaned['url']:
                size = original['word_count'] - cleaned['word_count']
                comparison.append({
                    'url': original['url'],
                    'word_count_difference': size
                })
    print(comparison)


def analyzeBoilerplatePerPage(pages, boilerplate):
    analyzed = []
    for page in pages:
        originalCount = len(page['text'].split())
        noBoilerCount = len((removeBoilerplate(page['text'], boilerplate)).split())
        if originalCount == 0:
            continue
        storeThis = originalCount - noBoilerCount
        store = {
            'url': page['url_canonical'],
            'original_text_amount': originalCount,
            'text_amount_after_removal': noBoilerCount,
            'difference': storeThis,
            'percent_removed': round(((storeThis / originalCount) * 100), 2)
        }
        analyzed.append(store)
    return analyzed

def topWords(pages):
    count = collections.Counter([])
    for entry in pages:
        theString = entry['text'].lower()
        items = re.findall(r"\b[a-z]+\b",theString)
        count.update(items)
    return count.most_common(30)

def topWordsMinusStop(pages):
    rules = set(stopwords.words('english'))
    count = collections.Counter([])
    for entry in pages:
        theString = entry['text'].lower()
        items = re.findall(r"\b[a-z]+\b", theString)
        for word in items:
            if word in rules:
                continue
            count[word]+=1
    return count.most_common(30)

def wordFrequencies(pages):
    count = collections.Counter([])
    for entry in pages:
        lowerText = entry['text'].lower()
        items = re.findall(r"\b[a-z]+\b", lowerText)
        for item in items:
            count[item]+=1
    return count

def wordFrequenciesMinusStop(pages):
    count = collections.Counter([])
    rules = set(stopwords.words('english'))
    for entry in pages:
        lowerText = entry['text'].lower()
        items = re.findall(r"\b[a-z]+\b", lowerText)
        for item in items:
            if item in rules:
                continue
            count[item] += 1
    return count

def fitZipf(frequencies):
    sortedWords = frequencies.most_common()
    frequenciesOnly = [item[1] for item in sortedWords]
    ranks = np.arange(1,stop = len(frequenciesOnly)+1)
    logRanks = np.log10(ranks)
    logFrequencies = np.log10(frequenciesOnly)
    slope, intercept = np.polyfit(logRanks, logFrequencies, 1)
    exponent = -slope
    meanLog = np.mean(logFrequencies)
    predicted = slope * logRanks + intercept
    totalSumSquares = np.sum((logFrequencies - meanLog) ** 2)
    residualSumSquares = np.sum((logFrequencies - predicted) ** 2)
    r2 = (1-(residualSumSquares/totalSumSquares))

    deviations = []
    for i in range(len(sortedWords)):
        residual = logFrequencies[i] - predicted[i]
        deviations.append((sortedWords[i][0], residual))
    sortedDeviations = sorted(deviations, key=lambda item: abs(item[1]), reverse=True)

    return exponent, slope, intercept, r2, sortedDeviations[:10]

def analyzeTfidf(pages):
    vectorizer = TfidfVectorizer(stop_words = 'english')
    sampledPages = random.sample(pages, 5)
    documents = [page['text'] for page in sampledPages]
    tfidfMatrix = vectorizer.fit_transform(documents)
    featureNames = vectorizer.get_feature_names_out()
    for i, page in enumerate(sampledPages):
        scores = tfidfMatrix[i].toarray().flatten()
        sortedScores = np.argsort(scores)[::-1][:5]
        for i in range(5):
            print('URL: ', page['url_canonical'])
            print(featureNames[sortedScores[i]], scores[sortedScores[i]])
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
    print(topOutgoing(pages))
    print(topIncoming(pages))
    countZeroWordPages(pages)
    boilerplate = analyzeRepeatedLines(pages)
    print("Mean words before removal:", meanOriginalWordCount(pages))
    print("Mean words after removal:", meanPostRemoval(pages, boilerplate))

    print("\nTop 5 longest pages BEFORE removal:")
    print(longestPages(pages))

    print("\nTop 5 longest pages AFTER removal:")
    print(longestMinusBoilerplate(pages, boilerplate))


    results = analyzeBoilerplatePerPage(pages, boilerplate)
    print(results[:5])
    addedPercents = 0
    for items in results:
        addedPercents += items['percent_removed']
    avgPercent = (addedPercents / len(results))
    print("Mean Percent Removed: ", round(avgPercent, 2))

    print("Top 30 before stopword removal:", topWords(pages))
    print("Top 30 after stopword removal:", topWordsMinusStop(pages))

    exponent, slope, intercept,r2, deviations = fitZipf(wordFrequencies(pages))
    exponentStopRemoved, slopeStopRemoved, interceptStopRemoved,r2StopRemoved, deviationsStopRemoved = fitZipf(wordFrequenciesMinusStop(pages))
    print("Zipf exponent before stopword removal:", exponent)
    print("Zipf exponent after stopword removal:", exponentStopRemoved)
    print(r2)
    print(r2StopRemoved)
    print("Biggest deviations without stops removed ", deviations)
    print("Biggest deviations with stops removed",deviationsStopRemoved)
    print(analyzeTfidf(pages))

    from collections import Counter

    hash_counts = Counter(
        page["content_hash"]
        for page in pages
        if page["word_count"] > 0
    )

    duplicate_groups = sum(
        count > 1 for count in hash_counts.values()
    )

    excess_duplicate_pages = sum(
        count - 1
        for count in hash_counts.values()
        if count > 1
    )

    print("Exact normalized-text duplicate groups:", duplicate_groups)
    print("Excess duplicate pages:", excess_duplicate_pages)
    print("Percentage of fetched pages:", excess_duplicate_pages / len(pages) * 100)
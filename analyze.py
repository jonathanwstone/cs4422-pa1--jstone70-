import argparse
import json
import collections

def loadMyFile(crawl):
    crawlLog =[]
    counter = 0
    with open(crawl, 'r', encoding = 'utf-8') as json_data:
        for line in json_data:
            line = line.strip()
            if not line:
                continue
            else:
                try:
                    printable = json.loads(line)
                    crawlLog.append(printable)

                except json.JSONDecodeError:
                    counter+=1
                    continue
    return crawlLog, counter
def loadStatsData(stats):
    with open (stats, 'r', encoding = 'utf-8') as json_data:
        statsData = json.load(json_data)
        return statsData

def sortFetch(rawFileContents):
    fetches = []
    robotFetches = []
    for line in rawFileContents:
        if line['event'] == ('fetch')and not line['url'].endswith('/robots.txt'):
            fetches.append(line)
        if line['event'] == ('fetch')and line['url'].endswith('/robots.txt'):
            robotFetches.append(line)

    return fetches, robotFetches

parser = argparse.ArgumentParser(description = 'Web Crawler Analysis')

if __name__ == "__main__":
    parser.add_argument('--pages', default = 'artifacts/pages.jsonl', help = 'Page file')
    parser.add_argument('--crawl', default='artifacts/crawl.log', help='Crawl log file')
    parser.add_argument('--stats', default='artifacts/stats.jsonl', help='Crawler final stats file')

    args = parser.parse_args()

    fileContents, skipped = loadMyFile(args.crawl)
    sortFetch(fileContents)

# imports
import datetime
import hashlib
import posixpath
import time
import json
import requests
import bs4
import lxml
import protego
import urllib.parse
# specific pulls from each import group
from urllib import response
from urllib.parse import urlsplit, parse_qsl
from collections import deque
from datetime import datetime, timezone

from lxml.etree import canonicalize
from protego import Protego


# examples used for earlier testing
# page = requests.get('https://www.kennesaw.edu/')
# page.headers.get('Content-Type')
# len(page.text)
# soup = bs4.BeautifulSoup(page.text,'lxml')
# print(soup.title.string)
# print(soup.find_all('a')[:100])

pageCount = 0
budget = 10
toScan = deque()
seen = set()
robotsCache = {}
myInfo = 'CrawlerProject: jstone70@students.kennesaw.edu'
lastFetchTime = {}
defaultDelay = 1.0

# Canonizes everything to make sure we have a consistent url style we are fetching
# makes sure pages with slightly different fragments do not overlap and pull twice
def makeCanon(toCanon):

    # Break apart url in order to canonize
    split = urlsplit(toCanon)

    scheme = split.scheme.lower()

    # Takes netloc and removes default ports, used to keep us from scanning page multiple times
    netloc = split.netloc.lower()
    if ':' in netloc:
        splitNetloc = netloc.split(':')

        # Actual point in which we remove the port addresses.
        if (scheme == 'http' and splitNetloc[1] == "80") or(scheme == 'https' and splitNetloc[1] =="443"):
            netloc = splitNetloc[0]

    # normalizes path so we do not get repeat pages if the path has variations such as (academic/..../events/calendar
    # which is not different from events/calendar
    path = urllib.parse.quote(urllib.parse.unquote(split.path), safe="/-._~")
    path = posixpath.normpath(path)
    if path == '.':
        path = '/'

    # Block list used to stop us from repeating pages that are caused by separate queries (EX. Facebook, Instagram)
    query = split.query
    queryBlockList = ['utm_source','utm_medium','utm_campaign','utm_term']
    cleanQuery = []
    queryFix = parse_qsl(query)
    for item in queryFix:
        if item[0] not in queryBlockList:
            cleanQuery.append(item)

    cleanQuery.sort()
    query = urllib.parse.urlencode(cleanQuery)


    # Removes fragment for canonization
    fragment = ''
    # reform and return full url now canonized
    return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))

# parses and checks robots.txt per netloc to make sure we are following the rules
def checkRobots(robotsCache,netloc, scheme):

    if netloc in robotsCache:
        return robotsCache[netloc]
    enforceDelay(lastFetchTime, netloc, defaultDelay)
    try:
        request = requests.get(f"{scheme}://{netloc}/robots.txt", timeout = 10)
    except requests.exceptions.RequestException:
        robotsCache[netloc] = 'Denied'
        return robotsCache[netloc]

    if 400 <= request.status_code < 500 and request.status_code != 429:
        requestParsed = Protego.parse(request.text)
        robotsCache[netloc] = requestParsed
    if 500 <= request.status_code:
        robotsCache[netloc] = 'Denied'
    if 200 <= request.status_code < 300 :
        requestParsed = Protego.parse(request.text)
        robotsCache[netloc] = requestParsed

    return robotsCache[netloc]

# The actual big bad crawler
def crawler(starting, pageCount, budget):
    canonStart = makeCanon(starting)
    toScan.append(canonStart)
    seen.add(canonStart)

    while len(toScan) != 0 and pageCount < budget:


        url = toScan.popleft()  # Pulls URL out of left side of double ended queue

        robotHost = urllib.parse.urlsplit(url).netloc
        robotScheme = urllib.parse.urlsplit(url).scheme
        robotsResult = checkRobots(robotsCache, robotHost, robotScheme)
        if robotsResult == 'Denied' or not robotsResult.can_fetch(url, myInfo):
            continue

        # calculate and enforce delay
        siteDelay = robotsResult.crawl_delay(myInfo)
        requiredDelay = max(defaultDelay, siteDelay or defaultDelay)
        enforceDelay(lastFetchTime, robotHost, requiredDelay)


        page = redirectHandler(url)


        if page is None:
            continue


        if not(200<= page.status_code < 300):
            continue

        if 'text/html' not in page.headers.get('Content-Type',''):
            continue

        content_length = page.headers.get('Content-Length')
        if content_length and int(content_length) > 5_000_000:
            continue

        soup = bs4.BeautifulSoup(page.text, 'lxml')  # provides the page html to the parser (lxml in this case)
                                                             # then makes it readable
        pageCount += 1
        outLinks = []

        for link in soup.find_all('a') : # loop 2: one link per pass
            toCanon = link.get('href')
            if toCanon is None:
                continue

            # Ignores redirects to things such as email/call
            if toCanon.startswith('#') or toCanon.startswith('mailto:') or toCanon.startswith('javascript:') or toCanon.startswith('tel:'):
                continue

            absolute = urllib.parse.urljoin(url, toCanon)
            host = urllib.parse.urlsplit(absolute).netloc
            if not (host == 'kennesaw.edu' or host.endswith('.kennesaw.edu')): # Checks host, if host is not related to KSU skip
                continue
            canon = makeCanon(absolute)  # See makeCanon comments

            # Final extra check to make sure canon is able to parse and scan
            if canon is not None:
                outLinks.append(canon)
                # Makes sure we have not parsed and scanned
                if canon not in seen:
                    seen.add(canon)
                    toScan.append(canon)
        outLinks = list(set(outLinks))
        record = buildRecord(page, soup, url, outLinks)
        print(record)

# Checks for needed delay time based on host or on preset if preset is longer
def enforceDelay(lastFetchTime, host, requiredDelay):
    if host in lastFetchTime:
        elapsed = time.time() - lastFetchTime[host]
        if elapsed < requiredDelay:
            time.sleep(requiredDelay - elapsed)

        lastFetchTime[host] = time.time()
    else:
        lastFetchTime[host] = time.time()

def redirectHandler(url, maxHops = 5):
    visited = []
    hopCount = 0
    while hopCount < maxHops:
        if url in visited:
            return
        else:
            host = urllib.parse.urlsplit(url).netloc
            enforceDelay(lastFetchTime, host, defaultDelay)
            visited.append(url)
            if hopCount >= maxHops:
                return
            else:
                try:
                    check = requests.get(url, headers={'User-Agent': myInfo}, timeout= 10.0, allow_redirects=False)
                except requests.exceptions.Timeout:
                    return
                except requests.exceptions.RequestException:
                    return

                if check.is_redirect or (300 <= check.status_code < 400):
                    location = check.headers.get('Location')
                    url = urllib.parse.urljoin(url, location)

                    host = urllib.parse.urlsplit(url).netloc
                    if not (host == 'kennesaw.edu' or host.endswith('.kennesaw.edu')):
                        return None

                    hopCount += 1
                else:
                    return check

    return None

def buildRecord(page, soup, canon, outLinks):
    title = soup.title.string if soup.title is not None else ''
    text = soup.get_text()
    normalize = ' '.join(text.lower().split())
    normalizedBytes = normalize.encode('utf-8')

    canonicalTag = soup.find('link', rel='canonical')
    if canonicalTag is not None:
        link = canonicalTag.get('href')
    else:
        link = None
    # this is what we need built
    return {
        'url_canonical': canon,
        'status': page.status_code,
        'fetched_at': datetime.now(timezone.utc).isoformat() ,
        'title': title,
        'text': text,
        'word_count': len(text.split()),
        'out_links': outLinks,
        'content_hash': hashlib.sha256(normalizedBytes).hexdigest() ,
        'canonical_link': link
    }

crawler('https://www.kennesaw.edu/', pageCount, budget) # Commented out till ready

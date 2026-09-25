import posixpath
from urllib import response
from urllib.parse import urlsplit, parse_qsl

import requests
import bs4
import lxml
import protego
import urllib.parse
from collections import deque

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
budget = 100
toScan = deque()
seen = set()
robotsCache = {}
myInfo = 'CrawlerProject: jstone70@students.kennesaw.edu'


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


def checkRobots(robotsCache,netloc, scheme):
    if netloc in robotsCache:
        return robotsCache[netloc]

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

def crawler(starting, pageCount, budget):
    toScan.append(starting)
    seen.add(starting)

    while len(toScan) != 0 and pageCount < budget:
        url = toScan.popleft()  # Pulls URL out of left side of double ended queue

        robotHost = urllib.parse.urlsplit(url).netloc
        robotScheme = urllib.parse.urlsplit(url).scheme
        robotsResult = checkRobots(robotsCache, robotHost, robotScheme)
        if robotsResult == 'Denied' or not robotsResult.can_fetch(url, headers = {myInfo}):
            continue


        try:
            page = requests.get(url, headers={'User-Agent': myInfo})  # sets the page
        except requests.exceptions.RequestException:
            continue
        except requests.exceptions.Timeout:
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

                # Makes sure we have not parsed and scanned
                if canon not in seen:
                    seen.add(canon)
                    toScan.append(canon)

                    # Used to make sure objects to scan is growing
                    # print(toScan)

crawler('https://www.kennesaw.edu/', pageCount, budget) # Commented out till ready



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


# examples used for earlier testing
# page = requests.get('https://www.kennesaw.edu/')
# page.headers.get('Content-Type')
# len(page.text)
# soup = bs4.BeautifulSoup(page.text,'lxml')
# print(soup.title.string)
# print(soup.find_all('a')[:100])

def makeCanon(toCanon):
    split = urlsplit(toCanon)

    scheme = split.scheme.lower()

    # Takes netloc and removes default ports
    netloc = split.netloc.lower()
    if ':' in netloc:
        splitNetloc = netloc.split(':')
        if (scheme == 'http' and splitNetloc[1] == "80") or(scheme == 'https' and splitNetloc[1] =="443"):
            netloc = splitNetloc[0]

    # normalizes path so we do not get repeat pages if the path has variations such as (academic/..../events/calendar
    # which is not different from events/calendar
    path = urllib.parse.quote(urllib.parse.unquote(split.path), safe="/-._~")
    path = posixpath.normpath(path)
    if path == '.':
        path = '/'

    query = split.query
    queryBlockList = ['utm_source','utm_medium','utm_campaign','utm_term']
    cleanQuery = []
    queryFix = parse_qsl(query)
    for item in queryFix:
        if item[0] not in queryBlockList:
            cleanQuery.append(item)
    query = urllib.parse.urlencode(cleanQuery)



    fragment = ''

    return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))

def crawler(starting):
    pageCount = 0
    budget = 100
    toScan = deque()
    seen = set()
    toScan.append(starting)
    seen.add(starting)

    while len(toScan) != 0 and pageCount < budget:
        url = toScan.popleft()
        page = requests.get(url)
        soup = bs4.BeautifulSoup(page.text, 'lxml')
        pageCount += 1

        for link in soup.find_all('a') : # loop 2: one link per pass
            toCanon = link.get('href')
            if toCanon is None:
                continue
            else:
                canon = makeCanon(urllib.parse.urljoin(url, toCanon))
            if canon is not None:

                if canon not in seen:
                    seen.add(canon)
                    toScan.append(canon)
                    print(toScan)
crawler('https://www.kennesaw.edu/') # Commented out till ready to use

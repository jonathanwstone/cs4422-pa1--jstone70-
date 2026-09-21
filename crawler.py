from urllib import response
from urllib.parse import urlsplit

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
    split.scheme = split.scheme.lower()
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
            canon = toCanon
            if canon is not None:

                if canon not in seen:
                    seen.add(canon)
                    toScan.append(canon)
                    print(toScan)
crawler('https://www.kennesaw.edu/')
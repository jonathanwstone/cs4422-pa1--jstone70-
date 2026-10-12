# imports
import hashlib
import os
import posixpath
import time
import json
import requests
import bs4
import urllib.parse

# specific pulls from each import group
from urllib.parse import urlsplit, parse_qsl
from collections import deque
from datetime import datetime, timezone
from protego import Protego
from email.utils import parsedate_to_datetime

pageCount = 0
budget = 5
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

    # Check if robots has already been checked
    if netloc in robotsCache:
        return robotsCache[netloc]
    enforceDelay(lastFetchTime, netloc, defaultDelay)

    #Pull robots.txt
    try:
        request = requests.get(f"{scheme}://{netloc}/robots.txt", timeout = 10, headers={'User-Agent': myInfo})

    # If server timesout
    except requests.exceptions.Timeout:
        robotsCache[netloc] = 'Timeout error'
        logEvent('error', f"{scheme}://{netloc}/robots.txt", failure_reason=robotsCache[netloc], status=None)
        return robotsCache[netloc]

    # If access is denied
    except requests.exceptions.RequestException:
        robotsCache[netloc] = 'Could not retrieve robots.txt ruleset, request failed'
        logEvent('error', f"{scheme}://{netloc}/robots.txt", failure_reason=robotsCache[netloc], status=None)
        return robotsCache[netloc]

    # If server says we have made too many requests or server is unavailable
    if request.status_code == 429 or request.status_code == 503:

        # Check for a wait time, if there is one cast to int, if not assign 10 and wait to
        # request again, making sure to log time
        waitTime = request.headers.get('Retry-After')
        if waitTime is None:
            waitTime = 10
        else:

            try:
                waitTime = int(waitTime)
            except ValueError:
                getThis = parsedate_to_datetime(waitTime)
                waitTime = max(0, (getThis - datetime.now(timezone.utc)).total_seconds())

        logEvent('retry', f"{scheme}://{netloc}/robots.txt", failure_reason='429/503, retrying robots.txt',
                 status=request.status_code)
        time.sleep(waitTime)

        # Check again
        try:
            request = requests.get(f"{scheme}://{netloc}/robots.txt", timeout=10,headers={'User-Agent': myInfo})
        except requests.exceptions.Timeout:
            robotsCache[netloc] = 'Timeout error'
            logEvent('error', f"{scheme}://{netloc}/robots.txt", failure_reason = robotsCache[netloc], status = None)
            return robotsCache[netloc]
        except requests.exceptions.RequestException:
            robotsCache[netloc] = 'Could not retrieve robots.txt ruleset, request failed'
            logEvent('error', f"{scheme}://{netloc}/robots.txt", failure_reason=robotsCache[netloc], status=None)
            return robotsCache[netloc]

        # If there is a second 429/503 error send out as too many requests otherwise pass it on
        if request.status_code == 429 or request.status_code == 503:
            robotsCache[netloc] = 'Could not retrieve robots.txt ruleset, request failed'
            logEvent('error', f"{scheme}://{netloc}/robots.txt", failure_reason=robotsCache[netloc], status=request.status_code)
            return robotsCache[netloc]

    # Error handling for thrown codes
    if 400 <= request.status_code < 500 and request.status_code != 429:
        robotsCache[netloc] = 'Could not retrieve robots.txt ruleset, request failed'
        logEvent('error', f"{scheme}://{netloc}/robots.txt", failure_reason=robotsCache[netloc], status=request.status_code)
        return robotsCache[netloc]
    if 500 <= request.status_code:
        robotsCache[netloc] = 'Could not retrieve robots.txt ruleset, request failed'
        logEvent('error', f"{scheme}://{netloc}/robots.txt", failure_reason=robotsCache[netloc], status=request.status_code)
        return robotsCache[netloc]
    if 200 <= request.status_code < 300 :
        requestParsed = Protego.parse(request.text)
        robotsCache[netloc] = requestParsed
        logEvent('success', f"{scheme}://{netloc}/robots.txt", failure_reason=None, status=request.status_code)
    if 300 <= request.status_code < 400:
        robotsCache[netloc] = 'Could not retrieve robots.txt ruleset, request failed'
        logEvent('error', f"{scheme}://{netloc}/robots.txt", failure_reason=robotsCache[netloc],
                 status=request.status_code)
        return robotsCache[netloc]
    return robotsCache[netloc]

# Check content length
def readLimitedResponse(response, maxBytes=5_000_000):
    byteArray = bytearray()
    totalBytes = 0
    try:
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            else:
                totalBytes += len(chunk)
                if totalBytes > maxBytes:
                    return None
            byteArray.extend(chunk)
        return byteArray
    finally:
        response.close()

# The actual big bad crawler
def crawler(starting, pageCount, budget):
    os.makedirs('artifacts', exist_ok = True)
    canonStart = makeCanon(starting)
    toScan.append(canonStart)
    logEvent('enqueue', canonStart)
    seen.add(canonStart)

    while len(toScan) != 0 and pageCount < budget:


        url = toScan.popleft()  # Pulls URL out of left side of double ended queue

        robotHost = urllib.parse.urlsplit(url).netloc
        robotScheme = urllib.parse.urlsplit(url).scheme
        robotsResult = checkRobots(robotsCache, robotHost, robotScheme)
        if isinstance(robotsResult, Protego) == False:
            logEvent('skip', url, failure_reason='Robots.txt could not be retrieved')
            continue
        if not robotsResult.can_fetch(url, myInfo):
            logEvent('skip', url, failure_reason='Robots.txt disallows')
            continue

        # calculate and enforce delay
        siteDelay = robotsResult.crawl_delay(myInfo)
        requiredDelay = max(defaultDelay, siteDelay or defaultDelay)
        enforceDelay(lastFetchTime, robotHost, requiredDelay)


        page = redirectHandler(url)


        if page is None:
            logEvent('error', url, failure_reason='Page is none')
            continue


        if not(200<= page.status_code < 300):
            logEvent('error', url, failure_reason= "Non 200 response", status = page.status_code)
            page.close()
            continue

        if 'text/html' not in page.headers.get('Content-Type',''):
            logEvent('error', url, failure_reason= 'Non text/html response', status= page.status_code)
            page.close()
            continue



        contentLengthCheck = readLimitedResponse(page)


        if contentLengthCheck is None:
            logEvent('error', url, failure_reason='Content exceeded maximum', status=page.status_code)
            continue


        soup = bs4.BeautifulSoup(bytes(contentLengthCheck), 'lxml')  # provides the page html to the parser (lxml in this case)
                                                             # then makes it readable
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
                    logEvent('enqueue', canon)
        outLinks = list(set(outLinks))
        record = buildRecord(page, soup, url, outLinks)
        appendRecord(record)
        pageCount += 1
        logEvent('success', url, status = page.status_code)
    if pageCount == budget:
        logEvent('complete when page limit reached', canonStart)
    else:
        logEvent('queue exhausted', canonStart)

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
            logEvent('error', url, 'redirect loop detected')
            return None
        else:
            host = urllib.parse.urlsplit(url).netloc
            enforceDelay(lastFetchTime, host, defaultDelay)
            scheme = urllib.parse.urlsplit(url).scheme
            robotsResult = checkRobots(robotsCache, host, scheme)
            if not isinstance(robotsResult, Protego) or not robotsResult.can_fetch(url, myInfo):
                return None
            visited.append(url)

            try:
                    check = requests.get(url, headers={'User-Agent': myInfo}, timeout= 10.0, allow_redirects=False, stream = True)
            except requests.exceptions.Timeout:
                logEvent('error', url, failure_reason= 'Timeout', status=None)
                return None
            except requests.exceptions.RequestException:
                logEvent('error', url, failure_reason='Exception', status=None)
                return None

            if 300 <= check.status_code < 400:

                location = check.headers.get('Location')
                if location is not None:
                    url = urllib.parse.urljoin(url, location)

                    host = urllib.parse.urlsplit(url).netloc

                    if not (host == 'kennesaw.edu' or host.endswith('.kennesaw.edu')):
                        check.close()
                        return None

                    hopCount += 1
                    check.close()
                    continue
                else:
                    logEvent('error', url, failure_reason ='missing location')
                    check.close()
                    return None

            if check.status_code == 429 or check.status_code == 503:

                # Check for a wait time, if there is one cast to int, if not assign 10 and wait to
                # request again, making sure to log time
                waitTime = check.headers.get('Retry-After')

                if waitTime is None:
                    waitTime = 10
                else:
                    try:
                        waitTime = int(waitTime)
                    except ValueError:
                        getThis = parsedate_to_datetime(waitTime)
                        waitTime = max(0, (getThis - datetime.now(timezone.utc)).total_seconds())

                logEvent('error', url, failure_reason='429/503, retrying',
                         status=check.status_code)
                time.sleep(waitTime)
                check.close()

                # Check again
                host = urllib.parse.urlsplit(url).netloc
                try:
                    check = requests.get(url, headers={'User-Agent': myInfo}, timeout= 10.0, allow_redirects=False, stream = True)
                except requests.exceptions.Timeout:
                    logEvent('error', url, failure_reason='Timeout',
                             status=None)
                    return None
                except requests.exceptions.RequestException:
                    logEvent('error', url, failure_reason='Exception',
                             status=None)
                    return None

                if 300 <= check.status_code < 400:

                    location = check.headers.get('Location')
                    if location != None:
                        url = urllib.parse.urljoin(url, location)

                        host = urllib.parse.urlsplit(url).netloc

                        if not (host == 'kennesaw.edu' or host.endswith('.kennesaw.edu')):
                            check.close()
                            return None

                        hopCount += 1
                        check.close()
                        continue
                    else:
                        logEvent('error', url, failure_reason='missing location')
                        check.close()
                        return None

                if check.status_code != 429 and check.status_code != 503:
                    return check
                # If there is a second 429/503 error send out as too many requests otherwise pass it on
                if check.status_code == 429 or check.status_code == 503:
                    logEvent('error', url, failure_reason='too many retries',
                             status=check.status_code)
                    check.close()
                    return None

            else:
                return check
    logEvent('error', url, failure_reason='exceeded hop counts')
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

def appendRecord(record):

    # Open the path and pages.json
    with open('artifacts/pages.jsonl', "a") as jsonFile:
        # Append the record
        json.dump(record, jsonFile)
        jsonFile.write("\n")

def logEvent(event, url, failure_reason = None, status = None):
    log = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'event': event,
        'url': url,
        'failure_reason': failure_reason,
        'status': status
    }
    with open ('artifacts/crawl.log', "a") as jsonFile:

        json.dump(log, jsonFile)
        jsonFile.write("\n")


crawler('https://www.kennesaw.edu/', pageCount, budget) # Commented out till ready


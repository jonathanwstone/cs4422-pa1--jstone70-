Q1:
A:  [('/index.php?catoid', (30, 30)), ('/content.php?catoid&navoid', (23, 0)), ('/', (7, 7)), ('/apply.php', (1, 1)), ('/visit.php', (1, 1)), ('/give.php', (1, 1)), ('/calendar.php', (1, 1)), ('/president/cabinet.php', (1, 1)), ('/admissions/undergraduate/admission-requirements/transfer.php', (1, 1))]
    index.php?catoid makes up about 6%
    content.php makes up about 4.6%

B:  these were our most common patterns, it contains roughly 30 distinct content hashes. This makes me believe that the URL's
    produced different content. The distinct hashes do not alone prove that those pages all have distinct content though
    content was our second largest consisting of 23 distinct URLs but contains zero distinct content hashes. This is due to 
    the records not containing a positive word count. I believe this was a crawler trap, and possible unlimited, but cannot conclude that without auditing
    the responses.
    other distinct patterns include homepage patters with 7 urls and 7 distinct hashes. The remaining listed patters each contain
    one URL
    the best way to check would be to use a catalog id in the future to check if they respond with new content, repeated content
    errors or redirects.

C:  The largest pattern used 6% of my 500-page budget, and the second-largest used 4.6%. Together, these patterns account for 53 of the 500 crawled pages, or 10.6% of the crawl budget.
    I would still allow index.php sice it produced 30 distinct hashes but would investigate content because each URL has a 
    non positive word count. I would edit it to put in a check that if it followed 10 out links that all contained 0 word count it would no longer follow
    those outlinks
Q2:
    A: [{'url': 'https://catalog.kennesaw.edu/', 'canonical_link': None, 'word_count': 820}, {'url': 'https://catalog.kennesaw.edu/index.php?catoid=84', 'canonical_link': None, 'word_count': 820}, {'url': 'https://catalog.kennesaw.edu/index.php', 'canonical_link': None, 'word_count': 820}, {'url': 'https://www.kennesaw.edu/', 'canonical_link': 'https://www.kennesaw.edu/index.php', 'word_count': 782}, {'url': 'https://www.kennesaw.edu/directories.php', 'canonical_link': 'https://www.kennesaw.edu/index.php', 'word_count': 782}, {'url': 'https://www.kennesaw.edu/request-info.php', 'canonical_link': 'https://www.kennesaw.edu/request-info.php', 'word_count': 686}, {'url': 'https://www.kennesaw.edu/request-info.php?major=Request+Info+&url=https%3A%2F%2Fwww.kennesaw.edu%2Frequest-info.php', 'canonical_link': 'https://www.kennesaw.edu/request-info.php', 'word_count': 686}, {'url': 'https://www.kennesaw.edu/admissions/undergraduate/admission-requirements/freshman.php', 'canonical_link': 'https://www.kennesaw.edu/admissions/undergraduate/admission-requirements/freshman.php', 'word_count': 2215}, {'url': 'https://admissions.kennesaw.edu/admissions-requirements/freshmen.php', 'canonical_link': 'https://www.kennesaw.edu/admissions/undergraduate/admission-requirements/freshman.php', 'word_count': 2215}, {'url': 'https://www.kennesaw.edu/privacy-statement.php', 'canonical_link': 'https://www.kennesaw.edu/privacy-statement.php', 'word_count': 2036}, {'url': 'https://www.kennesaw.edu/privacy.php', 'canonical_link': 'https://www.kennesaw.edu/privacy-statement.php', 'word_count': 2036}]
        5 pairs of duplicates listed above
    B: the 5 pairs are listed above within []
Q3:
    Failures: [('calendar.kennesaw.edu', 25), ('experience.kennesaw.edu', 2)]
    We got a multitude of calendar failures and experience failures, these were mainly 403 errors
    Examples:
    {"ts": "2026-10-15T19:45:27.353289+00:00", "event": "error", "url": "https://experience.kennesaw.edu/virtualtour", "failure_reason": "Non 200 response", "status": 403, 
    {"ts": "2026-10-15T21:11:56.678880+00:00", "event": "error", "url": "https://experience.kennesaw.edu/ksu-momentum?source=share-ksu", "failure_reason": "Non 200 response", "status": 403, "time_stamp": "2026-10-15T21:11:56.678880+00:00"}
    {"ts": "2026-10-15T21:18:31.363913+00:00", "event": "error", "url": "https://calendar.kennesaw.edu/calendar?event_types%5B%5D=32061222225277", "failure_reason": "Non 200 response", "status": 403, "time_stamp": "2026-10-15T21:18:31.363914+00:00"}
    {"ts": "2026-10-15T21:18:42.790021+00:00", "event": "error", "url": "https://calendar.kennesaw.edu/calendar?event_types%5B%5D=32822056252319", "failure_reason": "Non 200 response", "status": 403, "time_stamp": "2026-10-15T21:18:42.790022+00:00"}
Q4: Outgoing: [(291, 'https://digitalcommons.kennesaw.edu/communities.html'), (191, 'https://www.kennesaw.edu/degrees-programs/minors/index.php'), (167, 'https://catalog.kennesaw.edu/index.php?catoid=92'), (160, 'https://catalog.kennesaw.edu/misc/catalog_list.php?catoid=84'), (145, 'https://bookstore.kennesaw.edu/mens-apparel/sports/football')]
    Incoming:[('https://www.kennesaw.edu/', 356), ('https://www.kennesaw.edu/visit.php', 346), ('https://www.kennesaw.edu/feedback.php', 346), ('https://www.kennesaw.edu/apply.php', 346), ('https://www.kennesaw.edu/research.php', 346), ('https://www.kennesaw.edu/give.php', 346), ('https://www.kennesaw.edu/accreditation.php', 346), ('https://www.kennesaw.edu/about', 346)]
    For top incoming we see a tie with 346 being present for seven separate sites.
Q5:
    Mean words before removal: 668.606
    Mean words after removal: 435.744
    Mean words removed: 232.862
    Mean Percent Removed:  36.96
Q6:
    A:  Top 30 before stopword removal: [('of', 8918), ('the', 8168), ('and', 5991), ('to', 5895), ('campus', 5802), ('college', 4759), ('university', 4740), ('kennesaw', 4137), ('a', 3938), ('ksu', 3772), ('in', 3206), ('information', 2708), ('for', 2539), ('research', 2528), ('student', 2419), ('state', 2220), ('admissions', 2064), ('programs', 1861), ('academic', 1826), ('education', 1802), ('calendar', 1764), ('students', 1741), ('engineering', 1693), ('business', 1596), ('your', 1564), ('you', 1556), ('by', 1524), ('s', 1499), ('resources', 1481), ('life', 1475)]
        Top 30 after stopword removal: [('campus', 5802), ('college', 4759), ('university', 4740), ('kennesaw', 4137), ('ksu', 3772), ('information', 2708), ('research', 2528), ('student', 2419), ('state', 2220), ('admissions', 2064), ('programs', 1861), ('academic', 1826), ('education', 1802), ('calendar', 1764), ('students', 1741), ('engineering', 1693), ('business', 1596), ('resources', 1481), ('life', 1475), ('graduate', 1438), ('marietta', 1399), ('catalog', 1317), ('visit', 1316), ('services', 1300), ('community', 1283), ('apply', 1262), ('news', 1201), ('undergraduate', 1171), ('alumni', 1165), ('technology', 1112)]
        
        The diffence we see is a swap away from common english words (of,the,and) to words that are very focused towards
        this university, campus, college, and Kennesaw showing up frequently.

    B: Metric	        Before stopword removal	After stopword removal
        Zipf exponent	1.5622	                  1.5068
        R^2	            0.9723	                  0.9702
        The Zipf exponent is close to the classic Zipf exponent of 1, but is not exactly 1.
         Measured R2 shows how the fitted linear model explains variation in log-frequency 
        Produced values of 0.9723 and 0.9702 indicate strong linear fits and shows a strong linear relationship
        After removing stopwords the exponent becomes even more consistent but the linear relationship does not change much
        The residual is approximately -2.159, meaning we see a log-frequency about 2.159 below fitted value, telling us the words depart from the model.
         The top 10 are all negative, but that doesn't mean every word deviates negatively; these are simply the ten largest deviations by absolute magnitude.
Q8:

A:  Host: www.kennesaw.edu  fetches: 301  Smallest gap: 1.000 Floor: 1.0  Under floor: 0
    Host: catalog.kennesaw.edu  fetches: 57  Smallest gap: 120.001 Floor: 120  Under floor: 0
    Host: digitalcommons.kennesaw.edu  fetches: 9  Smallest gap: 1.002 Floor: 1.0  Under floor: 0
    Host: calendar.kennesaw.edu  fetches: 11  Smallest gap: 1.001 Floor: 1.0  Under floor: 0
    Host: bookstore.kennesaw.edu  fetches: 117  Smallest gap: 10.000 Floor: 10.0  Under floor: 0

    We see 0 gaps below any floor, and 5 hosts for example

B:  [(('campus.kennesaw.edu', 'unavailable'), 130), (('calendar.kennesaw.edu', 'disallowed'), 11), (('programfinder.kennesaw.edu', 'disallowed'), 4), (('digitalcommons.kennesaw.edu', 'disallowed'), 4), (('maps.kennesaw.edu', 'unavailable'), 3), (('azindex.kennesaw.edu', 'unavailable'), 2), (('catalog.kennesaw.edu', 'disallowed'), 2), (('financialaid.kennesaw.edu', 'unavailable'), 2), (('styleguide.kennesaw.edu', 'unavailable'), 2), (('bes-owlexpress.kennesaw.edu', 'unavailable'), 1), (('opensource.kennesaw.edu', 'unavailable'), 1), (('stratcomm.kennesaw.edu', 'unavailable'), 1), (('mysportsrec.kennesaw.edu', 'disallowed'), 1), (('legal.kennesaw.edu', 'unavailable'), 1)]
    
    calendar has a large amount of dissallows we follow :
    User-agent: *
    Crawl-Delay: 1
    Disallow: /calendar/*?*types*
    Disallow: /*/calendar/*?*types*
    Disallow: /*/browse*?*types*
    Disallow: /*/calendar/200*
    # Disallow: /*/calendar/2013*
    # Disallow: /*/calendar/2014*
    Disallow: /*/calendar/2015*
    Disallow: /*/calendar/2016*
    Disallow: /*/calendar/2017*
    Disallow: /*/calendar/2018*
    Disallow: /*/calendar/2019*
    Disallow: /*/calendar/202*
    Disallow: /*/calendar/week
    # /*/calendar/month is intentionally skipped
    Disallow: /*/calendar/three_months
    Disallow: /*/calendar/six_months
    Disallow: /*/calendar/year
    Disallow: /calendar/week
    Disallow: /calendar/month
    Disallow: /calendar/three_months
    Disallow: /calendar/six_months
    Disallow: /calendar/year
    Disallow: /event/confirm
    Disallow: /event/*/confirm
    Disallow: /event/unconfirm
    Disallow: /event/*/unconfirm
    Disallow: /event/get_attendees
    Disallow: /event/*/get_attendees
    Disallow: /event/watch_event
    Disallow: /event/*/watch_event
    Disallow: /event/create
    Disallow: /search
    Disallow: /photo/
    Disallow: /*/search
    Disallow: /signup?*
    Disallow: /auth/

    program finder has a similair list of disallows we follow:
    User-agent: *
    Disallow: /search/
    Disallow: /s/
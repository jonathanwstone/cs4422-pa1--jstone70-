Q1:
A:  [('/index.php?catoid', (30, 30)), ('/content.php?catoid&navoid', (23, 0)), ('/', (7, 7)), ('/apply.php', (1, 1)), ('/visit.php', (1, 1)), ('/give.php', (1, 1)), ('/calendar.php', (1, 1)), ('/president/cabinet.php', (1, 1)), ('/admissions/undergraduate/admission-requirements/transfer.php', (1, 1))]
    index.php?catoid makes up about 6%
    content.php makes up about 4.6%

B:  URL Patterns and Crawl Budget

The crawler collected 500 pages, and some URL patterns accounted for a noticeable portion of the crawl budget.

1. URL pattern: /index.php?catoid=...
     this appears 30 times representing 6% of my budget, and produced (based on the hashes) 30 seperate pages different from one another,
    when investigated it showed different pages including images, or handbooks for students and faculty. These are all seperate pages
   2. URL pattern: /content.php?catoid=...&navoid=...
       This pattern appeared in 23 URLs, representing approximately 4.6% of the crawl budget. The recorded pages had empty extracted text and identical content hashes. When manually checking one of these pages in a browser, I found a placeholder message stating, "Important info here soon."

       This discrepancy suggests that the crawler did not capture the same visible content as the browser. The exact cause has not yet been confirmed,
       so these pages should be considered empty or unusable responses rather than definitively classified as duplicate pages.

       Together, these two patterns accounted for 53 of the 500 crawled pages, or approximately 10.6% of the crawl budget.
   C:  I would continue crawling catalog URLs when they produce distinct, useful content. However, I would investigate repeated empty responses
   and avoid spending additional crawl budget on URLs that consistently return no usable content. Before excluding an entire URL pattern,
   I would test URLs and inspect their raw HTTP responses to determine whether the issue comes from the server,
   JavaScript rendering, or the crawler's extraction logic.
   This approach preserves potentially useful catalog pages while reducing wasted requests and improving the quality of the collected dataset.
   When investigated manually we saw that our 2nd most crawled were mostly blank placeholders, so i would attempt to exempt those in the future
   **Manual parameter testing:** I tested five unusual `catoid` values: alphabetic text (`abc`), zero (`0`), a negative value (`-1`), a very large value (`999999`),
   and an empty value. All five returned without redirects and displayed the same 2026–2027 graduate catalog page. Their content hashes also matched, indicating that the responses were identical. 
   This suggests that invalid or missing catalog identifiers may cause the server to return a default catalog page instead of an error. 
   These results demonstrate that different parameter values do not necessarily produce different content, and that a crawler may encounter
   multiple URLs that lead to the same page. A possible improvement would be to detect identical response hashes and avoid repeatedly processing duplicate content.
Q2:
       A: [{'url': 'https://catalog.kennesaw.edu/', 'canonical_link': None, 'word_count': 820}, {'url': 'https://catalog.kennesaw.edu/index.php?catoid=84', 'canonical_link': None, 'word_count': 820}, {'url': 'https://catalog.kennesaw.edu/index.php', 'canonical_link': None, 'word_count': 820}, {'url': 'https://www.kennesaw.edu/', 'canonical_link': 'https://www.kennesaw.edu/index.php', 'word_count': 782}, {'url': 'https://www.kennesaw.edu/directories.php', 'canonical_link': 'https://www.kennesaw.edu/index.php', 'word_count': 782}, {'url': 'https://www.kennesaw.edu/request-info.php', 'canonical_link': 'https://www.kennesaw.edu/request-info.php', 'word_count': 686}, {'url': 'https://www.kennesaw.edu/request-info.php?major=Request+Info+&url=https%3A%2F%2Fwww.kennesaw.edu%2Frequest-info.php', 'canonical_link': 'https://www.kennesaw.edu/request-info.php', 'word_count': 686}, {'url': 'https://www.kennesaw.edu/admissions/undergraduate/admission-requirements/freshman.php', 'canonical_link': 'https://www.kennesaw.edu/admissions/undergraduate/admission-requirements/freshman.php', 'word_count': 2215}, {'url': 'https://admissions.kennesaw.edu/admissions-requirements/freshmen.php', 'canonical_link': 'https://www.kennesaw.edu/admissions/undergraduate/admission-requirements/freshman.php', 'word_count': 2215}, {'url': 'https://www.kennesaw.edu/privacy-statement.php', 'canonical_link': 'https://www.kennesaw.edu/privacy-statement.php', 'word_count': 2036}, {'url': 'https://www.kennesaw.edu/privacy.php', 'canonical_link': 'https://www.kennesaw.edu/privacy-statement.php', 'word_count': 2036}]
           Out of the 500 pages fetched, I found 5 groups of pages with identical normalized extracted text. These groups
   contained 6 excess duplicate pages, which is 1.2% of the total pages fetched.
My crawler calculates a SHA-256 hash after converting the extracted text to lowercase and normalizing whitespace. This 
means it detects pages with identical normalized text, but it does not necessarily mean the raw HTML files are byte-identical.
I also found 6 pages that declared a different canonical URL. These links indicate that the websites consider another URL 
to be the preferred version. I tested near-duplicate content using Jaccard similarity with three-word shingles. The homepage 
and directories page had a similarity score of 1.0, meaning their sets of three-word shingles were identical.

These results measure different types of duplication, and I have not combined them into one percentage because the categories
can overlap. The 1.2% figure only measures excess copies with identical normalized extracted text.
       B: the 5 pairs are listed above within []
Identical normalized text

https://catalog.kennesaw.edu/

https://catalog.kennesaw.edu/index.php?catoid=84

https://catalog.kennesaw.edu/index.php

All three pages had 820 words and the same SHA-256 hash. This means their normalized extracted text was identical.
2. Near-duplicate content

https://www.kennesaw.edu/

https://www.kennesaw.edu/directories.php

These pages had a Jaccard similarity score of 1.0 using three-word shingles. This means both pages had identical sets of 
three-word sequences. Both also declared https://www.kennesaw.edu/index.php as their canonical URL. This suggests that 
the pages share the same extracted text or content   
3. Self-declared canonical duplicate

https://www.kennesaw.edu/request-info.php?major=Request+Info+&url=https%3A%2F%2Fwww.kennesaw.edu%2Frequest-info.php

https://www.kennesaw.edu/request-info.php

The version with query parameters declared the version without the query parameters as its canonical URL. Both pages had 
686 words. This suggests that the query parameters do not change the extracted conten
Overall, my crawl found several cases where multiple URLs represented the same or similar content. This shows why a crawler
needs to analyze both content hashes and canonical links instead of treating every unique URL as a unique page.
Q3:
        The most common failure was redirect loops, with 107 occurrences. The second most common failure was HTTP 403 errors,
with 27 occurrences, followed by HTTP 404 errors, with 12 occurrences. Non-HTML responses accounted for 3 failures, and timeouts accounted for 2 failures.

Redirect loop detected: 107 occurrences. The crawler detected a redirect loop and stopped following the URL.

HTTP 403 Forbidden: 27 occurrences. The server denied the crawler access to the requested page.

HTTP 404 Not Found: 12 occurrences. The requested page could not be found.

Non-HTML response: 3 occurrences. The server returned HTTP 200, but the response was not HTML, so the crawler skipped it.

Timeout: 2 occurrences. The request timed out before the crawler could retrieve the page.
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
       Mean word counts:
- Mean words per page before removal: 668.606
- Mean words per page after removal: 435.744
- Mean words removed per page: 232.862
- Mean percentage removed: 36.96%
Top 5 longest pages before removal:
1. https://www.kennesaw.edu/visit/campus-tours/index.php — 16,706 words
2. https://www.kennesaw.edu/admissions/undergraduate/next-steps/index.php — 3,819 words
3. https://www.kennesaw.edu/admissions/undergraduate/admission-requirements/freshman.php — 2,215 words
4. https://admissions.kennesaw.edu/admissions-requirements/freshmen.php — 2,215 words
5. https://www.kennesaw.edu/admissions/undergraduate/admission-requirements/international.php — 2,197 words
Top 5 longest pages after removal:
1. https://www.kennesaw.edu/visit/campus-tours/index.php — 16,356 words
2. https://www.kennesaw.edu/admissions/undergraduate/next-steps/index.php — 3,467 words
3. https://bookstore.kennesaw.edu/frequently-asked-questions — 2,139 words
4. https://bookstore.kennesaw.edu/faculty-resources — 1,989 words
5. https://www.kennesaw.edu/admissions/undergraduate/admission-requirements/freshman.php — 1,861 words
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
   Q7: URL:  https://www.kennesaw.edu/news/stories/2025/school-of-nursing-grant-for-opioid-disorder-training.php
       opioid 0.33260965441442375
       URL:  https://www.kennesaw.edu/news/stories/2025/school-of-nursing-grant-for-opioid-disorder-training.php
       grant 0.26133615703990437
       URL:  https://www.kennesaw.edu/news/stories/2025/school-of-nursing-grant-for-opioid-disorder-training.php
       college 0.2275407226787048
       URL:  https://www.kennesaw.edu/news/stories/2025/school-of-nursing-grant-for-opioid-disorder-training.php
       campus 0.19245248584971772
       URL:  https://www.kennesaw.edu/news/stories/2025/school-of-nursing-grant-for-opioid-disorder-training.php
       students 0.17400172910724482
       URL:  https://bookstore.kennesaw.edu/commencement-headquarters
       commencement 0.4150020516043849
       URL:  https://bookstore.kennesaw.edu/commencement-headquarters
       bookstore 0.23714402948821997
       URL:  https://bookstore.kennesaw.edu/commencement-headquarters
       javascript 0.17785802211616497
       URL:  https://bookstore.kennesaw.edu/commencement-headquarters
       graduation 0.17785802211616497
       URL:  https://bookstore.kennesaw.edu/commencement-headquarters
       october 0.14349473235814908
       URL:  https://www.kennesaw.edu/giving/online-giving/coles-college.php
       college 0.5366114631466751
       URL:  https://www.kennesaw.edu/giving/online-giving/coles-college.php
       university 0.25935002202749985
       URL:  https://www.kennesaw.edu/giving/online-giving/coles-college.php
       campus 0.25935002202749985
       URL:  https://www.kennesaw.edu/giving/online-giving/coles-college.php
       business 0.17887048771555836
       URL:  https://www.kennesaw.edu/giving/online-giving/coles-college.php
       ksu 0.1729000146849999
       URL:  https://www.kennesaw.edu/news/news-releases/health-human-services.php
       kennesaw 0.27537170252973536
       URL:  https://www.kennesaw.edu/news/news-releases/health-human-services.php
       read 0.2512601908175487
       URL:  https://www.kennesaw.edu/news/news-releases/health-human-services.php
       college 0.2406445348062302
       URL:  https://www.kennesaw.edu/news/news-releases/health-human-services.php
       state 0.22748097165499878
       URL:  https://www.kennesaw.edu/news/news-releases/health-human-services.php
       university 0.21550828893631463
       URL:  https://www.kennesaw.edu/president/contact-us.php
       president 0.35392233096927395
       URL:  https://www.kennesaw.edu/president/contact-us.php
       college 0.3266975362793298
       URL:  https://www.kennesaw.edu/president/contact-us.php
       office 0.2994727415893857
       URL:  https://www.kennesaw.edu/president/contact-us.php
       campus 0.27631868369652335
       URL:  https://www.kennesaw.edu/president/contact-us.php
       university 0.2072390127723925
       Looking ar our outputs we do see some extremely good results, in the nursing article we see opiod and grant, the main subjects of the article
        even things like president in the contact-us option are good. Where we see bad is in things like read, and javascript, college, campus. ALl
       of these terms can vary from being things like stop words for this particular crawl. The best fix would be to customize our stop word removal
       within analyze I only removed common english stop words, this allows terms like campus to slip through
        which is not necessarily pertinent to the article at hand. And in the case of things like java script removing a term 
       that specifically focuses to scripts or other technical activateable options would be great. In the future best practice would be to build upon what
       I did: I removed common English stopwords using scikit-learn. I could also remove navigation phrases such as “Read more,”
       exclude technical boilerplate, and consider a custom list of frequently occurring university-specific terms. This would help TF-IDF identify keywords that better distinguish each page's subject.
       However, terms such as “college” and “campus” should only be removed if they interfere with the purpose of the analysis,
       since they can still be meaningful in some contexts.
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
C: Our overall request rate was 0.02184 fetched pages per second, and the total wall-clock time was 12,500.4 seconds, or about 3 hours and 28 minutes.
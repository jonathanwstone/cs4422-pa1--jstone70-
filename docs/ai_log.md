AI Usage Log

Per assignment §0: this log tracks how an AI assistant (Claude) was used, what it generated vs. what I wrote, and how I verified correctness. Entries are added same-day, not reconstructed later.

Format per entry: date, what I asked, what the assistant did, how I used it, how I verified it.

2026-09-15 — Initial project scoping

What I asked: How to approach building a from-scratch web crawler for the assignment; advisor-only constraint (no base code from the assistant). What the assistant did: Explained general crawler architecture at a conceptual level (fetch → parse → extract → enqueue loop), recommended library choices already permitted by the assignment (requests, beautifulsoup4, lxml, protego), no code written. How I used it: Used it to plan project structure and confirm my tool choices were in-bounds under Req 6. Verification: Cross-checked the assignment gist directly; confirmed the libraries mentioned are explicitly allowed.

2026-09-15 — Canonicalization & frontier design decisions

What I asked: Trade-offs for trailing-slash policy, query-parameter policy, and frontier data structure (Req 9 requires stating and justifying these). What the assistant did: Explained the RFC 3986 §6.2.3 trade-offs for trailing slashes, recommended a tracking-param blocklist approach for query strings, and recommended starting with a simple deque + seen-set frontier (matching the assignment's own §6 guidance) rather than per-host queues prematurely. No code written. How I used it: Adopted "strip trailing slash by default, verify via content_hash comparison on a probe sample" as my policy; adopted the tracking-param blocklist approach; adopted deque + seen-set as my starting frontier. Verification: Design discussion — policies will be verified empirically once I have real crawl data (comparing content_hash values for trailing-slash pairs, per the plan discussed).

2026-09-15 — Module structure walkthrough

What I asked: What the basic structure of a crawler looks like and how to break it into files/functions. What the assistant did: Described the responsibilities of each conceptual piece (CLI/argparse entry point, frontier, per-host delay tracker, robots cache, main loop, canonicalization function, output writers) and a suggested incremental build order. No code written — I wrote all functions myself. How I used it: Used it as a planning checklist for crawler.py. Verification: N/A (design discussion, not code).

2026-09-15 — Debugging pip install error

What I asked: Why pip install BeautifulSoup failed with a wheel-build error. What the assistant did: Identified that BeautifulSoup (no version number) is the abandoned v3 package on PyPI, and that the correct current package is beautifulsoup4 (imported as bs4). How I used it: Changed my install command / requirements.txt entry to beautifulsoup4. Verification: Ran import bs4; print(bs4.__version__) in a REPL after reinstalling — imported cleanly with a version printed, confirming the fix.

2026-09-15 — Understanding requests.Response and BeautifulSoup APIs

What I asked: What the various requests.get() response attributes (.status_code, .headers, .content, etc.) and BeautifulSoup methods (find_all, get_text, etc.) actually do. What the assistant did: Explained each attribute/method conceptually and what it would be used for in the crawler (e.g. .headers for Content-Type checks, .content for byte-size caps). No code written. How I used it: Used the explanations to interpret real output from my own requests.get("https://www.kennesaw.edu/") call and my own BeautifulSoup parsing of it. Verification: Ran the calls myself against the real KSU homepage and inspected the actual returned status code, title, and link tags directly.

2026-09-15 — Link-filtering logic discussion

What I asked: How to think about filtering <a> tags extracted from a real KSU page (fragment links, mailto:, tel:, javascript:, missing href, subdomain scoping). What the assistant did: Reviewed real link output I pasted, identified the categories of non-page links present (fragments, JS-driven buttons, duplicate links within a page) and the subdomain-matching requirement for Req 3. Did not write the filter function — I'm writing it myself. How I used it: Informing the filter logic I'm about to write. Verification: Pending — will test the filter against the real link sample once written.

2026-09-16 — Frontier design: queue vs. recursive tree

What I asked: Whether the frontier should be built as a recursive tree-copy structure. What the assistant did: Explained why a recursive/tree approach is wrong for this use case (depth-first behavior, Python recursion limits, the web being a graph not a tree) and described the correct shape: a flat deque (FIFO queue) plus a flat set (seen-URLs), tied together by one while loop with a nested for loop. No code written. How I used it: Redesigned my mental model before writing crawler(). Verification: N/A (design discussion, not code).

2026-09-16 — Frontier loop review, multiple passes

What I asked: Reviewed several drafts of my crawler()/frontier() function as I iterated on it. What the assistant did: Code review only — identified specific bugs across several iterations: using .pop() (LIFO) instead of .popleft() (FIFO) for breadth-first order; a seen list instead of a set (O(n) vs O(1) lookup); checking membership against the raw href instead of the canonicalized URL; an rOrL toggle that alternated pop ends instead of always using popleft(); iterating over toScan instead of soup.find_all('a') for link extraction; missing None-checks on link.get('href'); no urljoin for relative hrefs; no junk-prefix filtering (#, mailto:, tel:, javascript:); no in-domain check. The assistant explained why each was a bug and what the fix should accomplish, but did not write the corrected code — I rewrote each piece myself and re-submitted for review. How I used it: Iteratively fixed my own crawler() function across several rounds based on this feedback. Verification: Traced through the logic by hand for each bug (e.g. confirmed .pop() vs .popleft() behavior against Python's deque docs); re-tested by rerunning and inspecting printed seen output after each fix.

2026-09-16 — Clarified: lxml does not canonicalize URLs

What I asked: I had assumed canonicalize() could be imported from lxml. What the assistant did: Corrected the misunderstanding — lxml's canonicalize is XML C14N (a document-signing concept), unrelated to URL normalization. Confirmed no library does Req 8/9 URL canonicalization for me and that I need to write it myself using urllib.parse. How I used it: Stopped trying to import a canonicalize function and started planning to write my own. Verification: N/A (factual correction, self-verified against lxml docs showing canonicalize is under lxml.etree and documented as XML C14N).

2026-09-16 — Canonicalization function: requirements and approach

What I asked: How to build my own canonicalize() function per Req 8/9. What the assistant did: Re-fetched the assignment text to confirm the exact Req 8 minimum requirements (lowercase scheme/host, remove default ports, remove fragments, normalize percent-encoding, resolve ./.. path segments), and laid out which urllib.parse functions map to each step (urlsplit, parse_qsl, urlencode, urlunsplit, posixpath.normpath for path resolution). Suggested test cases to verify by hand. No code written — I'm writing and testing the function myself. How I used it: Using this as my implementation checklist for canonicalize(). Verification: Pending — will hand-test against the example URLs suggested (mixed-case scheme/host, default port, trailing slash, tracking params, .. path segments, fragment) once written.

2026-09-17 — Building makeCanon(): scheme/netloc/fragment

What I asked: How to start writing my own URL canonicalization function using urllib.parse, since no library does this for me. What the assistant did: Explained urlsplit's immutable-tuple return type and the general reassemble-with-urlunsplit pattern; reviewed my drafts and caught bugs: split.scheme = ... attempting to mutate an immutable named tuple; a missing () on split.query.lower; blindly lowercasing path (case-sensitive on real servers, not part of Req 8) and fragment (should be dropped, not case-normalized); fragment = ' ' (a space) instead of '' (empty string). No code written — I wrote and fixed each version myself. How I used it: Iteratively corrected my own makeCanon() draft. Verification: Ran each version and inspected the printed tuple output by eye against hand-picked test URLs (mixed-case scheme/host, a real KSU link).

2026-09-17 — Default port stripping

What I asked: How to strip default ports (:80/:443) from netloc. What the assistant did: Explained the http→80 / https→443 default-port mapping; reviewed drafts and caught two logic bugs: unconditionally stripping any port regardless of value (would incorrectly strip non-default ports like :8443), and an or operator-precedence bug (splitNetloc[1] == "80" or "443" evaluates as (splitNetloc[1] == "80") or "443", which is always truthy since a non-empty string is truthy) that caused the port check to always fire. No code written — I rewrote the conditional myself. How I used it: Fixed the port-stripping conditional in makeCanon(). Verification: Tested against four hand-picked cases (:443 on https, :80 on http, :8443 non-default, and no port at all) and confirmed only the two default-port cases were stripped.

2026-09-20 — Percent-encoding normalization

What I asked: How to normalize percent-encoding in the path per Req 8. What the assistant did: Explained the two real-world problems this addresses (inconsistent hex casing, e.g. %2f vs %2F; unnecessarily encoded unreserved characters, e.g. %7E vs ~) and recommended quote(unquote(path), safe="/-._~") from urllib.parse. No code written. How I used it: Added this line to makeCanon(). Verification: Tested against crawler-test.com URLs including one with %7e/%2f sequences; confirmed unreserved chars decoded and reserved separators stayed encoded.

2026-09-20 — Path ./.. resolution and trailing slash

What I asked: How to resolve ./.. segments and handle trailing slashes in the path. What the assistant did: Explained what ./.. mean in a path (same semantics as cd . / cd ..) and why unresolved forms would cause duplicate crawls of the same resource; recommended posixpath.normpath() (specifically posixpath over os.path, since os.path's behavior depends on the host OS) and had me test it standalone first on /a/b/../c, /about/, and "" before trusting it. Identified from my test output that normpath("") returns ".", an artifact that needed a manual correction (if path == '.': path = '/') since it doesn't correspond to a real path. Confirmed from further tests that normpath already strips trailing slashes on non-root paths and preserves / for the bare root, so no separate trailing-slash logic was needed beyond the "." fix. No code written — I wrote and ran all tests myself. How I used it: Added path normalization + the .→/ correction to makeCanon(). Verification: Ran posixpath.normpath() standalone against three test cases before integrating; then ran the full makeCanon() against a bare domain, a trailing-slash URL, and a combined dot-segment+trailing-slash URL, confirming all three produced the expected canonical form.

2026-09-23 — Query parameter filtering and sorting

What I asked: How a tracking-parameter blocklist works, and how to implement filter/sort/re-encode logic for query strings. What the assistant did: Explained that a blocklist filters specific parameter keys within a URL's query string (not entire URLs) and why mismatched tracking params (e.g. utm_source=facebook vs. utm_source=twitter on an otherwise identical URL) would otherwise cause duplicate crawls of the same page. Reviewed my draft and caught a bug: comparing whole tuples from parse_qsl() against a list of plain blocklist strings, which can never match (needed item[0], the key, not the whole tuple). Recommended sorting survivors by key before urlencode() for order-independence. No code written. How I used it: Fixed the filter condition and (pending) added the sort call in makeCanon(). Verification: Tested the filter against a real query string with two tracking params, confirmed only the non-blocklisted param survived; sort behavior still pending a scrambled-order test.

2026-09-23 — Wiring makeCanon() into crawler()

What I asked: Reviewed my full crawler() function with makeCanon() now wired in via urljoin(url, toCanon). What the assistant did: Code review — flagged that toCanon can be None (tags with no href) and would crash urljoin before reaching the existing None-check, which happens too late; flagged missing filtering for junk hrefs (#..., mailto:, tel:, javascript:); flagged missing in-domain checking; flagged two unused/leftover imports (from urllib import response, from lxml.etree import canonicalize, the latter a leftover from an earlier mix-up). No code written — fixes pending on my end. How I used it: Identifying the next round of fixes needed in crawler(). Verification: Pending — will re-test once None-check ordering, prefix filtering, and domain checking are added.

2026-09-25 — robots.txt design: per-host caching concept

What I asked: How robots.txt checking should work, and whether one robots.txt covers the whole kennesaw.edu domain. What the assistant did: Corrected a misunderstanding — each subdomain (www., campus., catalog., etc.) has its own separate robots.txt, not one shared file for the whole domain. Explained the three response-code handling cases (2xx parse normally, 4xx-not-429 treat as unrestricted, 5xx/network-failure treat as fully disallowed) and recommended a per-host dict cache keyed by netloc. No code written. How I used it: Designed checkRobots()'s caching structure and response-handling logic around this. Verification: N/A (design/conceptual discussion).

2026-09-25 — Building checkRobots(): multiple debugging rounds

What I asked: Reviewed several drafts of my checkRobots() function. What the assistant did: Code review across multiple iterations — caught: creating the cache dict inside the function (defeating caching entirely, since it reset on every call); calling .append() on a string (netloc) and later on a dict (robotsCache), neither of which have that method; checking request.text (response body) instead of request.status_code for status branching; a not '429' condition that was always False since non-empty strings are truthy in Python; off-by-one errors in all three numeric range checks (< vs <= at boundaries) that excluded the boundary status codes themselves (404, 500, 200); a range that accidentally included 3xx redirects in the "success" branch; a missing return statement; and a missing try/except around the robots.txt fetch itself for genuine network failures. Explained each bug conceptually; I rewrote the function myself across each round. How I used it: Iteratively corrected checkRobots() until it worked end-to-end. Verification: Tested against a real fetch of kennesaw.edu's robots.txt, confirmed a real Protego object was returned (not a crash or None); tested .can_fetch() on the result and confirmed it returned True for a real page; confirmed conceptually (not yet re-verified with a second call) that the cache should prevent redundant re-fetches on the same host.

2026-09-25 — Timeout value discussion

What I asked: Whether 15 seconds was an appropriate requests timeout. What the assistant did: Explained the trade-off (too long stalls the whole crawl on dead hosts; too short risks killing legitimately slow real pages) and suggested 5-10 seconds as a common convention, recommending I start around 10 and adjust based on real timeout data from crawl.log later. How I used it: Set timeout to 10 seconds. Verification: N/A (design decision); will revisit if real-run logs show unnecessary timeouts on legitimate pages.

2026-09-25 — Wiring checkRobots() into crawler()

What I asked: Where the robots-check and its skip condition belong relative to the rest of the loop (I initially thought it belonged near the canon not in seen check). What the assistant did: Clarified that the robots check belongs in the outer loop (checking "can I fetch this URL right now") and is unrelated to the canon not in seen check in the inner loop (checking "should this newly-found link be added to the frontier") — different questions at different points in the loop. Also clarified that URLs popped from toScan are already canonical (canonicalized before being enqueued), so no re-canonicalization was needed before extracting host/scheme for the robots check. No code written — I wrote and placed the block myself. How I used it: Placed the robots-check block correctly, right after toScan.popleft() and before requests.get(). Verification: Ran the full loop; no crashes. Flagged by the assistant as not yet confirmed to actually exercise the "deny" branch, since KSU likely allows most of the site — still pending a deliberate test against a disallowed path.

2026-09-25 — User-Agent string (Req 10)

What I asked: What to use for the USER_AGENT argument to can_fetch(). What the assistant did: Explained Req 10's intent (an honest, traceable identity, not a spoofed browser string) and the conventional format (Name/Version (contact)). Flagged that my requests.get() call for fetching real pages wasn't sending any custom User-Agent header at all, even though checkRobots()'s check used one — meaning I was checking robots rules for one identity but fetching under a different (default Python) identity. No code written. How I used it: Defined a consistent User-Agent string/constant and added it as a header to both the robots.txt fetch and the main page fetch. Verification: N/A (Req 10 compliance decision); header presence confirmed by inspection of the request call.

2026-09-25 — Error handling (Req 13): try/except and response checks

What I asked: How to structure try/except for requests.get(), since I hadn't used it in a while; whether one general except was sufficient. What the assistant did: Reviewed the difference between exception-raising failures (timeout, connection error — need try/except) and non-exception bad responses (bad status code, wrong content-type, oversized body — need plain if checks after a successful request). Explained that except blocks are checked in order and a more specific exception (Timeout) must be listed before a more general one (RequestException) or it will never be reached. Reviewed my draft and confirmed the status-code and content-type guard clauses were structured correctly. No code written — I wrote the try/except and both if checks myself. How I used it: Added a two-tier except block (Timeout, then RequestException) and status-code/content-type guard clauses after the request. Verification: Structural review only so far; real network testing of each branch still pending.

2026-09-25 — Oversized-response cap

What I asked: Whether I actually needed a size cap, since I wanted to read full pages regardless of size; pushed back on an initial 5MB suggestion and proposed 1MB. What the assistant did: Explained the cap exists to guard against pathological responses (mis-configured infinite streams, mislabeled large files), not to limit normal page content, and that it should essentially never trigger on real pages if sized generously. Walked through why a real KSU page could plausibly exceed 1MB (inline styles/scripts, embedded SVGs, long server-rendered listings) using earlier observed markup volume as evidence, and suggested checking real response sizes from actual KSU pages before finalizing a number, recommending 2-5MB as a safer range in the meantime. No code written — final number still undecided as of this entry. How I used it: Reconsidering the cap value; considering an empirical check (printing len(page.content) across real fetched pages) before finalizing. Verification: Pending — plan is to base the final number on real observed page sizes from KSU rather than a guess

2026-09-30 — Per-host delay design (Req 11)

What I asked: Whether the per-host delay comes from robots.txt. What the assistant did: Clarified that Req 11's 1-second floor is my own requirement independent of robots.txt, while Crawl-delay (if a site declares one, via protego's .crawl_delay()) should be honored on top of that floor when it's longer. Recommended a lastFetchTime dict keyed by host, storing timestamps, with a helper function to check/sleep/update. No code written. How I used it: Designed enforceDelay()'s signature and the "mark-before-fetch vs. mark-after-fetch" decision — I proposed and the assistant agreed that marking the timestamp before the fetch (rather than after) is more correctly conservative, since it prevents a slow response from effectively shortening the enforced gap. Verification: N/A (design discussion).

2026-09-30 — Building and debugging enforceDelay()

What I asked: Reviewed my draft implementation. What the assistant did: Caught lastFetchTime.append(...) (dict has no .append(), needed lastFetchTime[host] = ...) and a logic gap where the timestamp update only ran inside the nested "needed to sleep" branch instead of unconditionally — meaning a host that didn't need sleeping never got its timestamp refreshed. No code written — I rewrote the function myself across two rounds. How I used it: Fixed both bugs in enforceDelay(). Verification: Reasoned through the corrected logic by hand; standalone timing test (two calls on the same fake host) still pending as of this entry.

2026-09-30 — Wiring delay into checkRobots() and crawler()

What I asked: Where exactly to call enforceDelay() — I initially thought it should apply only via the robots-check, and separately asked about netloc.host (which doesn't exist; netloc is already the host). What the assistant did: Explained that the robots.txt fetch itself is also an HTTP request to the host and should be delay-gated too (using the 1-second floor, since the site's own preferred delay isn't known until after parsing), requiring two separate call sites: inside checkRobots() before its robots.txt fetch, and inside crawler()'s main loop before the real page fetch (this one using max(defaultDelay, robotsResult.crawl_delay(...))). Caught an ordering bug in my draft — enforceDelay() was being called before the robotsCache hit-check, causing unnecessary sleeps even on cache hits — and a missing call in crawler() where I computed requiredDelay but never passed it to enforceDelay(). Also caught that the seed URL (starting) was being canonicalized but the result discarded, with the raw string still being added to toScan/seen. No code written. How I used it: Fixed the cache-check ordering in checkRobots(); added the missing enforceDelay() call in crawler(); fixed the seed URL to use its canonicalized form. Verification: Ran the full crawler end-to-end with both fixes in place, no crashes. Detailed per-host timing verification (confirming actual pauses occur between same-host requests) still pending a dedicated test run.

2026-09-30 — Re-confirmed pages.jsonl schema and remaining requirements

What I asked: What pages.jsonl is for, and asked the assistant to re-fetch the assignment to confirm the exact schema before building the writer. What the assistant did: Explained the JSONL format (one independent JSON object per line, vs. a single array) and why it's used — append-as-you-go durability against crashes, and easy line-by-line reading during analysis. Re-fetched the assignment gist and confirmed the exact required fields (url_canonical, status, fetched_at, title, text, word_count, out_links, content_hash, canonical_link). Flagged two gaps in my current code not yet addressed: Req 11's "at most one request in flight per host" and the per-host-queue optimization tip (my flat deque is correct but not optimally interleaved across hosts), and Req 13's redirect-handling requirement (allow_redirects=False, manual following, capped/loop-detected), which hasn't been implemented at all yet. No code written. How I used it: Confirming exact field names/types before implementing the pages.jsonl writer. Verification: N/A (requirements re-confirmation from source document).

## 2026-09-30 — Redirect handling design (Req 13)
**What I asked:** Whether the assignment specifies an exact redirect hop
limit, and how to structure a manual redirect-follower since `requests`'
default auto-follow isn't allowed.
**What the assistant did:** Clarified the assignment leaves the exact cap to
my judgment (only requiring "capped in length, with loop detection"),
recommended 5 as a reasonable, justifiable default. Laid out the
`redirectHandler()` design: a local `visited` list for loop detection
(distinct from the global `seen` set), a hop counter, and `allow_redirects=False`
with manual `Location`-header following via `urljoin`. No code written.
**How I used it:** Designed and wrote `redirectHandler()`'s structure myself.
**Verification:** N/A (design discussion).

## 2026-09-30 — Debugging `redirectHandler()`
**What I asked:** Reviewed several drafts of `redirectHandler()`.
**What the assistant did:** Caught a redundant recursive call left over from
an earlier draft that both duplicated the `while` loop's job and discarded
its own return value; `urllib.urljoin` instead of `urllib.parse.urljoin`
(would crash); and a bare `return` in the success branch that returned
`None` instead of the actual response object, discarding the one thing the
caller needed. No code written — I rewrote the function across multiple
rounds.
**How I used it:** Iteratively fixed `redirectHandler()` until it correctly
returned a final `Response` on success and `None` on loop/cap failure.
**Verification:** Tested against `http://kennesaw.edu/`, confirmed it
returned `<Response [200]>` with `.url` showing the correct final redirected
destination (`https://www.kennesaw.edu/`).

## 2026-09-30 — Per-hop scope-checking and delay in redirects
**What I asked:** Whether each redirect hop should be scope-checked (not
just the final destination), and how to apply per-host delay inside
`redirectHandler()` given it makes its own independent `requests.get()`
calls.
**What the assistant did:** Recommended checking every hop's host against
the in-domain rule (reusing the same two-condition check already written in
`crawler()`'s inner loop) so an off-domain intermediate hop is never
followed. Identified that `enforceDelay()` was only being called once, by
`crawler()`, before entering `redirectHandler()` — meaning intermediate
hops inside a multi-hop chain could fire rapid, undelayed requests to the
same host, a Req 11 violation. Recommended calling `enforceDelay()` inside
`redirectHandler()`'s own loop, before every fetch, using the 1-second floor
(not each hop's own robots.txt Crawl-delay, as a deliberate, documented
simplification) rather than the more complex alternative of robots-checking
every hop. No code written.
**How I used it:** Added the per-hop domain check and `enforceDelay()` call
inside `redirectHandler()`'s loop.
**Verification:** Fixed two parameter-passing bugs identified during review
(passing `url` instead of `host` to `enforceDelay`; an undefined
`requiredDelay[url]` dict lookup that would have crashed) by hand-tracing
the function's variables; re-ran the `http://kennesaw.edu/` test to confirm
the working case still succeeded after the changes.

## 2026-09-30 — Wiring `redirectHandler()` into `crawler()`
**What I asked:** Reviewed my integration of `redirectHandler()` into the
main loop, replacing the old direct `requests.get()` call.
**What the assistant did:** Caught that I had left the old
`try/except`-wrapped `requests.get()` call in place *alongside* the new
`redirectHandler()` call, causing every URL to be fetched twice (once
wastefully, with the result discarded). Confirmed the fix (deleting the old
block entirely, since `redirectHandler()` already handles timeouts/
exceptions internally) was structurally correct once applied. No code
written.
**How I used it:** Removed the duplicate fetch; confirmed
`page = redirectHandler(url)` plus a `None` check was the complete
replacement.
**Verification:** Reviewed the full updated loop by inspection; confirmed
only one fetch path remained.

## 2026-09-30 — Re-confirmed pages.jsonl schema; designed `buildRecord()`
**What I asked:** How to start building the pages.jsonl output — fields,
and whether it belongs in the same file.
**What the assistant did:** Re-explained the JSONL format and why it's used
over a single JSON array (crash resilience, line-by-line readability).
Confirmed `pages.jsonl` writing belongs in `crawler.py` (stage one of the
assignment's two-stage pipeline), not a new file. Walked through each of the
nine required schema fields and what Python tool/method produces each one,
without writing the code itself, and recommended structuring record-building
as its own function (`buildRecord()`) for testability, separate from
`crawler()`'s main loop — matching the pattern used for every other helper
function so far.
**How I used it:** Designed `buildRecord()`'s signature and overall shape
myself.
**Verification:** N/A (design discussion).

## 2026-09-30 — Building `buildRecord()`: field by field
**What I asked:** Worked through each field's implementation one at a time:
`title`, `word_count`, `fetched_at`, `content_hash`, `canonical_link`.
**What the assistant did:** Conceptual guidance only, no code written —
explained *why* each tool was the right one without supplying the line
itself: why `.string` on `soup.title` needs a `None`-guard; why `time.time()`
was the wrong tool for `fetched_at` (not human-readable/ISO format) versus
`datetime.now(timezone.utc).isoformat()`; why `.count()` doesn't count words
(it counts a specific given substring) versus `len(text.split())`; the
three-step shape for `content_hash` (normalize via lowercase + split/join,
encode to bytes via `.encode('utf-8')`, hash via `hashlib.sha256(...).hexdigest()`);
and the `soup.find('link', rel='canonical')` + `.get('href')` +
`None`-fallback pattern for `canonical_link`, mirroring the `title` pattern.
Caught several bugs in my attempts along the way: a `.spit()` typo; calling
`hashlib.sha256()` directly on a string instead of encoded bytes; storing
the string `'None'` instead of the real `None` value for a missing
canonical link; and calling `soup.find(...)` twice redundantly instead of
storing it once.
**How I used it:** Wrote `buildRecord()` myself, field by field, using the
guidance above.
**Verification:** Reviewed the complete function by inspection, confirmed
all nine schema fields were present and used the correct types; no live
execution test run yet as of this entry.

## 2026-10-02 — Wiring `buildRecord()` into `crawler()`: multiple bugs
**What I asked:** Where exactly to call `buildRecord()` from inside
`crawler()`, and debugged several placement/argument issues as they came up,
including an `UnboundLocalError` on `canon`.
**What the assistant did:** Identified multiple issues across several
rounds: the call was initially placed with wrong arguments (`url` passed
where the `page` response object was expected) and before `soup`/`outLinks`
existed yet; then placed inside the inner per-link `for` loop (would call it
once per link instead of once per page); explained the `UnboundLocalError`
on `canon` by walking through why `canon` is only conditionally assigned
inside the inner loop and may never be assigned at all if a page has no
qualifying links, recommending `url` (the page's own canonical URL,
unconditionally set at the top of the outer loop) be used instead of
`canon` as the third argument. Also identified that `outLinks` had briefly
been made a global variable, which would have caused every page's record to
accumulate links across the entire crawl rather than reflecting just that
page's own links, and explained why it needed to be re-initialized to an
empty list inside the outer loop, once per page. Separately, identified that
the `outLinks.append(canon)` call needed to happen unconditionally for every
valid filtered link — not only inside the `if canon not in seen:` branch —
since `out_links` should reflect a page's actual content, not which links
happened to be "new" to the crawl at the time that page was processed. No
code written throughout.
**How I used it:** Fixed call placement (after the inner loop, at the outer
loop's indentation), fixed the argument list (`page`, `soup`, `url`,
`outLinks`), moved `outLinks` back to a per-page local variable, and moved
the `outLinks.append(canon)` call to before the `seen`-membership check.
**Verification:** Reasoned through the `UnboundLocalError` by hand-tracing
which lines could leave `canon` unassigned; reviewed final indentation and
argument order by inspection against the full pasted function.

## 2026-10-02' — Deduplicating `out_links`
**What I asked:** How to deduplicate `out_links` in the simplest way
possible, per the schema's "canonicalized, deduplicated" requirement.
**What the assistant did:** Recommended `list(set(outLinks))` as the
simplest approach, noting the trade-off (loses original order, which the
schema doesn't require). Caught that my first attempt placed this line
immediately after `outLinks = []` (before the list had anything in it,
making it a no-op) and clarified it needed to run after the inner loop
finished populating the list, immediately before the `buildRecord()` call.
No code written.
**How I used it:** Added `outLinks = list(set(outLinks))` at the correct
point in `crawler()`.
**Verification:** Reviewed final placement by inspection against the full
pasted function; confirmed it sits after the inner loop and before
`buildRecord()` is called.
## 2026-10-03 — Redirect handling design (Req 13)
**What I asked:** Whether the assignment specifies an exact redirect hop
limit, and how to structure a manual redirect-follower since `requests`'
default auto-follow isn't allowed.
**What the assistant did:** Clarified the assignment leaves the exact cap to
my judgment (only requiring "capped in length, with loop detection"),
recommended 5 as a reasonable, justifiable default. Laid out the
`redirectHandler()` design: a local `visited` list for loop detection
(distinct from the global `seen` set), a hop counter, and `allow_redirects=False`
with manual `Location`-header following via `urljoin`. No code written.
**How I used it:** Designed and wrote `redirectHandler()`'s structure myself.
**Verification:** N/A (design discussion).

## 2026-10-03 — Debugging `redirectHandler()`
**What I asked:** Reviewed several drafts of `redirectHandler()`.
**What the assistant did:** Caught a redundant recursive call left over from
an earlier draft that both duplicated the `while` loop's job and discarded
its own return value; `urllib.urljoin` instead of `urllib.parse.urljoin`
(would crash); and a bare `return` in the success branch that returned
`None` instead of the actual response object, discarding the one thing the
caller needed. No code written — I rewrote the function across multiple
rounds.
**How I used it:** Iteratively fixed `redirectHandler()` until it correctly
returned a final `Response` on success and `None` on loop/cap failure.
**Verification:** Tested against `http://kennesaw.edu/`, confirmed it
returned `<Response [200]>` with `.url` showing the correct final redirected
destination (`https://www.kennesaw.edu/`).

## 2026-10-03 — Per-hop scope-checking and delay in redirects
**What I asked:** Whether each redirect hop should be scope-checked (not
just the final destination), and how to apply per-host delay inside
`redirectHandler()` given it makes its own independent `requests.get()`
calls.
**What the assistant did:** Recommended checking every hop's host against
the in-domain rule (reusing the same two-condition check already written in
`crawler()`'s inner loop) so an off-domain intermediate hop is never
followed. Identified that `enforceDelay()` was only being called once, by
`crawler()`, before entering `redirectHandler()` — meaning intermediate
hops inside a multi-hop chain could fire rapid, undelayed requests to the
same host, a Req 11 violation. Recommended calling `enforceDelay()` inside
`redirectHandler()`'s own loop, before every fetch, using the 1-second floor
(not each hop's own robots.txt Crawl-delay, as a deliberate, documented
simplification) rather than the more complex alternative of robots-checking
every hop. No code written.
**How I used it:** Added the per-hop domain check and `enforceDelay()` call
inside `redirectHandler()`'s loop.
**Verification:** Fixed two parameter-passing bugs identified during review
(passing `url` instead of `host` to `enforceDelay`; an undefined
`requiredDelay[url]` dict lookup that would have crashed) by hand-tracing
the function's variables; re-ran the `http://kennesaw.edu/` test to confirm
the working case still succeeded after the changes.

## 2026-10-03 — Wiring `redirectHandler()` into `crawler()`
**What I asked:** Reviewed my integration of `redirectHandler()` into the
main loop, replacing the old direct `requests.get()` call.
**What the assistant did:** Caught that I had left the old
`try/except`-wrapped `requests.get()` call in place *alongside* the new
`redirectHandler()` call, causing every URL to be fetched twice (once
wastefully, with the result discarded). Confirmed the fix (deleting the old
block entirely, since `redirectHandler()` already handles timeouts/
exceptions internally) was structurally correct once applied. No code
written.
**How I used it:** Removed the duplicate fetch; confirmed
`page = redirectHandler(url)` plus a `None` check was the complete
replacement.
**Verification:** Reviewed the full updated loop by inspection; confirmed
only one fetch path remained.

## 2026-10/03 — Re-confirmed pages.jsonl schema; designed `buildRecord()`
**What I asked:** How to start building the pages.jsonl output — fields,
and whether it belongs in the same file.
**What the assistant did:** Re-explained the JSONL format and why it's used
over a single JSON array (crash resilience, line-by-line readability).
Confirmed `pages.jsonl` writing belongs in `crawler.py` (stage one of the
assignment's two-stage pipeline), not a new file. Walked through each of the
nine required schema fields and what Python tool/method produces each one,
without writing the code itself, and recommended structuring record-building
as its own function (`buildRecord()`) for testability, separate from
`crawler()`'s main loop — matching the pattern used for every other helper
function so far.
**How I used it:** Designed `buildRecord()`'s signature and overall shape
myself.
**Verification:** N/A (design discussion).

## 2026-10/03 — Building `buildRecord()`: field by field
**What I asked:** Worked through each field's implementation one at a time:
`title`, `word_count`, `fetched_at`, `content_hash`, `canonical_link`.
**What the assistant did:** Conceptual guidance only, no code written —
explained *why* each tool was the right one without supplying the line
itself: why `.string` on `soup.title` needs a `None`-guard; why `time.time()`
was the wrong tool for `fetched_at` (not human-readable/ISO format) versus
`datetime.now(timezone.utc).isoformat()`; why `.count()` doesn't count words
(it counts a specific given substring) versus `len(text.split())`; the
three-step shape for `content_hash` (normalize via lowercase + split/join,
encode to bytes via `.encode('utf-8')`, hash via `hashlib.sha256(...).hexdigest()`);
and the `soup.find('link', rel='canonical')` + `.get('href')` +
`None`-fallback pattern for `canonical_link`, mirroring the `title` pattern.
Caught several bugs in my attempts along the way: a `.spit()` typo; calling
`hashlib.sha256()` directly on a string instead of encoded bytes; storing
the string `'None'` instead of the real `None` value for a missing
canonical link; and calling `soup.find(...)` twice redundantly instead of
storing it once.
**How I used it:** Wrote `buildRecord()` myself, field by field, using the
guidance above.
**Verification:** Reviewed the complete function by inspection, confirmed
all nine schema fields were present and used the correct types; no live
execution test run yet as of this entry.

## 2026-10-03 — Wiring `buildRecord()` into `crawler()`: multiple bugs
**What I asked:** Where exactly to call `buildRecord()` from inside
`crawler()`, and debugged several placement/argument issues as they came up,
including an `UnboundLocalError` on `canon`.
**What the assistant did:** Identified multiple issues across several
rounds: the call was initially placed with wrong arguments (`url` passed
where the `page` response object was expected) and before `soup`/`outLinks`
existed yet; then placed inside the inner per-link `for` loop (would call it
once per link instead of once per page); explained the `UnboundLocalError`
on `canon` by walking through why `canon` is only conditionally assigned
inside the inner loop and may never be assigned at all if a page has no
qualifying links, recommending `url` (the page's own canonical URL,
unconditionally set at the top of the outer loop) be used instead of
`canon` as the third argument. Also identified that `outLinks` had briefly
been made a global variable, which would have caused every page's record to
accumulate links across the entire crawl rather than reflecting just that
page's own links, and explained why it needed to be re-initialized to an
empty list inside the outer loop, once per page. Separately, identified that
the `outLinks.append(canon)` call needed to happen unconditionally for every
valid filtered link — not only inside the `if canon not in seen:` branch —
since `out_links` should reflect a page's actual content, not which links
happened to be "new" to the crawl at the time that page was processed. No
code written throughout.
**How I used it:** Fixed call placement (after the inner loop, at the outer
loop's indentation), fixed the argument list (`page`, `soup`, `url`,
`outLinks`), moved `outLinks` back to a per-page local variable, and moved
the `outLinks.append(canon)` call to before the `seen`-membership check.
**Verification:** Reasoned through the `UnboundLocalError` by hand-tracing
which lines could leave `canon` unassigned; reviewed final indentation and
argument order by inspection against the full pasted function.

## 2026-10-03 — Deduplicating `out_links`
**What I asked:** How to deduplicate `out_links` in the simplest way
possible, per the schema's "canonicalized, deduplicated" requirement.
**What the assistant did:** Recommended `list(set(outLinks))` as the
simplest approach, noting the trade-off (loses original order, which the
schema doesn't require). Caught that my first attempt placed this line
immediately after `outLinks = []` (before the list had anything in it,
making it a no-op) and clarified it needed to run after the inner loop
finished populating the list, immediately before the `buildRecord()` call.
No code written.
**How I used it:** Added `outLinks = list(set(outLinks))` at the correct
point in `crawler()`.
**Verification:** Reviewed final placement by inspection against the full
pasted function; confirmed it sits after the inner loop and before
`buildRecord()` is called.

## 2026-10-05 — pages.jsonl writer design: open-once vs. open-per-write
**What I asked:** Whether pages.jsonl is a separate file I write by hand, and
proposed keeping one contiguous file open for the whole crawl rather than
reopening it per write.
**What the assistant did:** Clarified that pages.jsonl is a data file
produced entirely by crawler.py, never hand-edited, and that "one contiguous
file" is true regardless of which write strategy is used — the real
trade-off is open-once-for-the-run (slightly more efficient, needs explicit
`.flush()` after every write for crash safety) versus open-per-write (simpler,
automatically flushes via Python's `with` block closing the file each time).
No code written.
**How I used it:** Chose to implement `appendRecord()` using the
open-per-write pattern with a `with open(..., 'a')` block, which the
assistant confirmed already provides full crash-safety equivalent to
explicit flushing, since closing a file flushes its buffer.
**Verification:** Ran the crawler with a small budget (2 pages) and
confirmed `artifacts/pages.jsonl` was created and correctly populated with
one JSON line per fetched page.

## 2026-10-05 — Minor cleanup: redundant import, dead imports
**What I asked:** N/A — reviewed my own full file.
**What the assistant did:** Pointed out `import datetime` was immediately
shadowed by the later `from datetime import datetime, timezone` (harmless
but redundant), and flagged remaining unused imports (`from urllib import
response`, `import lxml`, `import protego`, `from lxml.etree import
canonicalize`) as dead weight worth removing before submission. No code
written.
**How I used it:** Removed the redundant and unused imports myself.
**Verification:** N/A (cleanup only; confirmed by inspection).

## 2026-10-05 — crawl.log design: schema and decision-point inventory
**What I asked:** To start building crawl.log.
**What the assistant did:** Reiterated the assignment's own guidance to
design this file's contents deliberately, since un-logged decisions can't be
recovered without re-crawling. Walked through the required schema (ts,
event, url, failure_reason, status) and proposed a `logEvent()` helper
function following the same pattern as `appendRecord()`. Inventoried every
decision point in the existing crawler() code that should produce a log
entry: robots-denial, redirect failure, bad status, non-HTML content,
oversized response, successful fetch, and each link enqueued to the
frontier. Flagged an open design problem: `redirectHandler()` currently
collapses several distinct failure modes (timeout, connection error, loop
detected, hop cap exceeded, off-domain redirect) into one generic `None`
return, meaning `crawler()` can't currently log a precise failure_reason for
redirect failures — flagged as needing resolution before full logging
coverage is possible. No code written yet.
**How I used it:** Used this as the design checklist for implementing
logEvent() and placing calls throughout crawler() and redirectHandler().
**Verification:** N/A (design discussion); implementation not yet started.
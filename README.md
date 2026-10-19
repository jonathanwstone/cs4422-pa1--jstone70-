# cs4422-pa1--jstone70-
4433 Assignment 1 Web Crawler

# KSU Web Crawler and Corpus Analysis

## Overview

This project implements a Python web crawler and corpus analysis tool for websites within the Kennesaw State University (`kennesaw.edu`) domain.

The crawler collects HTML pages and metadata, follows in-scope links, respects robots.txt restrictions, applies per-host request delays, handles redirects and selected HTTP errors, and records its actions in crawl artifacts.

The analysis script processes those artifacts to investigate URL patterns, duplicate content, crawl failures, link structure, boilerplate removal, word frequencies, Zipf's law, TF-IDF keywords, and crawl politeness.

**Author:** Jonathan Stone  
**Course:** cs4422-pa1: Information Retrival  
**Project type:** Individual project  
**Crawl budget:** 500 pages  
**Approximate crawl runtime:** 3 hours

This project was completed independently by one student.

## Project Structure

```text
WorldWideWebCrawler/
├── crawler.py
├── analyze.py
├── requirements.txt
├── README.md
├── .gitignore
├── docs/
│   ├── analysis.md
│   └── ai_log.md
└── artifacts/
    ├── pages.jsonl
    ├── crawl.log
    └── stats.jsonl
```

The structure above represents the expected organization. Adjust it to match the files actually included in the final repository.

## Requirements

- Python: 3.12.3
- pip
- Internet access to retrieve pages
- The dependencies listed in `requirements.txt`

## Installation

1. Clone or download the repository.
2. Open a terminal in the repository directory.
3. Create a virtual environment.

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

4. Install the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

5. Download the NLTK English stopword corpus if it is not already installed:

```powershell
python -m nltk.downloader stopwords
```

## Running the Crawler

The crawler accepts one or more seed URLs and supports options for the maximum page count, default request delay, and output directory.

Example:

```powershell
python crawler.py --seeds https://www.kennesaw.edu/ --max-pages 500 --delay 1.0 --output-dir artifacts
```

### Command-line arguments

| Argument | Description | Default |
|---|---|---|
| `--seeds` | One or more starting URLs; required | None |
| `--max-pages` | Maximum number of successfully fetched pages | `500` |
| `--delay` | Default per-host request delay in seconds | `1.0` |
| `--output-dir` | Directory for crawl artifacts | `artifacts` |

The seed URLs must use HTTP or HTTPS and belong to `kennesaw.edu` or one of its subdomains.

### Crawling behavior

The crawler:

- Normalizes URLs to reduce redundant crawling.
- Checks robots.txt rules and caches the results by host.
- Restricts discovered URLs and redirects to KSU hosts.
- Applies the greater of the configured delay and the host's declared crawl delay when available.
- Handles redirects, with a maximum of five redirect hops.
- Handles HTTP 429 and 503 responses with a retry based on the `Retry-After` header when available.
- Rejects non-successful responses and non-HTML content.
- Limits the amount of response content read to 5,000,000 bytes.
- Records enqueue, fetch, skip, and error events.

## Running the Analysis

After the crawler has produced its artifacts, run:

```powershell
python analyze.py --pages artifacts/pages.jsonl --crawl artifacts/crawl.log --stats artifacts/stats.jsonl
```

All three arguments have defaults, so the analysis can also be run with:

```powershell
python analyze.py
```

The analysis script reads the JSON Lines files and prints measurements and examples for the investigation questions.

## Output Artifacts

### `artifacts/pages.jsonl`

Contains one JSON record per successfully processed HTML page. Records include:

- Canonicalized URL
- HTTP status
- Fetch timestamp
- Page title and extracted text
- Word count
- Outgoing links
- SHA-256 hash of normalized extracted text
- Declared canonical link, when present

### `artifacts/crawl.log`

Contains JSON Lines event records, including the event type, URL, failure reason, HTTP status, event timestamp, and fetch timing information.

### `artifacts/stats.jsonl`

Contains the final crawl statistics, including the number of fetched pages, URLs seen, robots-related skips, the stopping reason, and elapsed time.

## Crawl Configuration and Runtime

The crawl was configured with a page budget of 500 and took approximately three hours.

- **Seed URLs:** [kennesaw.edu]
- **Page budget:** 500
- **Default delay:** 1 second
- **Output directory:** `artifacts`
- **Observed runtime:** Approximately 3 hours
- **Actual fetched page count:** [500]
- **Crawl date:** [Oct-15-2026]

Actual delays may be longer than the default because individual hosts can specify longer crawl delays, and requests may be affected by server responses, retries, and network latency.

## Analysis Report

The detailed results and discussion are provided in `docs/analysis.md`. The report examines:

1. URL patterns and potential crawler traps
2. Duplicate and near-duplicate content
3. Crawl failure categories
4. Incoming and outgoing link counts
5. Boilerplate removal
6. Word frequencies and Zipf's law
7. TF-IDF keyword extraction
8. Crawl politeness and robots.txt restrictions

## Environment

- Python 3.12.3
- Dependencies are listed in `requirements.txt`.
- The project uses a Python virtual environment (`.venv`) to isolate dependencies.


## Reproducibility and Limitations

The analysis can be rerun against the existing crawl artifacts without repeating the crawl.

The TF-IDF analysis randomly samples five pages, so its selected pages can vary between runs unless the random sampling is made reproducible.

Repeating the crawl may produce different results because website content, access restrictions, redirects, and server responses can change.

The crawler is limited by its page budget, seed URLs, host restrictions, robots.txt policies, and response-size limit. The resulting corpus represents the pages successfully processed during the recorded crawl, not the entirety of Kennesaw State University's web presence.

## Author Contributions

This was an individual project. I developed and tested the crawler and analysis script, conducted the crawl, examined the resulting artifacts, and prepared the analysis report.

AI assistance, if applicable, is documented separately in `docs/ai_log.md`.

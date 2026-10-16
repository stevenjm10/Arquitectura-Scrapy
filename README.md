# scrapy instagram

I use scrapy instagram to collect Instagram profile information and explore it in a local dashboard. The scraper uses Python and Playwright to read the rendered page, while the dashboard presents the exported data in a more organized way.

My main extraction setup collects up to **50 posts, 100 followers, and 100 following accounts**. These are collection limits, so the final number can be lower if Instagram stops loading records or the page layout does not match the selectors.

## What the project includes

- Profile biography and visible follower/following counters.
- Post links, captions, and dates when they can be detected.
- Deduplicated follower and following profile candidates.
- JSON and CSV exports, saved throughout the extraction.
- A local dashboard with colored summary cards, search, sorting, pagination, and a run selector.
- Resume support and an option to retry posts with missing captions or dates.

The dashboard interface is in Spanish. The source code, command-line options, comments, and new export field names are in English. Historical exports remain readable through a compatibility module.

## Requirements

- Python 3.11 or later.
- Playwright and its Chromium browser.
- An Instagram session, signed in manually through the browser when needed.

## Installation

I run these commands from the project folder in PowerShell:

```powershell
py -m venv .venv_nuevo
.\.venv_nuevo\Scripts\python.exe -m pip install -r requirements.txt
.\.venv_nuevo\Scripts\python.exe -m playwright install chromium
```

If `.venv_nuevo` already works, I skip creating it again. On Linux or macOS, I use `python3 -m venv .venv` and replace the Windows Python path with `.venv/bin/python`.

## Running the scraper

This is the command I use for the Rubius profile:

```powershell
.\.venv_nuevo\Scripts\python.exe scraper.py --username elrubiuswtf --limit 50 --relationship-limit 100
```

The browser opens and waits up to 180 seconds for an active session. If Instagram asks me to sign in, I do that in the browser. I do not need to press Enter in the terminal. I keep the terminal and browser open until the extraction finishes.

The scraper saves its progress and generates `dashboard.html` when it finishes or handles an interruption. I can stop it with Ctrl+C and resume later. A detected authentication challenge or restriction stops extraction instead of triggering automatic retries.

## Opening the dashboard

I open `dashboard.html` in my browser:

```powershell
Start-Process .\dashboard.html
```

To rebuild it from existing exports without opening Instagram:

```powershell
py dashboard.py
```

The dashboard reads both the current `results/` folder and the historical `resultados/` folder. I can choose an extraction from the selector or import an export with the JSON file button. After rebuilding the page, I reload the browser to see the latest data.

The generated HTML works offline and does not require a web server. It contains a copy of the exported data, so sharing the HTML also shares that data.

## Resuming an extraction

For a new-format export, I use:

```powershell
.\.venv_nuevo\Scripts\python.exe scraper.py --username elrubiuswtf --resume results\RUN_FOLDER\data.json
```

I can also resume the historical export used in this project:

```powershell
.\.venv_nuevo\Scripts\python.exe scraper.py --username elrubiuswtf --relationships-only --relationship-limit 100 --resume resultados\20261015_235333_249974\datos.json
```

This second command skips the posts and repeats only the follower and following lists. It preserves the existing posts. Relationship lists are collected again from the beginning; the scraper does not restore the previous scroll position.

When resuming a historical export, the scraper writes `data.json` and the English-named CSV files into the same run folder. It leaves the original Spanish-named files unchanged. I use `data.json` for subsequent resumes because it contains the latest progress, and the dashboard prefers it automatically.

To retry posts with missing captions or dates:

```powershell
.\.venv_nuevo\Scripts\python.exe scraper.py --username elrubiuswtf --limit 50 --retry-incomplete --posts-only --resume resultados\20261015_235333_249974\data.json
```

Previously recovered fields are kept if the new attempt cannot obtain them. Error history is also kept when resuming, so an earlier `KeyboardInterrupt` entry does not necessarily describe the latest attempt.

## Command-line options

| Option | Purpose |
| --- | --- |
| `--username` | Required target username, with or without `@`. |
| `--limit` | Post limit from 1 to 50; defaults to 50. |
| `--relationship-limit` | Limit per relationship list from 1 to 100; defaults to 100. |
| `--posts-only` | Skip both relationship lists. |
| `--skip-relationships` | Alias for `--posts-only`. |
| `--relationships-only` | Skip post collection. |
| `--retry-incomplete` | Re-read saved posts with a missing caption or date. |
| `--resume` | Path to a current or historical JSON export. |
| `--manual-bio` | Select the biography by clicking its text in the browser. |
| `--output` | Run directory root; defaults to `results/` for new extractions. |

For a custom dashboard source or destination:

```powershell
py dashboard.py --results my_results --output my_dashboard.html
```

The previous Spanish command-line options have been replaced by the English options above.

## Output files

New runs are stored under `results/RUN_TIMESTAMP/`:

| File | Contents |
| --- | --- |
| `data.json` | Profile, posts, relationships, statuses, errors, and extraction summary. |
| `posts.csv` | Post URL, caption, date, extraction status, and method. |
| `followers.csv` | Collected follower profile candidates. |
| `following.csv` | Collected following profile candidates. |

JSON preserves original text. CSV cells that could be interpreted as spreadsheet formulas receive a protective prefix. JSON is saved through a temporary file replacement.

## How I organized the code

| File | Responsibility |
| --- | --- |
| `scraper.py` | Browser navigation, extraction, progress saving, and command-line options. |
| `dashboard.py` | Loading exports and generating the local HTML dashboard. |
| `dashboard.template.html` | Dashboard layout, styling, and browser interactions. |
| `legacy_data.py` | Converting historical field and status names in memory. |
| `test_local.py` | Local checks for URL handling, exports, compatibility, retries, and cleanup. |

I open **`dashboard.html`**, rather than the template, to view the generated results. The template is the source used to build that page.

## Data quality and limitations

I treat the results as a partial extraction rather than a complete copy of an Instagram account:

- The post limit follows the profile grid, which may include pinned posts. It does not guarantee the 50 most recent posts.
- Captions are read from the rendered page or an author-attributed quotation in page metadata. Missing text means it was not detected; it does not prove that the post has no caption. Extracted text may be truncated.
- Dates are read from DOM time elements or publication metadata when available.
- Biographies can be incomplete or include extra profile text, especially with manual selection.
- Exact counters are saved only when the scraper finds a numeric `title` attribute. Abbreviated visible counts are not converted into exact totals.
- Relationship candidates come from profile links inside the dialog. Suggestions may be mixed in, and scrolling may stop before the requested limit.
- Quality bars show whether fields were detected, not whether their contents are accurate. An empty error list does not guarantee a complete extraction.
- Photos, videos, stories, likes, and engagement metrics are not collected.

Earlier runs recovered 50 posts, 50 follower candidates, and 100 following candidates. Caption detection remained incomplete. Local tests check program behavior, but live selector changes still need validation against Instagram.

## Session storage

New sessions use `.instagram_session/`. If the existing `.sesion_instagram/` folder is present, the scraper reuses it to preserve the current login.

I keep these folders private because they can contain credentials that provide account access. Passwords are not requested or printed in the terminal. To remove a session, I close the scraper and browser first, then delete its session folder.

## Local checks

```powershell
py -m unittest test_local -v
py -m py_compile scraper.py dashboard.py legacy_data.py
```

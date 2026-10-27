# scrapy instagram

I use this project to collect Instagram profile information and view it in a local dashboard. The scraper runs with Python and Playwright, and the dashboard shows publications, screenshots, followers, and following accounts.

The project has three application files:

- `scraper.py`: collects the data, captures visible post media, and saves the results.
- `dashboard.py`: contains the dashboard layout and generates `dashboard.html`.
- `gemini_server.py`: serves the local pages and keeps Gemini API calls behind a local Python endpoint.

The source code and commands are in English. The dashboard interface is in Spanish.

## Installation

I run these commands from the project folder in PowerShell:

```powershell
py -m venv .venv_nuevo
.\.venv_nuevo\Scripts\python.exe -m pip install -r requirements.txt
.\.venv_nuevo\Scripts\python.exe -m playwright install chromium
```

If the environment already works, I skip creating it again.

## Collecting data

To collect up to 50 posts, 100 followers, and 100 following accounts:

```powershell
.\.venv_nuevo\Scripts\python.exe scraper.py --username elrubiuswtf --limit 50 --relationship-limit 100
```

For a smaller extraction of 25 posts, I use:

```powershell
.\.venv_nuevo\Scripts\python.exe scraper.py --username elrubiuswtf --limit 25 --relationship-limit 100
```

The browser opens and waits for my Instagram session. If needed, I sign in through the browser without pressing Enter in the terminal. I leave the terminal and browser open while the program runs.

Each post is saved with its link, caption and date when available. I download the image served by Instagram when available, and fall back to a JPEG screenshot if downloading fails. The delivered image may be resized by Instagram. For videos and reels, I save a cover image or visible frame; the video file itself is not downloaded. Carousel posts currently show one image.

The gallery shows large image previews, captions, an image download button, and a link to Instagram. Missing captions and images remain empty until a new extraction recovers them. I can use `--retry-incomplete` with `--resume` to revisit posts with missing captions or dates.

## Opening the dashboard

The scraper generates `dashboard.html` automatically. For the offline dashboard, I open it with:

```powershell
Start-Process .\dashboard.html
```

To rebuild it from existing results:

```powershell
python dashboard.py
```

The dashboard includes profile information, screenshot cards, search, sorting, pagination, and separate follower and following lists. It embeds the separate `bigfive.html` report for the exploratory text analysis, and provides a link to open it on its own. Rebuild both pages with `python dashboard.py`, then reload them.

To enable the optional Gemini analysis, I set a replacement key in PowerShell and run the local server:

The key visible in the shared screenshot is exposed. I revoke it in Google AI Studio and create a new key; I never reuse or paste an API key into HTML or source code.

```powershell
$env:GEMINI_API_KEY = "PASTE_YOUR_NEW_KEY_HERE"
python gemini_server.py
```

Then I open `http://127.0.0.1:8765/dashboard.html` in the browser. The server listens only on this computer; I leave that terminal running while I use the dashboard and press Ctrl+C to stop it. The report sends captions to Google Gemini only after I press **Analizar captions con Gemini**. The key stays in the server environment and is never written into the HTML. The Gemini analysis needs an internet connection; the lexical word counts still work offline.

Screenshots are embedded in the generated HTML, so the offline view can be opened without a server or internet connection. Sharing generated HTML also shares its captions and screenshots.

## Continuing a saved run

To continue an extraction and capture posts that do not have screenshots yet:

```powershell
.\.venv_nuevo\Scripts\python.exe scraper.py --username elrubiuswtf --limit 50 --posts-only --resume results\RUN_FOLDER\data.json
```

For the existing local extraction in this project, I use:

```powershell
.\.venv_nuevo\Scripts\python.exe scraper.py --username elrubiuswtf --limit 50 --posts-only --resume resultados\20261015_235333_249974\data.json
```

I use the current `data.json` file for resuming. Previous Spanish-named exports remain on disk, but the simplified application reads the current English field names. Existing local runs were converted before removing the compatibility module.

## Useful options

| Option | Purpose |
| --- | --- |
| `--username` | Instagram username. |
| `--limit` | Post limit, from 1 to 50. |
| `--relationship-limit` | Limit per follower/following list, from 1 to 100. |
| `--posts-only` | Collect posts without repeating relationship lists. |
| `--relationships-only` | Collect relationship lists without opening posts. |
| `--retry-incomplete` | Retry posts with missing captions or dates. |
| `--resume` | Continue from a saved `data.json`. |
| `--no-screenshots` | Collect text data without capturing post images. |
| `--output` | Choose the directory for new extraction runs. |

## Saved files

New runs are stored in `results/RUN_TIMESTAMP/`:

```text
data.json
posts.csv
followers.csv
following.csv
media/
    POST_CODE.jpg
```

The dashboard also reads current-format exports in the existing `resultados/` folder. The `media/` folder is needed when rebuilding the dashboard from saved data. Saved runs and their available images are included automatically when the dashboard is generated; there is no manual JSON import.

I keep extracted data, screenshots, virtual environments, generated HTML, and browser sessions out of GitHub. New browser sessions use `.instagram_session/`; the existing `.sesion_instagram/` is reused when present. These session folders stay private because they can provide account access.

## Collection limits

The scraper follows the profile grid, which may contain pinned posts, so the first 50 links are not guaranteed to be the 50 most recent posts. The dashboard can sort the dates that were recovered. Captions, dates, and relationship lists may be incomplete, and suggested profiles can appear among relationship candidates. The configured limits are maximum targets rather than guaranteed totals.


## Interaction counts

Posts record `likes`, `comments`, and `reposts` when Instagram reports them in post-specific JSON-LD, counter metadata, or supported visible counter controls. Missing or hidden counts stay `null`, not zero. Abbreviated counts such as 1.2K are approximate; JSON stores per-field sources and approximation flags. The dashboard marks rounded counts with ≈.

`interactions` is the sum of these three counts only when all three are available in new records. It is not Instagram Insights total interactions and excludes saves and other actions. `interactions_observed` is a partial sum when some counters are unavailable. CSV exports include counts, totals, an approximation flag and the check time. The scraper does not click engagement buttons or access private Insights.

Saved posts without a counter check are revisited on resume. Use `--posts-only --refresh-interactions --resume PATH_TO_DATA_JSON` to refresh counts without repeating relationship lists. The counters can change over time. A live run is needed to populate them; rebuilding the dashboard alone cannot recover missing values.


## Automatic extraction

Biography, posts, images and available counters are read automatically. There is no manual biography selection. The browser reuses the saved Instagram session. If it expires or Instagram requests verification, I complete authentication in the browser; the scraper cannot bypass that requirement. Unavailable biography text or counters remain missing instead of prompting for manual selection.


## Comment text and reposts

`--comments-limit` sets a collection target per post (default 25, from 0 to 200). Zero disables comment text collection. The scraper keeps any extra comments already loaded, so this is a target rather than a strict cap. It saves comment text, author, date and link in each post's `comments_list` and in `comments.csv`. Loaded comments are not guaranteed to be complete or exclusively top-level replies, and the reported comment counter remains separate from the number collected. Failed or skipped collection preserves previously saved comment text.

The current version also reads repost counters when a supported label is present. New post interaction sums include likes, comments and reposts; a full sum requires all three counters. The dashboard calculates this sum from those same counters for older records as well, excluding shares. Missing counters are never replaced with zero.

Collection loops share one bounded collector with per-operation scrolling and parsing. Optional media/comment failures use a common handler; restriction checks still stop the run. This keeps the two-script application and the existing resume and export options.

Saved comment text is displayed in an expandable section on each dashboard post, with its author, date and link when available. The saved comment count is separate from Instagram's reported total.

## Big Five exploratorio

`bigfive.html` muestra coincidencias léxicas orientativas y, opcionalmente, un análisis cualitativo con Gemini. El análisis de Gemini revisa solo los captions, exige al menos tres captions y 50 palabras, y solo se ejecuta tras pulsar el botón. Es una exploración del texto, no un test validado ni una evaluación psicológica o laboral, y no debe usarse para tomar decisiones sobre una persona. La página se regenera junto con `dashboard.html` al ejecutar `python dashboard.py`.

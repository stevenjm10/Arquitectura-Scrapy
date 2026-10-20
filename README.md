# scrapy instagram

I use this project to collect Instagram profile information and view it in a local dashboard. The scraper runs with Python and Playwright, and the dashboard shows publications, screenshots, followers, and following accounts.

The project has two application files:

- `scraper.py`: collects the data, captures visible post media, and saves the results.
- `dashboard.py`: contains the dashboard layout and generates `dashboard.html`.

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

The scraper generates `dashboard.html` automatically. I open it with:

```powershell
Start-Process .\dashboard.html
```

To rebuild it from existing results:

```powershell
py dashboard.py
```

The dashboard includes profile information, screenshot cards, search, sorting, pagination, and separate follower and following lists. I reload the page after rebuilding it.

Screenshots are embedded in the generated HTML, so it can be opened without a server or internet connection. Sharing that HTML also shares its data and screenshots.

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

The dashboard also reads current-format exports in the existing `resultados/` folder. The `media/` folder is needed when rebuilding the dashboard from saved data. Importing a raw `data.json` alone does not import separate image files; rebuilding with `dashboard.py` includes the available screenshots.

I keep extracted data, screenshots, virtual environments, generated HTML, and browser sessions out of GitHub. New browser sessions use `.instagram_session/`; the existing `.sesion_instagram/` is reused when present. These session folders stay private because they can provide account access.

## Collection limits

The scraper follows the profile grid, which may contain pinned posts, so the first 50 links are not guaranteed to be the 50 most recent posts. The dashboard can sort the dates that were recovered. Captions, dates, and relationship lists may be incomplete, and suggested profiles can appear among relationship candidates. The configured limits are maximum targets rather than guaranteed totals.


## Interaction counts

Posts record `likes`, `comments`, and `shares` when Instagram reports them in post-specific JSON-LD, counter metadata, or supported visible counter controls. Missing or hidden counts stay `null`, not zero. Abbreviated counts such as 1.2K are approximate; JSON stores per-field sources and approximation flags. The dashboard marks rounded counts with ≈.

`interactions` is the sum of these three counts only when all three are available. It is not Instagram Insights total interactions and excludes saves and other actions. `interactions_observed` is a partial sum when some counters are unavailable. CSV exports include counts, totals, an approximation flag and the check time. Shares cannot be inferred from a share button or from the number of comments loaded. The scraper does not click engagement buttons or access private Insights.

Saved posts without a counter check are revisited on resume. Use `--posts-only --refresh-interactions --resume PATH_TO_DATA_JSON` to refresh counts without repeating relationship lists. The counters can change over time. A live run is needed to populate them; rebuilding the dashboard alone cannot recover missing values.


## Automatic extraction

Biography, posts, images and available counters are read automatically. There is no manual biography selection. The browser reuses the saved Instagram session. If it expires or Instagram requests verification, I complete authentication in the browser; the scraper cannot bypass that requirement. Unavailable biography text or counters remain missing instead of prompting for manual selection.

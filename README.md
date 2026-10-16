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

The browser opens and waits for my Instagram session. If needed, I sign in through the browser without pressing Enter in the terminal. I leave the terminal and browser open while the program runs.

Each post is saved with its link, caption and date when available, and a JPEG screenshot. For videos and reels, the screenshot captures the visible frame; it does not download the video file. If the media cannot be captured separately, the scraper saves the visible browser area instead.

The screenshots come from what the browser renders. They are not downloads of the original-resolution media.

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
| `--manual-bio` | Select the profile biography with a click. |
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

import argparse
import csv
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from dashboard import generate_dashboard
from legacy_data import normalize_data
BASE = Path(__file__).resolve().parent
RESERVED_PATHS = {'accounts', 'explore', 'direct', 'reels', 'reel', 'p', 'stories',
              'about', 'legal', 'privacy', 'terms', 'challenge', 'settings'}

class InstagramRestriction(RuntimeError):
    """Stop extraction when Instagram reports a restriction."""

def username_from_url(url):
    parts = urlsplit(url)
    name = parts.path.strip('/')
    if parts.hostname not in {'www.instagram.com', 'instagram.com'}:
        return None
    if re.fullmatch(r'[A-Za-z0-9._]{1,30}', name) and name not in RESERVED_PATHS:
        return name
    return None

def get_text(locator):
    return locator.first.inner_text().strip() if locator.count() else ''

def check_access(page):
    if any(p in urlsplit(page.url).path for p in ('/challenge/', '/checkpoint/', '/accounts/login')):
        raise InstagramRestriction('Instagram requires authentication or verification. Extraction stopped.')
    body = page.locator('body').inner_text().lower()
    warnings = ('try again later', 'inténtalo de nuevo más tarde', 'intentá de nuevo más tarde',
              'we restrict certain activity', 'restringimos cierta actividad')
    if any(a in body for a in warnings):
        raise InstagramRestriction('Instagram reports a temporary restriction. Automatic retries are disabled.')

def open_page(page, url):
    page.goto(url, wait_until='domcontentloaded')
    page.locator('main, article, header').first.wait_for(state='visible')
    check_access(page)

def select_text(page, name):
    print(f'In the browser, click exactly on {name}. You have 90 seconds.')
    page.evaluate('''() => {

        window.__selectedText = null;

        if (window.__textSelector) document.removeEventListener('click', window.__textSelector, true);

        window.__textSelector = e => {

            e.preventDefault(); e.stopPropagation();

            window.__selectedText = e.target.innerText || e.target.textContent || '';

            document.removeEventListener('click', window.__textSelector, true);

        };

        document.addEventListener('click', window.__textSelector, true);

    }''')
    try:
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            selected = page.evaluate("() => window.__selectedText")
            if selected is not None:
                return selected.strip()
            page.wait_for_timeout(250)
        raise TimeoutError(
            "The biography was not selected within 90 seconds. "
            "Run the program again and click the biography text."
        )
    finally:
        if not page.is_closed():
            page.evaluate("""() => {
                document.removeEventListener('click', window.__textSelector, true);
            }""")

def relationship_link(page, username, kind):
    pattern = re.compile(r"\b(seguidores|followers)\b" if kind == 'followers'
                        else r"\b(seguidos|following)\b", re.I)
    candidates = page.get_by_role('link', name=pattern)
    for i in range(candidates.count()):
        if candidates.nth(i).is_visible():
            return candidates.nth(i)
    return page.locator(f'a[href="/{username}/{kind}/"]').first

def normalize_post_url(url):
    parts = urlsplit(url)
    if parts.hostname not in {'instagram.com', 'www.instagram.com'}:
        return None
    match = re.fullmatch(
        r'/(?:[A-Za-z0-9._]+/)?(p|reel)/([A-Za-z0-9_-]+)/?', parts.path)
    if not match:
        return None
    return f'https://www.instagram.com/{match[1]}/{match[2]}/'

def extract_bio(page):
    # Metadata can contain the biography even when the visible text is collapsed.
    # Only read the quoted segment after the counters.
    # Keep the biography separate from the profile header.
    for selector in ('meta[property="og:description"]', 'meta[name="description"]'):
        element = page.locator(selector).first
        content = element.get_attribute('content') if element.count() else None
        if not content:
            continue
        match = re.search(r':\s*["“](.*)["”]\s*$', content, re.S)
        if match:
            bio = match.group(1).strip()
            return {'bio': bio or None,
                    'bio_method': selector,
                    'bio_status': 'metadata_extracted_unverified' if bio else 'empty_in_metadata'}
    return {'bio': None, 'bio_method': 'metadata',
            'bio_status': 'not_detected_automatically'}

def wait_for_session(page, context, timeout=180):
    print('Waiting for an Instagram session (up to 180 seconds). Sign in through the browser if needed. Do not press Enter.')
    limit = time.monotonic() + timeout
    while time.monotonic() < limit:
        if page.is_closed():
            raise RuntimeError('The browser window was closed.')
        path = urlsplit(page.url).path
        if any(p in path for p in ('/challenge/', '/checkpoint/')):
            raise RuntimeError('Instagram requires verification. Complete it and run the program again.')
        # Check for the session cookie without printing its value.
        session = any(c['name'] == 'sessionid' and bool(c['value'])
                     for c in context.cookies('https://www.instagram.com/'))
        if session and not any(p in path for p in ('/accounts/login', '/accounts/onetap')):
            check_access(page)
            return
        page.wait_for_timeout(1000)
    raise TimeoutError('No active session was detected before the timeout.')

def profile(page, username, manual_bio=False):
    open_page(page, f'https://www.instagram.com/{username}/')
    page.locator('header').filter(has_text=re.compile(r'seguidores|followers', re.I)).first.wait_for(state='visible')
    if username_from_url(page.url) is None or username_from_url(page.url).lower() != username.lower():
        raise RuntimeError('The URL does not match the requested profile.')
    check_access(page)
    header = page.locator('header').filter(has_text=re.compile(r'seguidores|followers', re.I))
    data = {'username': username, 'url': page.url,
             'visible_header': get_text(header), 'bio': None,
             'bio_method': 'assisted HTML element selection'}
    for field, path in [('followers_visible', 'followers'), ('following_visible', 'following')]:
        link = relationship_link(page, username, path)
        data[field] = get_text(link)
        titles = link.locator('[title]').evaluate_all(
            '(els) => els.map(e => e.getAttribute("title"))') if link.count() else []
        exact = next((t for t in titles if re.fullmatch(r'[0-9]+(?:[., \u00a0][0-9]{3})*', t)), None)
        data[field.replace('_visible', '_total')] = (
            int(re.sub(r'\D', '', exact)) if exact else None)
    if manual_bio:
        data['bio'] = select_text(page, 'the profile biography text')
        data['bio_method'] = 'manual_selection_unconfirmed'
        data['bio_status'] = 'selected_by_user'
    else:
        data.update(extract_bio(page))
    return data

def collect_post_links(page, limit, checkpoint=None):
    links = {}
    stalled = 0
    for round_index in range(200):
        check_access(page)
        previous = len(links)
        urls = page.locator('a[href]').evaluate_all(
            "(els) => els.filter(e => e.querySelector('img, video') && e.getClientRects().length).map(e => e.href)")
        for url in urls:
            normalized = normalize_post_url(url)
            if normalized:
                links[normalized] = None
        print(f'Grid: {len(links)} unique links found (target {limit}).')
        if checkpoint:
            checkpoint(list(links)[:limit])
        if len(links) >= limit:
            return list(links)[:limit], 'target_reached'
        stalled = stalled + 1 if len(links) == previous else 0
        if stalled >= 5:
            return list(links), 'no_new_links; completeness_unverified'
        # Some layouts scroll an inner container instead of the window.
        page.evaluate(r"""() => {
            const anchor = [...document.querySelectorAll('a[href]')].find(e =>
                /\/(p|reel)\/[^/]+/.test(e.getAttribute('href') || '') &&
                e.querySelector('img, video') && e.getClientRects().length);
            let el = anchor;
            while (el) {
                if (el.clientHeight > 100 && el.scrollHeight > el.clientHeight + 10 &&
                    /auto|scroll/.test(getComputedStyle(el).overflowY)) {
                    el.scrollTop += Math.max(300, el.clientHeight * 0.8);
                    return;
                }
                el = el.parentElement;
            }
            window.scrollBy(0, Math.max(500, window.innerHeight * 0.8));
        }""")
        page.wait_for_timeout(2500)
    return list(links)[:limit], 'scroll_limit'

def caption_from_metadata(content, username):
    """Extract only the final quotation attributed to the requested author."""
    if not content or not username:
        return None
    match = re.fullmatch(r'(.*?):\s*["“](.*)["”]\s*', content, re.S)
    if not match:
        return None
    if not re.search(r'(?<![\w.])' + re.escape(username) + r'(?![\w.])', match[1], re.I):
        return None
    return match[2].strip() or None


def should_retry(row, incomplete=False):
    return (row.get('status') == 'error' or
            (incomplete and (not row.get('caption') or not row.get('date'))))


def extract_post(page, url, username=None):
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    open_page(page, url)
    # Navigation may finish before the post is rendered.
    try:
        page.wait_for_function('''() => !!document.querySelector(
            'article h1, main h1, article time[datetime], main time[datetime]')''', timeout=8000)
    except PlaywrightTimeoutError:
        check_access(page)
    main_content = page.locator('article')
    if not main_content.count():
        main_content = page.locator('main')
    caption_element = main_content.locator('h1')
    date = main_content.locator('time[datetime]')
    caption = get_text(caption_element) if caption_element.count() else None
    method = 'DOM article/main h1' if caption else 'caption_not_detected'
    if not caption:
        for selector in ('meta[property="og:description"]', 'meta[name="description"]'):
            meta = page.locator(selector).first
            content = meta.get_attribute('content') if meta.count() else None
            caption = caption_from_metadata(content, username)
            if caption:
                method = selector + '; quotation attributed to the username; check for truncation'
                break
    extracted_date = date.first.get_attribute('datetime') if date.count() else None
    if not extracted_date:
        for selector in ('meta[property="article:published_time"]', 'meta[property="og:published_time"]'):
            meta = page.locator(selector).first
            value = meta.get_attribute('content') if meta.count() else None
            if value:
                try:
                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    continue
                extracted_date = value
                break
    return {'url': url, 'caption': caption, 'date': extracted_date,
            'status': 'extracted_check_truncation' if caption else 'caption_not_detected',
            'method': method + '; date from DOM time or publication metadata'}

def extract_relationships(page, username, kind, checkpoint, limit=100):
    open_page(page, f'https://www.instagram.com/{username}/')
    relationship_link(page, username, kind).click()
    dialog = page.get_by_role('dialog').last
    dialog.wait_for(state='visible')
    page.wait_for_timeout(2000)
    found = {}
    print(f'{kind}: reading profile candidates from the dialog; membership is unverified.')
    stalled = 0
    for _ in range(500):
        check_access(page)
        previous = len(found)
        # Do not require buttons: Instagram may use other elements for actions.
        # Profile links are candidates; list membership remains unverified.
        urls = dialog.locator('a[href]').evaluate_all('(els) => els.map(e => e.href)')
        for url in urls:
            name = username_from_url(url)
            if name and name.lower() != username.lower():
                found[name.lower()] = {'username': name, 'url': f'https://www.instagram.com/{name}/'}
                if len(found) >= limit:
                    rows = list(found.values())[:limit]
                    checkpoint(rows, 'limit_reached; partial_sample')
                    print(f'{kind}: limit of {limit} users reached.')
                    return rows, 'limit_reached; partial_sample'
        print(f'{kind}: {len(found)} users found.')
        checkpoint(list(found.values()), 'in_progress')
        stalled = stalled + 1 if len(found) == previous else 0
        if stalled >= 5:
            if not found:
                raise RuntimeError('No profiles were detected in the dialog. The list may be empty or the selector may not match; a zero total is not confirmed.')
            return list(found.values()), 'no_new_users; completeness_unverified'
        # Find the scrollable container inside the dialog.
        moved = dialog.evaluate('''root => {

            const nodes = [root, ...root.querySelectorAll('*')].filter(e =>

                e.clientHeight > 100 && e.scrollHeight > e.clientHeight + 10 &&

                /auto|scroll/.test(getComputedStyle(e).overflowY));

            nodes.sort((a,b) => b.scrollHeight - a.scrollHeight);

            const el = nodes[0];

            if (!el) return false;

            el.scrollTop += Math.max(200, el.clientHeight * 0.75);

            return true;

        }''')
        if not moved:
            dialog.hover()
            page.mouse.wheel(0, 500)
        page.wait_for_timeout(2200)
    return list(found.values()), 'scroll_limit; partial_result'

def safe_cell(value):
    if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@')):
        return "'" + value
    return value

def save_results(data, output):
    output.mkdir(parents=True, exist_ok=True)
    temporary = output / 'data.tmp'
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(output / 'data.json')
    tables = [('posts', ['url', 'caption', 'date', 'status', 'method']),
              ('followers', ['username', 'url']), ('following', ['username', 'url'])]
    for name, fields in tables:
        with (output / f'{name}.csv').open('w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows({k: safe_cell(v) for k, v in row.items()} for row in data[name])

def finalize_run(context, data, output):
    """Save results and build the dashboard even if the driver disconnects during cleanup."""
    posts = data['posts']
    data['summary'] = {'posts': len(posts),
                        'with_caption': sum(bool(f.get('caption')) for f in posts),
                        'with_date': sum(bool(f.get('date')) for f in posts),
                        'followers_collected': len(data['followers']),
                        'following_collected': len(data['following'])}
    save_results(data, output)
    try:
        context.close()
    except Exception as exc:
        message = f'Browser cleanup: {type(exc).__name__}: {exc}'
        data['errors'].append(message)
        print('Warning: the browser could not close normally. Results have been saved.')
        save_results(data, output)
    finally:
        try:
            generate_dashboard(None if output.parent.resolve() in {(BASE / 'results').resolve(), (BASE / 'resultados').resolve()} else output.parent)
        except OSError as exc:
            print(f'Could not generate the dashboard: {exc}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--username', required=True, help='Target profile username, without @.')
    parser.add_argument('--output', type=Path, default=BASE / 'results', help='Directory for extraction runs.')
    parser.add_argument('--resume', type=Path, help='Path to the JSON file of an earlier run.')
    parser.add_argument('--posts-only', '--skip-relationships', action='store_true', dest='skip_relationships')
    parser.add_argument('--relationships-only', dest='relationships_only', action='store_true', help='Skip posts; combine with --resume to preserve existing posts.')
    parser.add_argument('--retry-incomplete', action='store_true', help='On resume, retry posts with a missing caption or date.')
    parser.add_argument('--manual-bio', action='store_true', help='Select the biography with one click.')
    parser.add_argument('--limit', type=int, default=50)
    parser.add_argument('--relationship-limit', type=int, default=100,
                        help='Maximum records per relationship list (1–100).')
    args = parser.parse_args()
    if not 1 <= args.relationship_limit <= 100:
        parser.error('--relationship-limit must be between 1 and 100.')
    if args.relationships_only and args.skip_relationships:
        parser.error('--relationships-only cannot be combined with --posts-only.')
    username = args.username.lstrip('@')
    if not re.fullmatch(r'[A-Za-z0-9._]{1,30}', username) or not 1 <= args.limit <= 50:
        parser.error('Invalid username or post limit outside 1–50.')
    output = args.output / datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    data = {'extracted_utc': datetime.now(timezone.utc).isoformat(), 'profile': {},
             'post_target': args.limit, 'relationship_limit': args.relationship_limit, 'posts': [], 'followers': [],
             'following': [], 'statuses': {}, 'errors': []}
    if args.resume:
        try:
            previous = normalize_data(json.loads(args.resume.read_text(encoding='utf-8')))
            if previous.get('profile', {}).get('username', '').lower() != username.lower():
                parser.error('The username does not match the run being resumed.')
            for field in ('posts', 'followers', 'following'):
                if not isinstance(previous.get(field), list):
                    raise ValueError(f'Invalid field: {field}')
            data.update(previous)
            data['post_target'] = args.limit
            data['relationship_limit'] = args.relationship_limit
            data['resumed_utc'] = datetime.now(timezone.utc).isoformat()
            output = args.resume.resolve().parent
        except (OSError, ValueError) as exc:
            parser.error(f'Cannot resume: {exc}')
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(BASE / ('.sesion_instagram' if (BASE / '.sesion_instagram').exists() else '.instagram_session')), headless=False, viewport={'width': 1280, 'height': 900})
        page = context.pages[0] if context.pages else context.new_page()
        page.set_default_timeout(15000)
        try:
            page.goto('https://www.instagram.com/', wait_until='domcontentloaded')
            wait_for_session(page, context)
            check_access(page)
            data['profile'] = profile(page, username, args.manual_bio)
            save_results(data, output)
            def checkpoint_links(urls):
                data['pending_links'] = urls
                save_results(data, output)
            links = data.get('pending_links', [])
            if args.relationships_only:
                links, status = [], data['statuses'].get('post_links', 'skipped_by_option')
            elif not links or len(links) < args.limit:
                links, status = collect_post_links(page, args.limit, checkpoint_links)
            else:
                status = 'links_restored'
            links = links[:args.limit]
            data['statuses']['post_links'] = status
            for i, url in enumerate(links, 1):
                previous_post = next((f for f in data['posts'] if f.get('url') == url), None)
                if previous_post and not should_retry(previous_post, args.retry_incomplete):
                    continue
                print(f'Post {i}/{len(links)}: {url}')
                try:
                    row = extract_post(page, url, username)
                except InstagramRestriction:
                    raise
                except Exception as exc:
                    check_access(page)
                    row = {'url': url, 'caption': None, 'date': None, 'status': 'error', 'method': 'DOM'}
                    data['errors'].append(f'{url}: {type(exc).__name__}: {exc}')
                # Preserve previously recovered fields if a new attempt fails.
                if previous_post:
                    for field in ('caption', 'date'):
                        if not row.get(field) and previous_post.get(field):
                            row[field] = previous_post[field]
                            row['method'] += f'; {field} preserved from the previous extraction'
                    if row.get('caption') and row['status'] == 'caption_not_detected':
                        row['status'] = 'extracted_check_truncation'
                data['posts'] = [f for f in data['posts'] if f.get('url') != url]
                data['posts'].append(row)
                save_results(data, output)
            for field, path in [('followers', 'followers'), ('following', 'following')]:
                if args.skip_relationships:
                    data['statuses'].setdefault(field, 'skipped_by_option')
                    continue
                def checkpoint(rows, status, field=field):
                    data[field] = rows
                    data['statuses'][field] = status
                    save_results(data, output)
                try:
                    rows, status = extract_relationships(page, username, path, checkpoint, args.relationship_limit)
                except InstagramRestriction:
                    raise
                except Exception as exc:
                    check_access(page)
                    data['errors'].append(f'{field}: {type(exc).__name__}: {exc}')
                    checkpoint(data[field], 'error; partial_result')
                    continue
                checkpoint(rows, status)
        except (Exception, KeyboardInterrupt) as exc:
            data['errors'].append(f'{type(exc).__name__}: {exc}')
            if isinstance(exc, KeyboardInterrupt):
                print('Extraction interrupted from the terminal (KeyboardInterrupt). Progress has been saved.')
            else:
                print(f'Extraction stopped. Progress has been saved: {type(exc).__name__}: {exc}')
        finally:
            finalize_run(context, data, output)
    print(f'Files saved to: {output}')
    print('Review statuses and errors in data.json. A saved list may still be incomplete.')
    print('Summary:', data.get('summary', {}))
    print(f'Local dashboard: {BASE / "dashboard.html"}')

if __name__ == '__main__':
    main()

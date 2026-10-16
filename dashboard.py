"""Generate a portable dashboard from local exports without extra dependencies."""
import argparse
import json
from pathlib import Path

from legacy_data import normalize_data

BASE = Path(__file__).resolve().parent


def generate_dashboard(results=None, output=BASE / 'dashboard.html'):
    roots = [results] if results is not None else [BASE / 'results', BASE / 'resultados']
    runs = []
    for root in roots:
        if not root.exists():
            continue
        for folder in sorted(root.iterdir(), reverse=True):
            if not folder.is_dir():
                continue
            # Prefer the current export if a historical export exists alongside it.
            file = folder / 'data.json'
            if not file.exists():
                file = folder / 'datos.json'
            try:
                data = normalize_data(json.loads(file.read_text(encoding='utf-8')))
                if isinstance(data, dict):
                    runs.append({'name': folder.name, 'data': data})
            except (OSError, ValueError):
                continue
    runs.sort(key=lambda run: run['name'], reverse=True)
    template = (BASE / 'dashboard.template.html').read_text(encoding='utf-8')
    content = json.dumps(runs, ensure_ascii=True).replace('<', '\\u003c')
    output.write_text(template.replace('/* DATA */[]', content), encoding='utf-8')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, help='Directory containing extraction runs.')
    parser.add_argument('--output', type=Path, default=BASE / 'dashboard.html')
    args = parser.parse_args()
    print(generate_dashboard(args.results, args.output))

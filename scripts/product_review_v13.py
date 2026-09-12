from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'products'
CSS = '/assets/css/product-review-v13.css'
JS = '/assets/js/product-review-v13.js'


def patch(path):
    s = path.read_text(encoding='utf-8')
    if CSS not in s:
        s = s.replace('</head>', f'<link rel="stylesheet" href="{CSS}"></head>', 1)
    if JS not in s:
        s = s.replace('</body>', f'<script src="{JS}"></script></body>', 1)
    path.write_text(s, encoding='utf-8')


def main():
    count = 0
    if OUT.exists():
        for path in OUT.glob('*/index.html'):
            if path.parent.name != 'deals':
                patch(path)
                count += 1
    print(f'V13 review intelligence enabled: {count} product pages')


if __name__ == '__main__':
    main()

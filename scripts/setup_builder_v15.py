from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=ROOT/'index.html'
    s=p.read_text(encoding='utf-8')
    if 'setup-builder-v15.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/assets/css/setup-builder-v15.css"></head>',1)
    if 'setup-builder-v15.js' not in s:s=s.replace('</body>','<script src="/assets/js/setup-builder-v15.js" defer></script></body>',1)
    if 'data-setup-builder' not in s:s=s.replace('</main>','<section class="gb-section"><div class="gb-container"><div data-setup-builder></div></div></section></main>',1)
    p.write_text(s,encoding='utf-8')
    print('V15 Build My Setup wired into homepage')
if __name__=='__main__':main()

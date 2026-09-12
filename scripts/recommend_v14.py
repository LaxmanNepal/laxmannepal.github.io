from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def patch(path):
    s=path.read_text(encoding='utf-8')
    if 'product-v14.css' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="/assets/css/product-v14.css"></head>',1)
    if 'product-recommend-v14.js' not in s:
        s=s.replace('</body>','<script src="/assets/js/product-recommend-v14.js" defer></script></body>',1)
    marker='<!-- V14_RECOMMENDER -->'
    if marker not in s:
        block=f'{marker}<section class="gb-section"><div class="gb-container"><div data-product-recommender></div></div></section>'
        s=s.replace('</main>',block+'</main>',1)
    path.write_text(s,encoding='utf-8')

def main():
    patched=0
    for p in [ROOT/'index.html']:
        if p.exists(): patch(p); patched+=1
    print(f'V14 recommendation shell patched: {patched} page(s)')
if __name__=='__main__': main()

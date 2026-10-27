"""Install the approved stacker video after a normal build/localization pass.

Existing localized pages retain their translations. The new video section is
explicitly English because the approved narration and transcript are English.
"""
from pathlib import Path
import html
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
BASE = 'https://www.lexygolift.com'
ROUTE = '/videos/electric-pallet-stacker/'
STEM = 'electric-pallet-stacker-60s-720p-20261027'
VIDEO = f'/assets/videos/{STEM}.mp4'
POSTER = f'/assets/videos/{STEM}.webp'
TITLE = 'Electric Pallet Stacker: Controls, Lift Assembly & Handling'
DESCRIPTION = 'Watch a 60-second electric pallet stacker product walkthrough covering the tiller controls, lifting assembly, pallet handling and warehouse selection criteria. English narration and captions; AI-generated demonstration.'
CSS_LINK = '<link rel="stylesheet" href="/assets/stacker-video.css?v=20261027-1">'
START, END = '<!-- stacker-video:start -->', '<!-- stacker-video:end -->'
CSS = '''.stacker-demo{padding:48px 0;background:#f3f6f8;scroll-margin-top:100px}.stacker-demo .shell{max-width:1100px}.stacker-demo h2,.stacker-watch h1{color:#182e3b;line-height:1.18;letter-spacing:-.02em}.stacker-demo h2{font-size:clamp(25px,3vw,38px);margin:8px 0 14px}.stacker-demo p{max-width:820px;line-height:1.7}.stacker-demo video,.stacker-watch video{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:contain;background:#101518;border-radius:8px}.stacker-demo video{margin:22px 0 14px}.stacker-demo .stacker-meta,.stacker-watch .stacker-meta{color:#506371;font-size:14px}.stacker-demo .stacker-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px}.catalog-main .stacker-demo{margin:22px 0;padding:24px;border:1px solid #dce4ea;border-radius:8px}.catalog-main .stacker-demo .shell{width:100%;padding:0}.catalog-main .stacker-demo h2{font-size:27px}.stacker-watch{padding:38px 0 64px}.stacker-watch>.shell{max-width:1100px}.stacker-watch h1{font-size:clamp(29px,4vw,46px);margin:14px 0 16px}.stacker-watch .stacker-lead{font-size:18px;line-height:1.7;max-width:900px}.stacker-watch video{margin:24px 0 12px}.stacker-watch h2{margin:30px 0 12px;font-size:26px}.stacker-watch p,.stacker-watch li{line-height:1.8}.stacker-watch .stacker-transcript{max-width:900px}.stacker-watch .stacker-chapters{padding-left:24px}.stacker-watch .stacker-chapters time{font-variant-numeric:tabular-nums;font-weight:700;margin-right:10px}.stacker-watch .stacker-links{display:flex;gap:16px;flex-wrap:wrap;margin:20px 0}.stacker-watch a:focus-visible,.stacker-demo a:focus-visible{outline:3px solid #f27a24;outline-offset:4px}@media(max-width:600px){.stacker-demo{padding:30px 0}.catalog-main .stacker-demo{padding:16px}.stacker-watch{padding-top:24px}.stacker-watch .stacker-lead{font-size:16px}}'''


def player():
    return f'<video controls playsinline preload="none" width="1280" height="720" poster="{POSTER}" aria-label="Electric pallet stacker product walkthrough with English narration"><source src="{VIDEO}" type="video/mp4">Your browser does not support HTML video. <a href="{VIDEO}">Download the 720p video</a>.</video>'


def block():
    return f'''{START}<section class="stacker-demo" id="stacker-video" lang="en" dir="ltr"><div class="shell"><p class="section-kicker">PRODUCT VIDEO · ENGLISH · 60 SECONDS</p><h2>See the Electric Pallet Stacker in Action</h2><p>Explore the tiller controls, visible lifting components and pallet handling sequence. Review load weight, lift height, pallet dimensions and aisle space when selecting a configuration.</p>{player()}<p class="stacker-meta">720p · English narration and captions · AI-generated product demonstration. Model specifications vary by configuration.</p><div class="stacker-actions"><a class="button button-primary" href="{ROUTE}" hreflang="en">Video details &amp; English transcript</a><a class="button button-light" href="/contact/?subject=Electric%20pallet%20stacker%20video">Discuss your requirements</a></div></div></section>{END}'''


def watch_page(transcript):
    from build_site import page
    chapters = [(0, '00:00', 'Product overview'), (8, '00:08', 'Tiller controls and body panel'), (18, '00:18', 'Lifting assembly close-ups'), (30, '00:30', 'Pallet handling'), (44, '00:44', 'Warehouse selection criteria'), (52, '00:52', 'Mast movement and configuration inquiry')]
    paragraphs = ''.join(f'<p>{html.escape(p)}</p>' for p in transcript.split('\n\n') if p.strip())
    body = f'''<article class="stacker-watch" lang="en"><div class="shell"><nav aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/products/electric-pallet-stackers/">Electric Pallet Stackers</a> / Product Video</nav><p class="section-kicker">PRODUCT WALKTHROUGH</p><h1>{html.escape(TITLE)}</h1><p class="stacker-lead">A closer look at an electric pallet stacker: its operating controls, visible lifting components and pallet handling sequence, followed by the questions to consider when selecting a configuration for your warehouse.</p>{player()}<p class="stacker-meta">60 seconds · 1280 × 720 · English narration and captions · Published 27 October 2026</p><p class="stacker-meta">AI-generated product demonstration. This video illustrates product features and handling concepts; it is not a measured performance test. Confirm the specifications of your selected model.</p><div class="stacker-links"><a class="button button-primary" href="/contact/?subject=Electric%20pallet%20stacker%20video">Request a configuration review</a><a class="button button-light" href="/products/electric-pallet-stackers/">Browse electric pallet stackers</a></div><h2>In this video</h2><ol class="stacker-chapters">{''.join(f'<li><time>{stamp}</time>{label}</li>' for _, stamp, label in chapters)}</ol><h2>What to check before selecting a stacker</h2><p>Share your load weight, required lift height, pallet dimensions and aisle space. These details help us review a suitable model and configuration without assuming that every stacker has the same specifications.</p><h2 id="transcript">English transcript</h2><div class="stacker-transcript">{paragraphs}</div><div class="stacker-links"><a href="{VIDEO}" download>Download video (720p MP4)</a><a href="/assets/videos/{STEM}.txt" download>Download transcript</a><a href="/assets/videos/{STEM}.srt" download>Download English captions</a></div></div></article>'''
    schema = {'@type':'VideoObject','@id':BASE+ROUTE+'#video','name':TITLE,'description':DESCRIPTION,'thumbnailUrl':[BASE+POSTER],'uploadDate':'2026-10-27T00:00:00+08:00','duration':'PT1M','inLanguage':'en','contentUrl':BASE+VIDEO,'url':BASE+ROUTE,'transcript':transcript,'publisher':{'@type':'Organization','name':'LEXYGO Material Handling Equipment','url':BASE},'hasPart':[{'@type':'Clip','name':label,'startOffset':offset,'endOffset':chapters[i+1][0] if i+1<len(chapters) else 60} for i,(offset,_,label) in enumerate(chapters)]}
    content = page(TITLE, DESCRIPTION, ROUTE, body, schema, 'products')
    content = content.replace('</head>', CSS_LINK+'</head>')
    content = re.sub(r'(<meta property="og:image" content=")[^"]+', r'\g<1>'+BASE+POSTER, content)
    return content


def install():
    media = DIST / 'assets' / 'videos'
    media.mkdir(parents=True, exist_ok=True)
    for ext in ['mp4','webp','txt','srt']:
        shutil.copy2(ROOT/'assets'/'videos'/f'{STEM}.{ext}', media/f'{STEM}.{ext}')
    (DIST/'assets'/'stacker-video.css').write_text(CSS, encoding='utf8')
    changed=[]
    homes=[DIST/'index.html']+[p/'index.html' for p in DIST.iterdir() if p.is_dir() and (p/'products'/'electric-pallet-stackers'/'index.html').exists()]
    categories=[DIST/'products'/'electric-pallet-stackers'/'index.html']+[p.parent/'products'/'electric-pallet-stackers'/'index.html' for p in homes[1:]]
    for path in homes+categories:
        if not path.exists():continue
        source=path.read_text(encoding='utf8')
        source=re.sub(re.escape(START)+'.*?'+re.escape(END),'',source,flags=re.S)
        if CSS_LINK not in source:source=source.replace('</head>',CSS_LINK+'</head>')
        marker='<div class="product-grid">' if path in categories else '<section class="home-section cases-section">'
        if marker not in source:raise RuntimeError(f'Missing insertion point in {path}')
        source=source.replace(marker,block()+marker,1)
        path.write_text(source,encoding='utf8');changed.append(str(path.relative_to(DIST)))
    target=DIST/ROUTE.strip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True)
    transcript=(media/f'{STEM}.txt').read_text(encoding='utf8').strip()
    target.write_text(watch_page(transcript),encoding='utf8')
    sitemap=DIST/'sitemap.xml';text=sitemap.read_text(encoding='utf8')
    if BASE+ROUTE not in text:text=text.replace('</urlset>',f'<url><loc>{BASE+ROUTE}</loc><lastmod>2026-10-27</lastmod></url>\n</urlset>')
    sitemap.write_text(text,encoding='utf8')
    llms=DIST/'llms.txt';text=llms.read_text(encoding='utf8');line=f'- [{TITLE}]({BASE+ROUTE}): English video, transcript, controls, lifting assembly and pallet handling. AI-generated demonstration.'
    if BASE+ROUTE not in text:llms.write_text(text+'\n## Product video\n'+line+'\n',encoding='utf8')
    print(f'Installed approved video on {len(changed)} existing pages plus {ROUTE}')


if __name__=='__main__':
    install()

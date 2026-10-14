# -*- coding: utf-8 -*-
# 產生 GitHub Pages 用的 PWA 資料夾
import os, sys, json, hashlib, subprocess, shutil
from PIL import Image, ImageDraw, ImageFilter

SRC = "/home/claude/rws1909/cards"
OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
shutil.rmtree(OUT, ignore_errors=True)
for d in ("cards", "thumbs", "icons"): os.makedirs(f"{OUT}/{d}")

def save(im, path, w, q):
    im = im.convert("RGB").resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(path, "JPEG", quality=q, optimize=True, progressive=True)

for i in range(78):
    im = Image.open(f"{SRC}/{i:02d}.jpg")
    save(im, f"{OUT}/cards/{i:02d}.jpg", 420, 80)
    save(im, f"{OUT}/thumbs/{i:02d}.jpg", 132, 72)

# App 圖示：暖米色底，愚者牌置中（落在 maskable 安全區內）
def icon(size, card_h_ratio=0.66):
    bg = Image.new("RGB", (size, size), "#f6f1e7")
    card = Image.open(f"{SRC}/00.jpg").convert("RGB")
    h = round(size * card_h_ratio); w = round(card.width * h / card.height)
    card = card.resize((w, h), Image.LANCZOS)
    x, y = (size - w) // 2, (size - h) // 2
    sh = Image.new("L", (size, size), 0); ImageDraw.Draw(sh).rectangle([x + size*0.01, y + size*0.015, x + w + size*0.01, y + h + size*0.015], fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(size * 0.012))
    bg.paste(Image.new("RGB", (size, size), "#8a7a63"), (0, 0), sh)
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=round(size * 0.02), fill=255)
    bg.paste(card, (x, y), m)
    return bg
icon(512).save(f"{OUT}/icons/icon-512.png", optimize=True)
icon(192).save(f"{OUT}/icons/icon-192.png", optimize=True)
icon(180, 0.74).save(f"{OUT}/icons/apple-touch-icon.png", optimize=True)

subprocess.run([sys.executable, "-I", f"{HERE}/build.py", f"{OUT}/index.html", "pwa"], check=True)

manifest = {
    "name": "塔羅講義・1909 原版偉特牌",
    "short_name": "塔羅講義",
    "description": "78 張 1909 原版偉特牌圖文對照講義，含愚者之旅與 Waite 原意。",
    "lang": "zh-Hant",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#f6f1e7",
    "theme_color": "#f6f1e7",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
json.dump(manifest, open(f"{OUT}/manifest.webmanifest", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

files = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png"] \
      + [f"cards/{i:02d}.jpg" for i in range(78)] + [f"thumbs/{i:02d}.jpg" for i in range(78)]
h = hashlib.sha256()
for f in files[1:]: h.update(open(f"{OUT}/{f}", "rb").read())
version = h.hexdigest()[:10]   # 內容一變，快取版本就跟著變，手機會自動更新

sw = f"""// 離線快取：第一次開啟時把整份講義存進手機，之後沒網路也能看
const CACHE = 'tarot-{version}';
const FILES = {json.dumps(files)};
self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
}});
self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
}});
self.addEventListener('fetch', e => {{
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request, {{ignoreSearch: true}}).then(hit => hit || fetch(e.request)));
}});
"""
open(f"{OUT}/sw.js", "w", encoding="utf-8").write(sw)
open(f"{OUT}/.nojekyll", "w").write("")
open(f"{OUT}/README.md", "w", encoding="utf-8").write(
"""# 塔羅講義・1909 原版偉特牌

78 張 1909 年原版 Rider–Waite–Smith 塔羅的圖文對照講義，可安裝成手機 App（PWA）、離線瀏覽。

- 牌面：Pamela Colman Smith 繪，1909「Roses & Lilies」版，取自 Wikimedia Commons，公有領域。
- Waite 原意：A. E. Waite《The Pictorial Key to the Tarot》(1910)，取自 Wikisource。

## 安裝到手機
- iPhone：用 Safari 打開網址 → 分享 → 加入主畫面
- Android：用 Chrome 打開網址 → 選單 → 安裝應用程式
""")
total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
print("version", version, "files", len(files), "total bytes", total)

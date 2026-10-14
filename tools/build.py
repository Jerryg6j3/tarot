# -*- coding: utf-8 -*-
import base64, io, sys, html, os
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from data_major import MAJOR
from data_minor import SUITS, MINOR

CARDS = "/home/claude/rws1909/cards"
OUT = sys.argv[1]
MODE = sys.argv[2] if len(sys.argv) > 2 else "inline"

def b64(path, width=None, q=80):
    im = Image.open(path).convert("RGB")
    if width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def dims(i, w):
    im = Image.open(f"{CARDS}/{i:02d}.jpg"); return w, round(im.height * w / im.width)
def img(i):
    return f"cards/{i:02d}.jpg" if MODE == "pwa" else b64(f"{CARDS}/{i:02d}.jpg", 420, 80)
def thumb(i):
    return f"thumbs/{i:02d}.jpg" if MODE == "pwa" else b64(f"{CARDS}/{i:02d}.jpg", 132, 72)

assert [c["id"] for c in MAJOR] == list(range(22))
assert [c["id"] for c in MINOR] == list(range(22, 78))
for c in MAJOR + MINOR:
    for k in ("zh", "en", "kw", "look", "up", "rev", "waite_up", "waite_rev"):
        assert c.get(k), (c["id"], k)

esc = html.escape
suit_of = {s["key"]: s for s in SUITS}

def kw_html(kws): return "".join(f'<span class="tag">{esc(k)}</span>' for k in kws)

def waite_block(c):
    d = f'<p class="diff"><b>差異：</b>{esc(c["diff"])}</p>' if c.get("diff") else ""
    return f'''<details class="waite"><summary>Waite 原意（1910）</summary>
<dl><dt>正位</dt><dd>{esc(c["waite_up"])}</dd><dt>逆位</dt><dd>{esc(c["waite_rev"])}</dd></dl>{d}</details>'''

def card_section(c, major):
    i = c["id"]
    if major:
        title = f'<span class="num">{c["num"]}</span> {esc(c["zh"])} <span class="en">{esc(c["en"])}</span>'
        look = "<ul>" + "".join(f"<li>{x}</li>" for x in c["look"]) + "</ul>"   # look items contain <b> markup we wrote
        apply = '<h4>應用舉例</h4><dl class="apply">' + "".join(
            f"<dt>{esc(a)}</dt><dd>{esc(b)}</dd>" for a, b in c["apply"]) + "</dl>"
        journey = f'<p class="journey"><b>愚者之旅：</b>{esc(c["journey"])}</p>'
    else:
        title = f'{esc(c["zh"])} <span class="en">{esc(c["en"])}</span>'
        look = f'<p>{esc(c["look"])}</p>'
        apply = journey = ""
    return f'''<article class="card" id="c{i}">
<figure><img src="{img(i)}" width="{dims(i,420)[0]}" height="{dims(i,420)[1]}" alt="{esc(c["en"])}（1909 原版）" decoding="async"></figure>
<div class="body">
<h3>{title}</h3>
<div class="tags">{kw_html(c["kw"])}</div>
<h4>讀圖重點</h4>{look}
<h4>現代牌義</h4>
<dl class="meaning"><dt class="up">正位</dt><dd>{esc(c["up"])}</dd><dt class="rev">逆位</dt><dd>{esc(c["rev"])}</dd></dl>
{apply}{journey}{waite_block(c)}
<a class="top" href="#overview">回到總覽 ↑</a>
</div></article>'''

def grid(cards):
    return '<div class="grid">' + "".join(
        f'<a href="#c{c["id"]}"><img src="{thumb(c["id"])}" width="{dims(c["id"],132)[0]}" height="{dims(c["id"],132)[1]}" alt=""><span>{esc(c["zh"])}</span></a>' for c in cards) + "</div>"

sections_html = []
sections_html.append('<section id="major"><h2>大阿爾克那 <small>Major Arcana · 22 張</small></h2>'
    '<p class="lead">人生的重大課題。0 號愚者是主角，1～21 號常被讀成他一路經歷的旅程，每七張一個階段：1～7 學習外在世界，8～14 轉向內在，15～21 試煉與完成。完整的故事請看<a href="#journey">「愚者之旅」</a>篇章。</p>'
    + "".join(card_section(c, True) for c in MAJOR) + "</section>")
for s in SUITS:
    cs = [c for c in MINOR if c["suit"] == s["key"]]
    sections_html.append(f'<section id="{s["key"]}"><h2>{s["zh"]} <small>{s["en"]} · {s["element"]}元素</small></h2>'
        f'<p class="lead">{esc(s["theme"])}</p>' + "".join(card_section(c, False) for c in cs) + "</section>")

overview = ('<section id="overview"><h2>總覽 <small>點牌面跳到解說</small></h2>'
    '<h3 class="grp">大阿爾克那</h3>' + grid(MAJOR) +
    "".join(f'<h3 class="grp">{s["zh"]}（{s["element"]}）</h3>' + grid([c for c in MINOR if c["suit"] == s["key"]]) for s in SUITS) +
    '<p class="draw"><button id="drawBtn" type="button">隨機抽一張練習</button></p></section>')

import re
import data_journey as J
NAME = {c["id"]: c["zh"] for c in MAJOR}
def links(t):  # [[n]] -> 連到大牌 n 的連結
    return re.sub(r"\[\[(\d+)\]\]", lambda m: f'<a class="cl" href="#c{m.group(1)}">{NAME[int(m.group(1))]}</a>', t)

def road(ids):
    return '<div class="road">' + "".join(
        f'<a href="#c{i}"><img src="{thumb(i)}" width="{dims(i,132)[0]}" height="{dims(i,132)[1]}" alt=""><span><b>{MAJOR[i]["num"]}</b> {esc(NAME[i])}</span></a>' for i in ids) + "</div>"

stages_html = "".join(
    f'<div class="stage"><h3><span class="badge">{s["rng"][0]}～{s["rng"][1]}</span>{esc(s["title"])}</h3>'
    f'<p class="sub">{esc(s["sub"])}</p>{road(range(s["rng"][0], s["rng"][1] + 1))}'
    + "".join(f"<p>{links(p)}</p>" for p in s["text"]) + "</div>" for s in J.STAGES)

journey = f'''<section id="journey">
<h2>愚者之旅 <small>The Fool's Journey</small></h2>
{"".join(f"<p>{p}</p>" for p in J.INTRO)}
<div class="note"><p>{esc(J.WAITE_NOTE)}</p></div>
<div class="stage depart"><h3><span class="badge">0</span>出發</h3>
<div class="depart-row"><a href="#c0"><img src="{thumb(0)}" width="{dims(0,132)[0]}" height="{dims(0,132)[1]}" alt="愚者"></a><p>{links(J.DEPART)}</p></div></div>
{stages_html}
<div class="stage"><h3><span class="badge">21→0</span>回到起點</h3>
<div class="depart-row"><a href="#c21"><img src="{thumb(21)}" width="{dims(21,132)[0]}" height="{dims(21,132)[1]}" alt="世界"></a><span class="arrow">→</span><a href="#c0"><img src="{thumb(0)}" width="{dims(0,132)[0]}" height="{dims(0,132)[1]}" alt="愚者"></a></div>
<p>{links(J.RETURN)}</p></div>
<h3 class="jh">小阿爾克那：旅途上的日常</h3>
{"".join(f"<p>{p}</p>" for p in J.MINOR_TEXT)}
<h3 class="jh">和「英雄旅程」的關係</h3>
<p>{esc(J.HERO)}</p>
<h3 class="jh">怎麼用在解牌上</h3>
<dl class="use">{"".join(f"<dt>{esc(a)}</dt><dd>{links(b)}</dd>" for a, b in J.USE)}</dl>
</section>'''

intro = '''<section id="intro">
<h2>怎麼使用這份講義</h2>
<p>每張牌都分成幾個部分：</p>
<ol>
<li><b>讀圖重點</b>：只寫原版牌面上看得到的東西。解牌時先看圖，牌義常常就藏在圖裡。</li>
<li><b>現代牌義</b>：目前主流塔羅書籍的常見讀法，分正位、逆位。這是主體。</li>
<li><b>應用舉例</b>（大牌）：放在工作、感情、建議裡大概怎麼讀。這只是舉例，實際解牌要看問題和牌陣。</li>
<li><b>Waite 原意</b>：可展開的補充欄。這是偉特牌設計者 A. E. Waite 在 1910 年《The Pictorial Key to the Tarot》中寫的占卜牌義（中譯），以及它和現代讀法的差異。</li>
</ol>
<div class="note">
<p><b>關於 Waite 原意</b>：Waite 的占卜牌義大多是沿用 18、19 世紀法國占卜書的關鍵詞清單，常常互相矛盾，跟 Pamela Colman Smith 畫的圖也不一定對得上。Waite 自己在書中也說，大牌的占卜牌義「極其人為、武斷」。現代讀法大多是從圖像、以及 Waite 書中描寫圖像象徵的章節發展出來的，所以兩者有時差很多。</p>
<p><b>關於宮廷牌</b>：Waite 時代會用宮廷牌代表特定外貌的人（例如「黑髮男子」「金髮女子」），現代讀法多半改讀成一種性格或狀態。</p>
</div>
</section>'''

sources = '''<footer id="sources">
<h2>來源</h2>
<ul>
<li><b>牌面</b>：1909 年原版 Rider–Waite–Smith 塔羅（「Roses &amp; Lilies」版），繪者 Pamela Colman Smith。收藏者 Saskia Jansen 的實體牌掃描，取自維基共享資源（Wikimedia Commons）分類「Rider-Waite tarot deck (Roses &amp; Lilies)」，標示為公有領域。</li>
<li><b>Waite 原意</b>：A. E. Waite，《The Pictorial Key to the Tarot》（1910），第三部 §2–3；取自維基文庫（Wikisource），中文為本講義翻譯。</li>
<li><b>現代牌義、讀圖說明、應用舉例</b>：依主流塔羅讀法整理撰寫，僅供學習參考。</li>
</ul>
</footer>'''

ids = [c["id"] for c in MAJOR + MINOR]
script = """<script>
(function(){
  var ids=%s, btn=document.getElementById('drawBtn');
  btn.addEventListener('click',function(){
    var i=ids[Math.floor(Math.random()*ids.length)], el=document.getElementById('c'+i);
    if(!el) return;
    var rev=Math.random()<0.5;
    document.querySelectorAll('.card.drawn').forEach(function(e){e.classList.remove('drawn','reversed')});
    el.classList.add('drawn'); if(rev) el.classList.add('reversed');
    el.scrollIntoView({behavior:'smooth',block:'start'});
    var t=el.querySelector('.drawnlabel'); if(!t){t=document.createElement('p');t.className='drawnlabel';el.prepend(t);}
    t.textContent='你抽到的是'+(rev?'「逆位」':'「正位」')+'。先別看解說，看著圖想一想它在說什麼。';
  });
})();
</script>""" % ids

css = """
:root{--bg:#f6f1e7;--paper:#fffdf8;--ink:#2b2622;--muted:#6f655b;--line:#e3d9c8;--accent:#9b3d2e;--accent2:#2f5d74;--tag:#efe5d3;--up:#2e6b45;--rev:#9b3d2e}
@media (prefers-color-scheme:dark){:root{--bg:#1c1a18;--paper:#262320;--ink:#ece6dc;--muted:#a99f93;--line:#3a352f;--accent:#e08a74;--accent2:#8cc0d8;--tag:#332e29;--up:#7cc596;--rev:#e08a74}}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:56px}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 -apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif}
header.hero{padding:40px 16px 24px;text-align:center}
header.hero h1{margin:0;font-family:"Songti TC","Noto Serif TC",serif;font-size:2rem;letter-spacing:.08em}
header.hero p{margin:.4em 0 0;color:var(--muted)}
nav{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);display:flex;gap:4px;overflow-x:auto;padding:8px 12px;justify-content:center}
nav a{flex:none;color:var(--ink);text-decoration:none;padding:4px 12px;border-radius:999px;font-size:.92rem;background:var(--tag)}
nav a:hover{background:var(--accent);color:#fff}
main{max-width:980px;margin:0 auto;padding:0 16px 48px}
section{margin-top:40px}
h2{font-family:"Songti TC","Noto Serif TC",serif;font-size:1.6rem;border-bottom:2px solid var(--accent);padding-bottom:6px;margin:0 0 12px}
h2 small{font-size:.9rem;color:var(--muted);font-weight:normal;margin-left:6px}
.lead{color:var(--muted)}
.note{background:var(--paper);border-left:4px solid var(--accent2);padding:4px 16px;border-radius:6px}
h3.grp{font-size:1rem;margin:20px 0 8px;color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(72px,1fr));gap:8px}
.grid a{text-decoration:none;color:var(--ink);text-align:center;font-size:.78rem;line-height:1.3}
.grid img{width:100%;height:auto;border-radius:4px;display:block;box-shadow:0 1px 3px rgba(0,0,0,.2);transition:transform .15s}
.grid a:hover img{transform:translateY(-3px)}
.draw{text-align:center;margin-top:20px}
.draw button{font:inherit;background:var(--accent);color:#fff;border:0;border-radius:999px;padding:10px 24px;cursor:pointer}
.card{display:grid;grid-template-columns:260px 1fr;gap:24px;background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:20px;margin:20px 0}
.card figure{margin:0}
.card figure img{width:100%;height:auto;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,.25);position:sticky;top:64px;transition:transform .4s}
.card.reversed figure img{transform:rotate(180deg)}
.card.drawn{outline:3px solid var(--accent)}
.drawnlabel{grid-column:1/-1;margin:0;background:var(--tag);padding:8px 12px;border-radius:8px;font-weight:600}
.card h3{margin:0;font-size:1.45rem;font-family:"Songti TC","Noto Serif TC",serif}
.card h3 .num{color:var(--accent);margin-right:4px}
.card h3 .en{font-size:.95rem;color:var(--muted);font-weight:normal;font-family:Georgia,serif;margin-left:6px}
.card h4{margin:18px 0 4px;font-size:.95rem;color:var(--accent2);letter-spacing:.05em}
.card ul{margin:0;padding-left:1.2em}
.card li{margin:4px 0}
.card p{margin:4px 0}
.tags{margin-top:6px}
.tag{display:inline-block;background:var(--tag);border-radius:999px;padding:0 10px;margin:4px 6px 0 0;font-size:.85rem}
dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:4px 12px}
dt{font-weight:700;white-space:nowrap}
dd{margin:0}
dt.up{color:var(--up)} dt.rev{color:var(--rev)}
.journey{margin-top:14px!important;font-size:.95rem;color:var(--muted)}
details.waite{margin-top:16px;border:1px dashed var(--line);border-radius:8px;padding:6px 12px;font-size:.92rem}
details.waite summary{cursor:pointer;color:var(--muted);font-weight:600}
details.waite dl{margin-top:8px}
.diff{margin-top:8px!important;color:var(--muted)}
a.top{display:inline-block;margin-top:14px;font-size:.85rem;color:var(--muted)}
#journey > p{max-width:46em}
.stage{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:16px 20px;margin:20px 0}
.stage h3{margin:0;font-family:"Songti TC","Noto Serif TC",serif;font-size:1.3rem;display:flex;align-items:center;gap:10px}
.badge{font-family:Georgia,serif;font-size:.85rem;background:var(--accent);color:#fff;border-radius:999px;padding:2px 10px;flex:none}
.stage .sub{color:var(--muted);margin:2px 0 12px;font-size:.92rem}
.road{display:grid;grid-template-columns:repeat(7,1fr);gap:8px;margin:8px 0 14px}
.road a{text-decoration:none;color:var(--ink);text-align:center;font-size:.78rem;line-height:1.3}
.road img,.depart-row img{width:100%;height:auto;border-radius:4px;display:block;box-shadow:0 1px 3px rgba(0,0,0,.2)}
.road b{color:var(--accent);font-family:Georgia,serif;font-weight:normal}
.depart-row{display:flex;gap:16px;align-items:center;margin-top:10px}
.depart-row a{flex:none;width:84px}
.depart-row p{margin:0}
.arrow{font-size:1.6rem;color:var(--accent)}
a.cl{color:var(--accent);font-weight:600;text-decoration:none;border-bottom:1px dotted var(--accent)}
h3.jh{font-family:"Songti TC","Noto Serif TC",serif;font-size:1.2rem;margin:28px 0 6px}
dl.use{grid-template-columns:1fr;gap:2px}
dl.use dt{margin-top:10px;color:var(--accent2)}
@media (max-width:680px){.road{gap:4px}.road span{font-size:.68rem}.stage{padding:14px}}
footer{max-width:980px;margin:0 auto;padding:0 16px 60px;color:var(--muted);font-size:.9rem}
footer h2{font-size:1.2rem}
@media (max-width:680px){
 .card{grid-template-columns:1fr;padding:16px;gap:12px}
 .card figure{max-width:240px;margin:0 auto}
 .card figure img{position:static}
 header.hero h1{font-size:1.6rem}
 nav{justify-content:flex-start}
}
"""

PWA_HEAD = """
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#f6f1e7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1c1a18" media="(prefers-color-scheme: dark)">
<link rel="icon" href="icons/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="塔羅講義">
<meta name="apple-mobile-web-app-status-bar-style" content="default">"""
PWA_SCRIPT = """<script>
if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}
</script>"""

page = f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>塔羅講義・1909 原版偉特牌</title>{PWA_HEAD if MODE == "pwa" else ""}<style>{css}</style></head><body>
<header class="hero"><h1>塔羅講義</h1><p>1909 年原版偉特牌（Rider–Waite–Smith）・78 張圖文對照</p></header>
<nav><a href="#intro">說明</a><a href="#overview">總覽</a><a href="#journey">愚者之旅</a><a href="#major">大阿爾克那</a><a href="#wands">權杖</a><a href="#cups">聖杯</a><a href="#swords">寶劍</a><a href="#pentacles">錢幣</a></nav>
<main>{intro}{overview}{journey}{"".join(sections_html)}</main>{sources}{script}{PWA_SCRIPT if MODE == "pwa" else ""}</body></html>"""

open(OUT, "w", encoding="utf-8").write(page)
print("bytes", len(page.encode()), "cards", len(MAJOR) + len(MINOR))

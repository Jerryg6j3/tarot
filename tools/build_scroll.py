# -*- coding: utf-8 -*-
# 產生「滑牌」頁面 scroll.html：一次一張牌、全螢幕，往下滑換下一張，隨機順序、無限循環。
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_major import MAJOR
from data_minor import MINOR

OUT = sys.argv[1]

cards = []
for c in MAJOR:
    cards.append({"i": c["id"], "zh": c["zh"], "en": c["en"], "n": c["num"], "kw": c["kw"], "up": c["up"]})
for c in MINOR:
    cards.append({"i": c["id"], "zh": c["zh"], "en": c["en"], "n": "", "kw": c["kw"], "up": c["up"]})
assert [c["i"] for c in cards] == list(range(78))
DATA = json.dumps(cards, ensure_ascii=False, separators=(",", ":"))

page = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>滑牌・塔羅</title>
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#16130f">
<link rel="icon" href="icons/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="塔羅講義">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<style>
:root{--bg:#16130f;--ink:#ece4d6;--muted:#a3988a;--tag:rgba(255,255,255,.08);--accent:#d9a57a}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;height:100%;background:var(--bg);color:var(--ink);overflow:hidden;
 font:16px/1.6 -apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif}
#feed{height:100dvh;overflow-y:auto;scroll-snap-type:y mandatory;overscroll-behavior:contain;scrollbar-width:none}
#feed::-webkit-scrollbar{display:none}
.slide{height:100dvh;scroll-snap-align:start;scroll-snap-stop:always;display:flex;flex-direction:column;
 align-items:center;justify-content:center;gap:14px;padding:calc(env(safe-area-inset-top) + 28px) 20px calc(env(safe-area-inset-bottom) + 28px);position:relative}
.slide::before{content:"";position:absolute;inset:0;background:var(--glow);opacity:.18;filter:blur(60px);pointer-events:none}
.card{position:relative;height:min(68dvh,calc((100vw - 56px) * 1.7));aspect-ratio:7/12;border-radius:10px;overflow:hidden;
 box-shadow:0 10px 40px rgba(0,0,0,.55);background:#2a241e;cursor:pointer;border:0;padding:0;display:block}
.card img{width:100%;height:100%;object-fit:cover;display:block;opacity:0;transition:opacity .5s}
.card img.on{opacity:1}
.card .more{position:absolute;inset:0;background:rgba(18,15,12,.88);color:var(--ink);padding:22px 20px;
 display:flex;flex-direction:column;justify-content:center;gap:10px;text-align:left;opacity:0;transition:opacity .3s;font-size:.98rem}
.card.open .more{opacity:1}
.more b{color:var(--accent);font-weight:600;font-size:.85rem;letter-spacing:.1em}
.cap{text-align:center;position:relative}
.cap h2{margin:0;font-family:"Songti TC","Noto Serif TC",serif;font-weight:600;font-size:1.35rem;letter-spacing:.06em}
.cap h2 small{font-family:Georgia,serif;color:var(--muted);font-weight:normal;font-size:.8rem;margin-left:8px;letter-spacing:0}
.tags{margin-top:6px;display:flex;gap:6px;justify-content:center;flex-wrap:wrap}
.tags span{background:var(--tag);border-radius:999px;padding:1px 10px;font-size:.8rem;color:var(--muted)}
#home{position:fixed;top:calc(env(safe-area-inset-top) + 10px);left:12px;z-index:3;color:var(--muted);text-decoration:none;
 font-size:.85rem;background:rgba(0,0,0,.35);padding:4px 12px;border-radius:999px;backdrop-filter:blur(6px)}
#hint{position:fixed;left:0;right:0;bottom:calc(env(safe-area-inset-bottom) + 10px);text-align:center;color:var(--muted);
 font-size:.82rem;pointer-events:none;transition:opacity 1.2s}
#hint.gone{opacity:0}
@media (prefers-reduced-motion:reduce){.card img,.card .more,#hint{transition:none}}
</style></head><body>
<a id="home" href="./">← 講義</a>
<main id="feed" aria-label="塔羅牌，往上滑看下一張"></main>
<p id="hint">手指往上滑，看下一張・點牌面看牌義</p>
<script>
const CARDS=__DATA__;
const feed=document.getElementById('feed'), hint=document.getElementById('hint');
// 每張牌背景微光的顏色，依花色區分（大牌金、權杖橘、聖杯藍、寶劍灰藍、錢幣綠）
const glow=i=>i<22?'#c9a24a':i<36?'#c8663a':i<50?'#3f74a8':i<64?'#7d8ea3':'#6f9a52';
let order=[], pos=0, made=0;
function shuffle(last){
  const a=[...Array(78).keys()];
  for(let k=a.length-1;k>0;k--){const j=Math.floor(Math.random()*(k+1));[a[k],a[j]]=[a[j],a[k]];}
  if(a[0]===last){[a[0],a[1]]=[a[1],a[0]];}   // 兩輪交界不連續出現同一張
  return a;
}
function next(){ if(pos>=order.length){order=shuffle(order[order.length-1]);pos=0;} return order[pos++]; }
const io=new IntersectionObserver(es=>es.forEach(e=>{
  if(!e.isIntersecting) return;
  const s=e.target, img=s.querySelector('img');
  if(!img.src){img.src=img.dataset.src;}
  // 預先載入下一張
  const n=s.nextElementSibling; if(n){const ni=n.querySelector('img'); if(!ni.src) ni.src=ni.dataset.src;}
  if(!s.nextElementSibling || !s.nextElementSibling.nextElementSibling || !s.nextElementSibling.nextElementSibling.nextElementSibling) add(10);
}),{root:feed,rootMargin:'100% 0px'});
function slide(i){
  const c=CARDS[i], s=document.createElement('section'); s.className='slide'; s.style.setProperty('--glow',glow(i));
  const num=c.n?c.n+' ':'';
  s.innerHTML=`<button class="card" type="button" aria-label="${c.zh}，點一下看牌義">
    <img alt="${c.en}" decoding="async" data-src="cards/${String(i).padStart(2,'0')}.jpg">
    <div class="more"><b>正位</b><div>${c.up}</div></div></button>
    <div class="cap"><h2>${num}${c.zh}<small>${c.en}</small></h2><div class="tags">${c.kw.map(k=>`<span>${k}</span>`).join('')}</div></div>`;
  const img=s.querySelector('img'); img.addEventListener('load',()=>img.classList.add('on'));
  s.querySelector('.card').addEventListener('click',e=>e.currentTarget.classList.toggle('open'));
  return s;
}
function add(n){
  for(let k=0;k<n;k++){const s=slide(next()); feed.appendChild(s); io.observe(s); made++;}
  // 頁面保持輕量：上方累積太多張時，移除最舊的，並補回捲動位置
  const max=60, extra=feed.children.length-max;
  if(extra>20){
    const h=feed.firstElementChild.offsetHeight;
    for(let k=0;k<20;k++){io.unobserve(feed.firstElementChild); feed.firstElementChild.remove();}
    feed.scrollTop-=20*h;
  }
}
add(6);
let hid=false; feed.addEventListener('scroll',()=>{ if(!hid && feed.scrollTop>40){hid=true;hint.classList.add('gone');} },{passive:true});
if('serviceWorker' in navigator){navigator.serviceWorker.register('sw.js').catch(()=>{});}
</script></body></html>
""".replace("__DATA__", DATA)

open(OUT, "w", encoding="utf-8").write(page)
print("scroll.html bytes", len(page.encode()))

# -*- coding: utf-8 -*-
# 產生「滑牌」頁面 scroll.html
#   模式：逐張（有名字，一次一張、會停在每張牌上） / 安靜（只有牌面，連續自由捲動，可停在任何位置）
#   順序：隨機（每輪 78 張洗牌，不連續重複） / 照順序（0 愚者 → 錢幣國王 → 回到愚者）
#   兩種設定可以自由組合，會記住上次的選擇；網址參數 ?mode=quiet|cards&order=seq|random 可直接指定
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
:root{--bg:#16130f;--ink:#ece4d6;--muted:#a3988a;--tag:rgba(255,255,255,.08);--accent:#d9a57a;--top:calc(env(safe-area-inset-top) + 10px)}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;height:100%;background:var(--bg);color:var(--ink);overflow:hidden;
 font:16px/1.6 -apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif}
#feed{position:relative;height:100dvh;overflow-y:auto;overflow-anchor:none;overscroll-behavior:contain;scrollbar-width:none}
#feed::-webkit-scrollbar{display:none}
.slide{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center}
.slide::before{content:"";position:absolute;inset:0;background:var(--glow);opacity:.18;filter:blur(60px);pointer-events:none}
.card{position:relative;aspect-ratio:420/708;border-radius:10px;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,.55);
 background:#2a241e;border:0;padding:0;display:block;color:inherit;font:inherit}
.card img{width:100%;height:100%;object-fit:cover;display:block;opacity:0;transition:opacity .5s}
.card img.on{opacity:1}

/* 逐張模式：一次一張，停在每張牌上 */
body.cards #feed{scroll-snap-type:y mandatory}
body.cards .slide{height:100dvh;scroll-snap-align:start;scroll-snap-stop:always;gap:14px;
 padding:calc(env(safe-area-inset-top) + 28px) 20px calc(env(safe-area-inset-bottom) + 28px)}
body.cards .card{height:min(68dvh,calc((100vw - 56px) * 1.69));cursor:pointer}
.card .more{position:absolute;inset:0;background:rgba(18,15,12,.88);padding:22px 20px;display:flex;flex-direction:column;
 justify-content:center;gap:10px;text-align:left;opacity:0;transition:opacity .3s;font-size:.98rem}
.card.open .more{opacity:1}
.more b{color:var(--accent);font-weight:600;font-size:.85rem;letter-spacing:.1em}
.cap{text-align:center;position:relative}
.cap h2{margin:0;font-family:"Songti TC","Noto Serif TC",serif;font-weight:600;font-size:1.35rem;letter-spacing:.06em}
.cap h2 small{font-family:Georgia,serif;color:var(--muted);font-weight:normal;font-size:.8rem;margin-left:8px;letter-spacing:0}
.tags{margin-top:6px;display:flex;gap:6px;justify-content:center;flex-wrap:wrap}
.tags span{background:var(--tag);border-radius:999px;padding:1px 10px;font-size:.8rem;color:var(--muted)}

/* 安靜模式：只有牌面，一張接一張，連續自由捲動 */
body.quiet #feed{scroll-snap-type:none;padding-top:calc(env(safe-area-inset-top) + 52px)}
body.quiet .slide{padding:10px 16px}
body.quiet .card{width:min(calc(100vw - 32px),460px);pointer-events:none}
body.quiet .cap,body.quiet .more{display:none}

/* 上方按鈕：低調，捲動時變淡 */
.pill{color:var(--muted);text-decoration:none;font:inherit;font-size:.85rem;background:rgba(0,0,0,.4);border:0;
 padding:4px 12px;border-radius:999px;backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);cursor:pointer}
#home{position:fixed;top:var(--top);left:12px;z-index:3}
#ctl{position:fixed;top:var(--top);right:12px;z-index:3;display:flex;gap:6px}
#home,#ctl{transition:opacity .4s}
body.moving #home,body.moving #ctl{opacity:.25}
#toast,#hint{position:fixed;left:0;right:0;text-align:center;color:var(--muted);font-size:.82rem;pointer-events:none;transition:opacity 1s}
#hint{bottom:calc(env(safe-area-inset-bottom) + 10px)}
#toast{top:calc(env(safe-area-inset-top) + 48px);opacity:0}
#toast span,#hint span{background:rgba(0,0,0,.55);padding:4px 12px;border-radius:999px;color:var(--ink)}
#toast.show{opacity:1;transition:opacity .2s}
#hint.gone{opacity:0}
@media (prefers-reduced-motion:reduce){.card img,.card .more,#hint,#toast,#home,#ctl{transition:none}}
</style></head><body class="cards">
<a id="home" class="pill" href="./">← 講義</a>
<div id="ctl"><button id="bMode" class="pill" type="button"></button><button id="bOrder" class="pill" type="button"></button></div>
<main id="feed" aria-label="塔羅牌，往上滑看下一張"></main>
<p id="toast"><span></span></p>
<p id="hint"><span></span></p>
<script>
const CARDS=__DATA__;
const feed=document.getElementById('feed'), hint=document.getElementById('hint'), toast=document.getElementById('toast');
const bMode=document.getElementById('bMode'), bOrder=document.getElementById('bOrder');
// 每張牌背景微光的顏色，依花色區分（大牌金、權杖橘、聖杯藍、寶劍灰藍、錢幣綠）
const glow=i=>i<22?'#c9a24a':i<36?'#c8663a':i<50?'#3f74a8':i<64?'#7d8ea3':'#6f9a52';

// ---- 設定：網址參數 > 上次的選擇 > 預設 ----
const store={get(k){try{return localStorage.getItem(k)}catch(e){return null}},set(k,v){try{localStorage.setItem(k,v)}catch(e){}}};
const qs=new URLSearchParams(location.search);
let mode=qs.get('mode')||store.get('tarot.scroll.mode')||'cards'; if(mode!=='quiet') mode='cards';
let ord=qs.get('order')||store.get('tarot.scroll.order')||'random'; if(ord!=='seq') ord='random';

// ---- 下一張牌 ----
let deck=[], pos=0, seq=0;
function shuffle(first,last){
  const a=[...Array(78).keys()].filter(x=>x!==first);
  for(let k=a.length-1;k>0;k--){const j=Math.floor(Math.random()*(k+1));[a[k],a[j]]=[a[j],a[k]];}
  if(first!=null) a.unshift(first); else if(a[0]===last){[a[0],a[1]]=[a[1],a[0]];}   // 兩輪交界不連續出現同一張
  return a;
}
function startFrom(id){ // 從某張牌開始（切換設定時，畫面留在原本那張）
  if(ord==='seq'){ seq=(id==null?0:id); }
  else { deck=shuffle(id,null); pos=0; }
}
function next(){
  if(ord==='seq'){ const r=seq; seq=(seq+1)%78; return r; }
  if(pos>=deck.length){ deck=shuffle(null,deck[deck.length-1]); pos=0; }
  return deck[pos++];
}

// ---- 畫面 ----
function slide(i){
  const c=CARDS[i], s=document.createElement('section'); s.className='slide'; s.dataset.id=i; s.style.setProperty('--glow',glow(i));
  const num=c.n?c.n+' ':'';
  s.innerHTML=`<button class="card" type="button" aria-label="${c.zh}，點一下看牌義">
    <img alt="${c.zh} ${c.en}" decoding="async" data-src="cards/${String(i).padStart(2,'0')}.jpg">
    <div class="more"><b>正位</b><div>${c.up}</div></div></button>
    <div class="cap"><h2>${num}${c.zh}<small>${c.en}</small></h2><div class="tags">${c.kw.map(k=>`<span>${k}</span>`).join('')}</div></div>`;
  const img=s.querySelector('img'); img.addEventListener('load',()=>img.classList.add('on'));
  s.querySelector('.card').addEventListener('click',e=>{ if(mode==='cards') e.currentTarget.classList.toggle('open'); });
  return s;
}
function add(n){ for(let k=0;k<n;k++) feed.appendChild(slide(next())); }
function geom(){ // 每張牌佔的高度都一樣
  const f=feed.firstElementChild; if(!f) return null;
  return {h:f.offsetHeight||1, top:f.offsetTop};
}
function current(){ const g=geom(); if(!g) return 0; return Math.max(0,Math.floor((feed.scrollTop-g.top+g.h*0.5)/g.h)); }
// 依捲動位置：載入目前附近的圖；快滑到底時，先在後面補 10 張
function tick(){
  const g=geom(); if(!g) return;
  const idx=current();
  for(let k=Math.max(0,idx-1);k<=idx+3;k++){const s=feed.children[k]; if(s){const im=s.querySelector('img'); if(!im.src) im.src=im.dataset.src;}}
  if(feed.children.length-idx<8) add(10);
}
// 頁面保持輕量：停下來的時候，才清掉上方太舊的牌，並補回捲動位置（不會打斷滑動）
let selfScroll=false;
function trim(){
  if(feed.children.length<=60) return;
  const idx=current(), n=idx-10; if(n<=0) return;   // 保留目前這張上方 10 張
  const anchor=feed.children[idx], rel=anchor.offsetTop-feed.scrollTop;   // 以畫面上這張牌為基準，清完後放回同一個位置
  for(let k=0;k<n;k++) feed.firstElementChild.remove();
  const want=anchor.offsetTop-rel;
  if(Math.abs(feed.scrollTop-want)>1){ selfScroll=true; feed.scrollTop=want; }
}
function render(keepId){
  document.body.className=mode;
  bMode.textContent=mode==='quiet'?'安靜・連續':'逐張・有名字';
  bOrder.textContent=ord==='seq'?'照順序':'隨機';
  bMode.setAttribute('aria-label','目前：'+bMode.textContent+'，點一下切換');
  bOrder.setAttribute('aria-label','目前：'+bOrder.textContent+'，點一下切換');
  hint.firstElementChild.textContent=mode==='quiet'?'慢慢往上滑，隨時可以停下來':'手指往上滑，看下一張・點牌面看牌義';
  hint.classList.remove('gone'); hidden=false;
  feed.replaceChildren(); startFrom(keepId); add(12); feed.scrollTop=0; tick();
}
let toastT;
function say(t){ toast.firstElementChild.textContent=t; toast.classList.add('show'); clearTimeout(toastT); toastT=setTimeout(()=>toast.classList.remove('show'),1400); }
function curId(){ const s=feed.children[current()]; return s?+s.dataset.id:null; }
bMode.addEventListener('click',()=>{ const id=curId(); mode=mode==='quiet'?'cards':'quiet'; store.set('tarot.scroll.mode',mode); render(id); say(mode==='quiet'?'安靜模式：只有牌面，連續捲動':'逐張模式：一次一張，有名字'); });
bOrder.addEventListener('click',()=>{ const id=curId(); ord=ord==='seq'?'random':'seq'; store.set('tarot.scroll.order',ord); render(id); say(ord==='seq'?'照順序：從這張往後依序':'隨機：從這張開始洗牌'); });

let hidden=false, idleT;
feed.addEventListener('scroll',()=>{
  if(selfScroll){ selfScroll=false; return; }   // 清理舊牌造成的位置調整，不算使用者在滑
  tick();
  if(!hidden && feed.scrollTop>40){hidden=true;hint.classList.add('gone');}
  document.body.classList.add('moving');
  clearTimeout(idleT); idleT=setTimeout(()=>{ document.body.classList.remove('moving'); trim(); tick(); },600);
},{passive:true});
addEventListener('resize',tick);
render(ord==='seq'?0:null);
if('serviceWorker' in navigator){navigator.serviceWorker.register('sw.js').catch(()=>{});}
</script></body></html>
""".replace("__DATA__", DATA)

open(OUT, "w", encoding="utf-8").write(page)
print("scroll.html bytes", len(page.encode()))

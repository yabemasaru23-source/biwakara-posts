# -*- coding: utf-8 -*-
"""菅井様に送る確認ページを作る。

   使い方:
     python gen_check.py 2026-10-01 2026-10-06 2026-10-19 2026-10-05
                         ↑作成日     ↑対象の始まり ↑終わり    ↑締め

   出力: 投稿サイト/check/<作成日>.html
   公開: https://yabemasaru23-source.github.io/biwakara-posts/check/<作成日>.html

   posts.json の各回の "ask"（菅井様への確認事項）だけを載せる。
   ask のない回は「確認済みの事実だけで書いた回」として末尾に一覧だけ出す。
   画面に管理用語（案A、d31 など）は出さない。
   菅井様は ○／×／修正 を選び、「回答をコピーする」で出た文面をメールに貼って返す。
"""
import datetime
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
WD = "月火水木金土日"


def jp(iso):
    d = datetime.date.fromisoformat(iso)
    return "%d月%d日（%s）" % (d.month, d.day, WD[d.weekday()])


def main():
    made, start, end, due = sys.argv[1:5]
    posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf-8"))
    st = json.loads(re.search(r'<script id="app-state" type="application/json">(.*?)</script>',
                              open(os.path.join(SITE, "index.html"), encoding="utf-8").read(), re.S).group(1))
    rows = []
    for i, d in enumerate(posts["days"]):
        for key, media, part, pickkey in ((d["id"], "X", "xv", "xPick"), ("i%02d" % (i + 1), "Instagram", "igv", "igPick")):
            date = st["dates"].get(key)
            if not date or not (start <= date <= end):
                continue
            if (st["items"].get(key) or {}).get("status") == "posted":
                continue
            pick = (st.get(pickkey) or {}).get(key, "A")
            text = next((v["text"] for v in d.get(part, []) if v["id"] == pick), d.get("x", ""))
            asks = d.get("ask", []) if media == "X" else [a for a in d.get("ask_ig", [])]
            rows.append(dict(date=date, media=media, theme=d["theme"], text=text, asks=asks))
    rows.sort(key=lambda r: (r["date"], r["media"]))
    need = [r for r in rows if r["asks"]]
    skip = [r for r in rows if not r["asks"]]

    n = 0
    blocks = []
    for r in need:
        items = []
        for a in r["asks"]:
            n += 1
            items.append(
                '<div class="q" data-n="%d"><div class="qt"><b>%d</b>%s</div>'
                '<div class="ch">'
                '<label><input type="radio" name="q%d" value="○">このままでよい</label>'
                '<label><input type="radio" name="q%d" value="×">載せない</label>'
                '<label><input type="radio" name="q%d" value="修正">直してほしい</label></div>'
                '<textarea name="c%d" placeholder="修正の内容・ひとこと（任意）"></textarea></div>'
                % (n, n, html.escape(a), n, n, n, n))
        blocks.append(
            '<section><h2>%s　%s「%s」</h2>'
            '<details><summary>投稿する文を見る</summary><pre>%s</pre></details>%s</section>'
            % (jp(r["date"]), r["media"], html.escape(r["theme"]), html.escape(r["text"]), "".join(items)))
    skiplist = "".join("<li>%s　%s「%s」</li>" % (jp(r["date"]), r["media"], html.escape(r["theme"])) for r in skip)

    page = """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>みんなのびわから基金 投稿のご確認（%(range)s）</title>
<style>
:root{--bg:#FAF6EC;--card:#fff;--ink:#2A2117;--sub:#7B6B55;--line:#E5DAC6;--c:#C8741B}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font-family:"Hiragino Sans","Yu Gothic UI",system-ui,sans-serif;line-height:1.8}
.w{max-width:760px;margin:0 auto;padding:24px 16px 80px}
h1{font-size:21px;margin:0 0 6px}.lead{color:var(--sub);font-size:14px}
.due{display:inline-block;background:var(--c);color:#fff;border-radius:999px;padding:4px 14px;font-weight:700;margin:10px 0}
section{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:16px 0}
h2{font-size:16px;margin:0 0 8px}summary{cursor:pointer;color:var(--sub);font-size:13px}
pre{white-space:pre-wrap;background:#F4EDDF;border-radius:10px;padding:12px;font-family:inherit;font-size:14px}
.q{border-top:1px dashed var(--line);padding-top:12px;margin-top:12px}
.qt b{display:inline-block;min-width:26px;height:26px;border-radius:50%%;background:var(--ink);color:#fff;
text-align:center;line-height:26px;margin-right:8px;font-size:13px}
.ch{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.ch label{border:1px solid var(--line);border-radius:999px;padding:6px 14px;font-size:14px;cursor:pointer;background:#fff}
.ch input{margin-right:6px}
textarea{width:100%%;min-height:52px;border:1px solid var(--line);border-radius:10px;padding:8px;font:inherit;font-size:14px}
.skip{font-size:14px;color:var(--sub)}.skip li{margin:2px 0}
button{background:var(--c);color:#fff;border:0;border-radius:999px;padding:12px 26px;font-size:16px;font-weight:700;cursor:pointer}
#out{display:none;width:100%%;min-height:160px;margin-top:12px}
.done{color:#2C6B48;font-weight:700;margin-left:10px}
</style></head><body><div class="w">
<h1>みんなのびわから基金　投稿のご確認</h1>
<div class="lead">対象：%(range)s に投稿する予定の分</div>
<div class="due">ご回答の締め：%(due)s</div>
<p class="lead">公式サイトやご回答済みの内容にない事実だけを抜き出しています。
各項目で「○／×／修正」を選び、いちばん下の「回答をコピーする」を押して、出てきた文面をメールに貼ってご返信ください。
×・修正の回は直してから出し、ご回答のない回は出さずに後ろへ回します。%(note)s</p>
%(blocks)s
<section><h2>確認済みの事実だけで書いた回（ご確認は不要です）</h2><ul class="skip">%(skip)s</ul></section>
<section><button id="copy">回答をコピーする</button><span class="done" id="ok"></span>
<textarea id="out" readonly></textarea></section>
</div>
<script>
(function(){
  var KEY='biwakara-check-%(made)s', f=document.body;
  function save(){ var o={}; document.querySelectorAll('input:checked,textarea[name]').forEach(function(e){o[e.name]=e.value;});
    try{localStorage.setItem(KEY,JSON.stringify(o));}catch(e){} }
  try{ var o=JSON.parse(localStorage.getItem(KEY)||'{}');
    Object.keys(o).forEach(function(k){ var r=document.querySelector('input[name="'+k+'"][value="'+o[k]+'"]');
      if(r) r.checked=true; var t=document.querySelector('textarea[name="'+k+'"]'); if(t) t.value=o[k]; }); }catch(e){}
  f.addEventListener('change',save); f.addEventListener('input',save);
  document.getElementById('copy').addEventListener('click',function(){
    var L=['みんなのびわから基金 投稿のご確認（%(range)s）への回答'];
    document.querySelectorAll('.q').forEach(function(q){
      var n=q.getAttribute('data-n'), r=q.querySelector('input:checked'), c=q.querySelector('textarea').value.trim();
      L.push(n+'  '+(r?r.value:'未回答')+(c?'　'+c:''));});
    var t=L.join('\\n'), out=document.getElementById('out'); out.value=t; out.style.display='block'; out.select();
    var ok=document.getElementById('ok');
    (navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){ok.textContent='コピーしました。メールに貼ってご返信ください';},
      function(){try{document.execCommand('copy');ok.textContent='コピーしました。メールに貼ってご返信ください';}catch(e){ok.textContent='下の文面を選んでコピーしてください';}});
  });
})();
</script></body></html>""" % dict(range="%s〜%s" % (jp(start), jp(end)), due=jp(due), made=made,
                                  blocks="".join(blocks), skip=skiplist,
                                  note=("<br>（初回のため、締めを少し長めにしております）" if made == "2026-10-01" else ""))
    outdir = os.path.join(SITE, "check")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "%s.html" % made)
    open(out, "w", encoding="utf-8").write(page)
    print("確認ページ: check/%s.html　確認項目 %d件（%d回）／確認不要 %d回" % (made, n, len(need), len(skip)))
    for r in need:
        print("  要確認 %s %s %s（%d件）" % (r["date"], r["media"], r["theme"], len(r["asks"])))
    for r in skip:
        print("  不要   %s %s %s" % (r["date"], r["media"], r["theme"]))


if __name__ == "__main__":
    main()

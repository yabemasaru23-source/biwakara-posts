# -*- coding: utf-8 -*-
"""画像だけを一覧する軽いページ（images.html）を作る。
   スマホから開いて、その日の4枚をすぐ保存できるようにするためのもの。
   data URI を使わず images/ の実ファイルを直接参照するので軽い。"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)

HEAD = """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>みんなのびわから基金 投稿画像</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap">
<style>
:root{--bg:#FAF6EC;--surface:#fff;--ink:#2A2117;--ink2:#7B6B55;--line:#E5DAC6;--c:#E2892B;
  --shadow:0 2px 4px rgba(60,40,15,.06),0 10px 26px rgba(60,40,15,.08)}
@media(prefers-color-scheme:dark){:root{--bg:#16130E;--surface:#211C14;--ink:#F4EEE1;
  --ink2:#AC9C85;--line:#3A3124;--c:#F0A755;
  --shadow:0 2px 4px rgba(0,0,0,.3),0 10px 26px rgba(0,0,0,.3)}}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);
  font-family:"Zen Kaku Gothic New","Hiragino Sans",system-ui,sans-serif;line-height:1.7}
.wrap{max-width:760px;margin:0 auto;padding:22px 16px 70px;display:flex;flex-direction:column;gap:26px}
h1{font-family:"Shippori Mincho",serif;font-size:24px;font-weight:700}
.lead{color:var(--ink2);font-size:13.5px}
.how{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  padding:14px 17px;font-size:13px;color:var(--ink2);box-shadow:var(--shadow)}
.how b{color:var(--c)}
section{display:flex;flex-direction:column;gap:12px}
h2{font-family:"Shippori Mincho",serif;font-size:18px;font-weight:700;
  display:flex;align-items:center;gap:9px;flex-wrap:wrap}
h2 em{font-style:normal;font-size:12.5px;color:var(--ink2);font-weight:500}
.row{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}
.row.one{grid-template-columns:repeat(2,1fr);max-width:380px}
figure{display:flex;flex-direction:column;gap:5px}
figure a{display:block;border-radius:11px;overflow:hidden;box-shadow:var(--shadow);
  border:2px solid transparent}
figure a:hover{border-color:var(--c)}
figure img{width:100%;aspect-ratio:1;object-fit:cover;display:block}
figcaption{font-size:11px;color:var(--ink2);text-align:center;font-weight:700}
footer{border-top:1px solid var(--line);padding-top:18px;color:var(--ink2);font-size:12px}
footer a{color:var(--c)}
@media(max-width:520px){.row{gap:7px}h1{font-size:21px}}
</style></head><body><div class="wrap">
<h1>投稿画像 一覧</h1>
<p class="lead">みんなのびわから基金プロジェクト ／ 投稿に使う画像をここにまとめています。</p>
<div class="how"><b>保存のしかた</b>　画像を長押し（PCは右クリック）して保存します。
Instagramのカルーセルは、<b>1→4の順に1枚ずつ</b>保存してください。
カメラロールが保存した順に並ぶので、投稿時に順番がずれません。
Instagramの複数選択では、タップした順に番号が付きます。</div>
"""

TAIL = """<footer>
<p>投稿デスク（承認・数字の記録）は <a href="./">こちら</a></p>
<p>すべて 1080×1080（表紙帯は 1720×430）。投稿にそのまま使えます。</p>
</footer></div></body></html>"""


def fig(name, cap):
    return ('<figure><a href="images/%s.jpg" target="_blank" rel="noopener">'
            '<img src="images/%s.jpg" alt="" loading="lazy"></a>'
            '<figcaption>%s</figcaption></figure>' % (name, name, cap))


def main():
    posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf-8"))
    out = [HEAD]

    out.append('<section><h2>Instagram <em>4枚のカルーセル。1→4の順に保存</em></h2></section>')
    for i, d in enumerate(posts["days"]):
        keys = [d["id"]] + ["%s_%d" % (d["id"], j + 2)
                            for j in range(len(d.get("igslides", [])))]
        keys = [k for k in keys if os.path.exists(os.path.join(SITE, "images", k + ".jpg"))]
        if not keys:
            continue
        out.append('<section><h2>第%d回　%s<em>%s</em></h2><div class="row">%s</div></section>'
                   % (i + 1, d["theme"], d["cap"],
                      "".join(fig(k, "%d / %d" % (n + 1, len(keys))) for n, k in enumerate(keys))))

    xs = [(d["id"], "第%d回 %s" % (i + 1, d["theme"])) for i, d in enumerate(posts["days"])]
    out.append('<section><h2>X <em>1投稿につき1枚（Instagramの表紙と同じもの）</em></h2>'
               '<div class="row">%s</div></section>'
               % "".join(fig(k, c.split(" ")[1]) for k, c in xs))

    out.append('<section><h2>一発目の3案</h2><div class="row one">%s</div></section>'
               % "".join(fig("L" + d["id"], "案" + d["id"]) for d in posts["launch"]))
    out.append('<section><h2>24時間テレビ連動</h2><div class="row">%s</div></section>'
               % "".join(fig(p["id"], "%d 本目" % p["n"]) for p in posts["series"]))

    out.append(TAIL)
    dest = os.path.join(SITE, "images.html")
    open(dest, "w", encoding="utf-8").write("\n".join(out))
    print("built", dest, round(len("\n".join(out)) / 1024), "KB")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""投稿カード画像を Chrome headless で生成する。
   びわから基金 公式サイト（https://biwa.site/）の実写素材に、
   びわの5色をかぶせてキャッチを載せる。

   - days   : 1080x1080
   - launch : 1080x1080（一発目3案）
   - series : 1080x1080（24時間テレビ連動4本）
   - hero   : 1720x430（ページ上部の帯）

   使わない素材（意図的に除外）:
     story_yakei / story_onsen / furo01 … 温泉の原体験は理事長の最終確認が必要な題材
     work_003                          … 利用者の顔が写っており、SNSでの二次利用の同意範囲が不明
     nakigao01                         … 同情訴求に読まれうる

   素材は src/ に置く（fetch_src.py で公式サイトのリポジトリから取得）。
"""
import base64, io, json, os, subprocess
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
OUT = os.path.join(os.path.dirname(HERE), "images")
TMP = os.path.join(HERE, "_tmp")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

PALETTE = [
    dict(c="#E2892B", deep="#6E3907"),   # びわの実
    dict(c="#3F8F63", deep="#123322"),   # 葉
    dict(c="#2C6AA0", deep="#0B2440"),   # 長崎の海・出島
    dict(c="#D8A00C", deep="#553E00"),   # 山吹
    dict(c="#C4564A", deep="#4A130F"),   # 土
]
CREAM = "#FFF9EF"

# どの写真をどこに使うか
PHOTO = {
    "hero": "farm01.jpg",
    "LA": "facility01.jpg", "LB": "farm01.jpg", "LC": "biwa02.jpeg",
    "s1": "work_001.jpg", "s2": "work_002.jpg", "s3": "work_005.jpg", "s4": "farm01.jpg",
    "d01": "facility01.jpg",  # 3本柱＝住まい
    "d02": "work01.jpg",      # びわ茶＝葉の手元
    "d03": "biwa02.jpeg",     # 名前の由来＝長崎の風景
    "d04": "work_004.jpg",    # 農福連携＝畑
    "d05": "ikeda001.png",    # 支援の考え方＝理事長
    "d06": "biwa01.jpeg",     # いまの余白＝ゆとりのある風景
    "d07": "work_002.jpg",    # 仕事の選択肢＝加工場
    "d08": "jam01.jpg",       # 産学連携＝商品
    "d09": "work_005.jpg",    # 寄付の設計＝現場
    "d10": "farm01.jpg",      # これから＝畑
}

TPL = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{position:relative;background:{deep};
  font-family:"Zen Kaku Gothic New","Yu Gothic UI",sans-serif;color:{cream}}}
.photo{{position:absolute;inset:0;background-image:url({img});
  background-size:cover;background-position:{pos}}}
.scrim{{position:absolute;inset:0;background:
  linear-gradient(180deg,{c}3D 0%,{deep}88 42%,{deep}F2 100%)}}
.wrap{{position:absolute;inset:0;padding:{pad}px;display:flex;flex-direction:column}}
.top{{display:flex;align-items:center;gap:16px}}
.badge{{font-family:"Shippori Mincho",serif;font-weight:700;font-size:{bs}px;
  background:{cream};color:{deep};border-radius:999px;padding:{bp}px {bp2}px;letter-spacing:.08em}}
.acct{{font-size:{as_}px;font-weight:500;letter-spacing:.05em;opacity:.9;
  text-shadow:0 1px 6px {deep}}}
.mid{{flex:1;display:flex;align-items:flex-end}}
.theme{{font-size:{ts}px;font-weight:700;letter-spacing:.14em;margin-bottom:{tm}px;
  color:{c};text-shadow:0 1px 8px {deep}}}
h1{{font-family:"Shippori Mincho",serif;font-weight:700;
  font-size:{size}px;line-height:1.42;letter-spacing:.02em;text-wrap:balance;
  text-shadow:0 2px 18px {deep}}}
.sub{{font-size:{ss}px;font-weight:500;opacity:.95;margin-top:{sm}px;line-height:1.7;
  text-shadow:0 1px 10px {deep}}}
.bot{{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;
  margin-top:{bm}px}}
.org{{font-family:"Shippori Mincho",serif;font-size:{os}px;font-weight:600;line-height:1.5;
  text-shadow:0 1px 8px {deep}}}
.org small{{display:block;font-family:"Zen Kaku Gothic New",sans-serif;
  font-size:{oss}px;font-weight:500;opacity:.8;letter-spacing:.06em;margin-top:6px}}
.num{{font-family:"Shippori Mincho",serif;font-size:{ns}px;font-weight:700;opacity:.55;
  line-height:.85;white-space:nowrap;text-shadow:0 1px 8px {deep}}}
</style></head><body>
<div class="photo"></div><div class="scrim"></div>
<div class="wrap">
  <div class="top"><span class="badge">びわから基金</span><span class="acct">@biwakara_fund</span></div>
  <div class="mid"><div><div class="theme">{theme}</div><h1>{cap}</h1>{sub}</div></div>
  <div class="bot">
    <div class="org">社会福祉法人 出島福祉村<small>長崎 ／ びわから基金プロジェクト</small></div>
    <div class="num">{num}</div>
  </div>
</div></body></html>"""

SQ = dict(W=1080, H=1080, pad=76, bs=25, bp=7, bp2=22, as_=23, ts=26, tm=20,
          ss=25, sm=18, bm=52, os=26, oss=19, ns=58, pos="center")
HERO = dict(W=1720, H=430, pad=44, bs=21, bp=5, bp2=18, as_=19, ts=19, tm=10,
            ss=21, sm=12, bm=26, os=20, oss=15, ns=36, pos="center 62%")


def photo_uri(name, w, h):
    """素材を目的の比率に切り出して data URI にする。"""
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    sr, dr = im.width / im.height, w / h
    if sr > dr:                                  # 横に長い → 左右を切る
        nw = int(im.height * dr)
        x = (im.width - nw) // 2
        im = im.crop((x, 0, x + nw, im.height))
    else:                                        # 縦に長い → 上下を切る（やや上寄せ）
        nh = int(im.width / dr)
        y = int((im.height - nh) * 0.28)
        im = im.crop((0, y, im.width, y + nh))
    im = im.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def render(name, cfg, p, theme, cap, num, sub=""):
    n = len(cap)
    size = cfg["W"] // (9 if n <= 11 else (11 if n <= 15 else 14))
    if cfg is HERO:
        size = 62
    html = TPL.format(c=p["c"], deep=p["deep"], cream=CREAM, theme=theme, cap=cap, num=num,
                      img=photo_uri(PHOTO[name], cfg["W"], cfg["H"]),
                      sub=('<div class="sub">%s</div>' % sub) if sub else "",
                      size=size, **cfg)
    src = os.path.join(TMP, name + ".html")
    open(src, "w", encoding="utf-8").write(html)
    png = os.path.join(TMP, name + ".png")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--virtual-time-budget=9000",
                    "--window-size=%d,%d" % (cfg["W"], cfg["H"]),
                    "--screenshot=" + png, "file:///" + src.replace("\\", "/")],
                   check=True, capture_output=True)
    # 投稿用は JPEG（写真入りを PNG にすると1枚1.5MBを超えるため）
    jpg = os.path.join(OUT, name + ".jpg")
    Image.open(png).convert("RGB").save(jpg, "JPEG", quality=90)
    return jpg


LAUNCH = [("A", "はじめまして", "はじめまして。"),
          ("B", "宣言する",     "日本から、なくす。"),
          ("C", "問いかける",   "もしも、を考える。")]
SERIES = [("s1", "放送開始前",  "年に1度と、365日。"),
          ("s2", "放送中",      "感動の、前にあるもの。"),
          ("s3", "放送翌日",    "寄付だけが、方法ではない。"),
          ("s4", "放送1週間後", "あの1日で、終わらない。")]


def main():
    posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    for old in os.listdir(OUT):
        if old.endswith(".png"):
            os.remove(os.path.join(OUT, old))
    n = 0

    render("hero", HERO, PALETTE[0], "PROJECT", "びわから基金プロジェクト", "",
           sub="「親亡き後」の不安を、日本からなくす。長崎から、10,000人の応援団をつくります。")
    n += 1

    for i, (k, theme, cap) in enumerate(LAUNCH):
        render("L" + k, SQ, PALETTE[i % 5], theme, cap, "案 " + k)
        n += 1

    for i, (k, theme, cap) in enumerate(SERIES):
        render(k, SQ, PALETTE[(i + 2) % 5], theme, cap, str(i + 1) + " / 4")
        n += 1

    for i, d in enumerate(posts["days"]):
        render(d["id"], SQ, PALETTE[i % 5], d["theme"], d["cap"], "DAY %02d" % d["day"])
        n += 1

    print("generated", n, "images")


if __name__ == "__main__":
    main()

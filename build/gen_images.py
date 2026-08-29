# -*- coding: utf-8 -*-
"""投稿カード画像を Chrome headless で生成する。
   びわの5色パレットを回し、色面と実のかたちで組む。
   - days   : 1080x1080（posts.json の cap / theme から）
   - launch : 1080x1080（一発目3案）
   - series : 1080x1080（24時間テレビ連動4本）
   - hero   : 1720x760（ページ上部の帯）
   再実行すれば作り直せる。"""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "images")
TMP = os.path.join(HERE, "_tmp")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# びわの5色。solid=色面に載せる / cream=生成りに色で載せる
PALETTE = [
    dict(key="amber", c="#E2892B", deep="#8A4A0B", soft="#FCEBD3"),   # びわの実
    dict(key="leaf",  c="#3F8F63", deep="#17402A", soft="#DFEFE2"),   # 葉
    dict(key="sea",   c="#2C6AA0", deep="#0E2C4A", soft="#DCE9F4"),   # 長崎の海・出島
    dict(key="sun",   c="#E0A80C", deep="#6A4E00", soft="#FBF0CE"),   # 山吹
    dict(key="clay",  c="#C4564A", deep="#5C1913", soft="#F8E0DC"),   # 土・朱
]
CREAM = "#FFF9EF"

TPL = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{bg};position:relative;
  font-family:"Zen Kaku Gothic New","Yu Gothic UI",sans-serif;color:{fg}}}
svg.deco{{position:absolute;inset:0;width:{W}px;height:{H}px}}
.wrap{{position:absolute;inset:0;padding:{pad}px;display:flex;flex-direction:column}}
.top{{display:flex;align-items:center;gap:16px}}
.badge{{font-family:"Shippori Mincho",serif;font-weight:700;font-size:{bs}px;
  background:{fg};color:{bg};border-radius:999px;padding:{bp}px {bp2}px;letter-spacing:.08em}}
.acct{{font-size:{as_}px;font-weight:500;letter-spacing:.05em;opacity:.72}}
.mid{{flex:1;display:flex;align-items:center}}
.theme{{font-size:{ts}px;font-weight:700;letter-spacing:.14em;opacity:.72;margin-bottom:{tm}px}}
h1{{font-family:"Shippori Mincho",serif;font-weight:700;
  font-size:{size}px;line-height:1.42;letter-spacing:.02em;text-wrap:balance}}
.sub{{font-size:{ss}px;font-weight:500;opacity:.8;margin-top:{sm}px;line-height:1.7}}
.bot{{display:flex;align-items:flex-end;justify-content:space-between;gap:20px}}
.org{{font-family:"Shippori Mincho",serif;font-size:{os}px;font-weight:600;line-height:1.5}}
.org small{{display:block;font-family:"Zen Kaku Gothic New",sans-serif;
  font-size:{oss}px;font-weight:500;opacity:.72;letter-spacing:.06em;margin-top:6px}}
.num{{font-family:"Shippori Mincho",serif;font-size:{ns}px;font-weight:700;opacity:.34;
  line-height:.85;letter-spacing:.02em;white-space:nowrap}}
</style></head><body>
<svg class="deco" viewBox="0 0 {W} {H}" aria-hidden="true">{deco}</svg>
<div class="wrap">
  <div class="top"><span class="badge">びわから基金</span><span class="acct">@biwakara_fund</span></div>
  <div class="mid"><div><div class="theme">{theme}</div><h1>{cap}</h1>{sub}</div></div>
  <div class="bot">
    <div class="org">社会福祉法人 出島福祉村<small>長崎 ／ びわから基金プロジェクト</small></div>
    <div class="num">{num}</div>
  </div>
</div></body></html>"""


def fruit(cx, cy, r, fill, op, leaf_fill, leaf_op):
    """びわの実（丸）と、そこから伸びる葉。"""
    c = '<circle cx="{}" cy="{}" r="{}" fill="{}" opacity="{}"/>'.format(
        cx, cy, r, fill, op)
    d = "M {} {} Q {} {} {} {} Q {} {} {} {} Z".format(
        cx, cy - r,
        cx + int(r * 1.05), cy - int(r * 1.95),
        cx + int(r * 0.18), cy - int(r * 1.55),
        cx - int(r * 0.12), cy - int(r * 1.18),
        cx, cy - r)
    leaf = '<path d="{}" fill="{}" opacity="{}"/>'.format(d, leaf_fill, leaf_op)
    return c + leaf


def deco_for(i, W, H, p, solid):
    """3種のレイアウトを回して単調さを避ける。"""
    on = CREAM if solid else p["c"]
    kind = i % 3
    if kind == 0:
        return (fruit(int(W * .84), int(H * .80), int(W * .20), on, ".26", on, ".18")
                + '<circle cx="%d" cy="%d" r="%d" fill="%s" opacity=".13"/>'
                % (int(W * .97), int(H * .40), int(W * .12), on))
    if kind == 1:
        return ('<circle cx="%d" cy="%d" r="%d" fill="%s" opacity=".14"/>'
                % (int(W * .12), int(H * .16), int(W * .17), on)
                + fruit(int(W * .88), int(H * .86), int(W * .17), on, ".24", on, ".16")
                + '<circle cx="%d" cy="%d" r="%d" fill="%s" opacity=".10"/>'
                % (int(W * .70), int(H * .18), int(W * .09), on))
    return ('<path d="M%d %d L%d %d L%d %d Z" fill="%s" opacity=".12"/>'
            % (W, int(H * .30), W, H, int(W * .42), H, on)
            + fruit(int(W * .80), int(H * .74), int(W * .155), on, ".26", on, ".17"))


SQ = dict(W=1080, H=1080, pad=86, bs=25, bp=7, bp2=22, as_=23, ts=27, tm=24,
          ss=26, sm=20, os=28, oss=21, ns=74)
HERO = dict(W=1720, H=760, pad=84, bs=27, bp=8, bp2=26, as_=24, ts=28, tm=20,
            ss=30, sm=22, os=30, oss=22, ns=64)


def render(name, cfg, p, solid, i, theme, cap, num, sub=""):
    bg = p["c"] if solid else CREAM
    fg = CREAM if solid else p["deep"]
    n = len(cap)
    size = cfg["W"] // (9 if n <= 11 else (11 if n <= 15 else 14))
    if cfg is HERO:
        size = 108
    html = TPL.format(bg=bg, fg=fg, theme=theme, cap=cap, num=num,
                      sub=('<div class="sub">%s</div>' % sub) if sub else "",
                      size=size, deco=deco_for(i, cfg["W"], cfg["H"], p, solid), **cfg)
    src = os.path.join(TMP, name + ".html")
    open(src, "w", encoding="utf-8").write(html)
    png = os.path.join(OUT, name + ".png")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--virtual-time-budget=9000",
                    "--window-size=%d,%d" % (cfg["W"], cfg["H"]),
                    "--screenshot=" + png, "file:///" + src.replace("\\", "/")],
                   check=True, capture_output=True)
    return png


LAUNCH = {"A": ("はじめまして", "はじめまして。"),
          "B": ("宣言する",   "日本から、なくす。"),
          "C": ("問いかける", "もしも、を考える。")}
SERIES = {"s1": ("放送開始前",  "年に1度と、365日。"),
          "s2": ("放送中",      "感動の、前にあるもの。"),
          "s3": ("放送翌日",    "寄付だけが、方法ではない。"),
          "s4": ("放送1週間後", "あの1日で、終わらない。")}


def main():
    posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    n = 0

    render("hero", HERO, PALETTE[0], True, 0, "PROJECT",
           "びわから基金プロジェクト", "",
           sub="「親亡き後」の不安を、日本からなくす。長崎から、10,000人の応援団をつくります。")
    n += 1

    for i, (k, (theme, cap)) in enumerate(LAUNCH.items()):
        render("L" + k, SQ, PALETTE[i % 5], i % 2 == 0, i, theme, cap, "案 " + k)
        n += 1

    for i, (k, (theme, cap)) in enumerate(SERIES.items()):
        render(k, SQ, PALETTE[(i + 2) % 5], i % 2 == 1, i + 1, theme, cap, str(i + 1) + " / 4")
        n += 1

    for i, d in enumerate(posts["days"]):
        p = PALETTE[i % 5]
        render(d["id"], SQ, p, i % 2 == 0, i, d["theme"], d["cap"],
               "DAY %02d" % d["day"])
        n += 1

    print("generated", n, "images")


if __name__ == "__main__":
    main()

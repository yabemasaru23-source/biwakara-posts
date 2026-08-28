# -*- coding: utf-8 -*-
"""投稿カード画像（1080x1080）を Chrome headless で生成する。
   posts.json の days[].cap / tone から作る。再実行すれば作り直せる。"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "images")
TMP = os.path.join(HERE, "_tmp")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

TONES = {
    "amber": dict(bg="#F6E7CB", ink="#6E3A10", sub="#A5723C", fruit="#E7A644", leaf="#B9863C"),
    "leaf":  dict(bg="#E7EEE6", ink="#20443A", sub="#5A7C6E", fruit="#E7A644", leaf="#3C7A63"),
    "deep":  dict(bg="#1E3B32", ink="#F4F0E4", sub="#9DBAAE", fruit="#E7A644", leaf="#4E8C76"),
}

TPL = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1080px;overflow:hidden}}
body{{background:{bg};position:relative;
  font-family:"Zen Kaku Gothic New","Yu Gothic UI",sans-serif;color:{ink}}}
svg.deco{{position:absolute;inset:0;width:1080px;height:1080px}}
.wrap{{position:absolute;inset:0;padding:88px 92px;display:flex;flex-direction:column}}
.top{{display:flex;align-items:center;gap:18px}}
.badge{{font-family:"Shippori Mincho",serif;font-weight:700;font-size:26px;
  border:2px solid {ink};border-radius:999px;padding:6px 22px;letter-spacing:.06em}}
.acct{{font-size:24px;font-weight:500;letter-spacing:.04em;color:{sub}}}
.mid{{flex:1;display:flex;align-items:center}}
h1{{font-family:"Shippori Mincho",serif;font-weight:700;
  font-size:{size}px;line-height:1.45;letter-spacing:.02em;text-wrap:balance}}
.theme{{font-size:30px;font-weight:500;color:{sub};letter-spacing:.08em;margin-bottom:26px}}
.bot{{display:flex;align-items:flex-end;justify-content:space-between}}
.org{{font-family:"Shippori Mincho",serif;font-size:30px;font-weight:600;line-height:1.5}}
.org small{{display:block;font-family:"Zen Kaku Gothic New",sans-serif;
  font-size:22px;font-weight:500;color:{sub};letter-spacing:.06em;margin-top:6px}}
.day{{font-family:"Shippori Mincho",serif;font-size:22px;color:{sub};letter-spacing:.14em}}
</style></head><body>
<svg class="deco" viewBox="0 0 1080 1080" aria-hidden="true">
  <circle cx="905" cy="880" r="200" fill="{fruit}" opacity=".22"/>
  <circle cx="1010" cy="700" r="112" fill="{leaf}" opacity=".16"/>
  <path d="M690 1010 C760 900 900 860 1010 880 C940 1000 800 1050 690 1010 Z"
        fill="{leaf}" opacity=".14"/>
</svg>
<div class="wrap">
  <div class="top"><span class="badge">びわから基金</span><span class="acct">@biwakara_fund</span></div>
  <div class="mid"><div><div class="theme">{theme}</div><h1>{cap}</h1></div></div>
  <div class="bot">
    <div class="org">社会福祉法人 出島福祉村<small>長崎 ／ びわから基金</small></div>
    <div class="day">DAY {day:02d}</div>
  </div>
</div></body></html>"""


def main():
    posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    made = []
    for d in posts["days"]:
        t = TONES[d["tone"]]
        cap = d["cap"]
        size = 96 if len(cap) <= 11 else (84 if len(cap) <= 15 else 74)
        html = TPL.format(theme=d["theme"], cap=cap, day=d["day"], size=size, **t)
        src = os.path.join(TMP, d["id"] + ".html")
        open(src, "w", encoding="utf-8").write(html)
        png = os.path.join(OUT, d["id"] + ".png")
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1",
                        "--virtual-time-budget=9000",
                        "--window-size=1080,1080",
                        "--screenshot=" + png, "file:///" + src.replace("\\", "/")],
                       check=True, capture_output=True)
        made.append(png)
        print("ok", d["id"], os.path.getsize(png))
    print("generated", len(made))


if __name__ == "__main__":
    main()

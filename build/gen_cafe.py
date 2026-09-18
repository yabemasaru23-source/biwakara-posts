# -*- coding: utf-8 -*-
"""きずなカフェ・三和ゆめランドに渡す紹介用の画像を作る。

   読み手は「カフェのお客さま」であって、寄付を検討している人ではない。
   だから金額・申込み・お願いの言葉は入れない。
   「同じ法人が、こういうことを始めた」とだけ伝えて、あとはアカウントに任せる。

   出力（成果物/カフェ紹介/）:
     cafe_feed.jpg   1080x1080  Instagram・Xのフィード用
     cafe_story.jpg  1080x1920  ストーリーズ用
     cafe_card.png   1748x2480  店内に置く A6 カード（QR入り・300dpi）

   写真は check.photo() を通す。理事長の写真などは機械が弾く。
"""
import base64
import io
import os
import subprocess

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image

import check
import gen_images as G

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "成果物", "カフェ紹介")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

PHOTO = "jam01.jpg"        # びわジャム。カフェのお客さまに一番近い題材
IG_URL = "https://www.instagram.com/biwakara_fund/"
TONE = dict(c="#E2892B", deep="#6E3907")
CREAM = "#FFF9EF"

EYEBROW = "同じ法人の、新しい取り組み"
HEAD = "びわから、\n仕事が生まれました"
SUB = ("きずなカフェを運営している社会福祉法人 出島福祉村が、\n"
       "「みんなのびわから基金」を始めました。\n"
       "障害のある方とご家族が、この先も安心して暮らせるように。\n"
       "びわ茶づくりや畑のことを、SNSでお伝えしています。")
SUB_STORY = ("きずなカフェと同じ、\n出島福祉村の新しい取り組みです。\n\n"
             "障害のある方とご家族が、\nこの先も安心して暮らせるように。\n\n"
             "びわ茶づくりや畑のことを、\nSNSでお伝えしています。")
CARD_SUB = ("きずなカフェと同じ、出島福祉村の取り組みです。\n"
            "障害のある方とご家族が、この先も安心して暮らせるように。\n"
            "びわ茶づくりや畑のことを、日々お伝えしています。")

TPL = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{position:relative;background:{deep};
  font-family:"Zen Kaku Gothic New","Yu Gothic UI",sans-serif;color:{cream}}}
.photo{{position:absolute;inset:0;background-image:url({img});
  background-size:cover;background-position:center}}
.scrim{{position:absolute;inset:0;background:
  linear-gradient(180deg,{deep}A6 0%,{c}59 22%,{deep}B8 48%,{deep}F2 74%,{deep} 100%)}}
.wrap{{position:absolute;inset:0;padding:{pad}px;display:flex;flex-direction:column}}
.eyebrow{{font-size:{es}px;font-weight:700;letter-spacing:.16em;color:{cream};
  opacity:.92;text-shadow:0 1px 8px {deep}}}
.mid{{flex:1;display:flex;align-items:flex-end}}
h1{{font-family:"Shippori Mincho",serif;font-weight:700;
  font-size:{hs}px;line-height:1.38;letter-spacing:.02em;white-space:pre-line;
  text-shadow:0 2px 20px {deep}}}
.sub{{font-size:{ss}px;font-weight:500;line-height:1.85;margin-top:{sm}px;opacity:.95;
  white-space:pre-line;text-shadow:0 1px 10px {deep}}}
.bot{{margin-top:{bm}px;display:flex;align-items:flex-end;justify-content:space-between;gap:24px}}
.acct{{font-family:"Shippori Mincho",serif;font-size:{as_}px;font-weight:700;
  letter-spacing:.04em;text-shadow:0 1px 8px {deep}}}
.acct small{{display:block;font-family:"Zen Kaku Gothic New",sans-serif;
  font-size:{ass}px;font-weight:500;opacity:.82;letter-spacing:.05em;margin-top:8px}}
.org{{text-align:right;font-size:{os}px;font-weight:500;opacity:.8;line-height:1.7;
  text-shadow:0 1px 8px {deep}}}
</style></head><body>
<div class="photo"></div><div class="scrim"></div>
<div class="wrap">
  <div class="eyebrow">{eyebrow}</div>
  <div class="mid"><div><h1>{head}</h1><div class="sub">{sub}</div></div></div>
  <div class="bot">
    <div class="acct">@biwakara_fund<small>X ／ Instagram</small></div>
    <div class="org">社会福祉法人 出島福祉村<br>みんなのびわから基金</div>
  </div>
</div></body></html>"""

CARD_TPL = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1748px;height:2480px;overflow:hidden}}
body{{background:#FFF9EF;color:#2A2117;
  font-family:"Zen Kaku Gothic New","Yu Gothic UI",sans-serif;
  display:flex;flex-direction:column}}
.bar{{height:26px;background:#E2892B;flex:none}}
.photo{{height:1080px;flex:none;background-image:url({img});
  background-size:cover;background-position:center}}
.body{{flex:1;padding:78px 96px 0;display:flex;flex-direction:column}}
.eyebrow{{font-size:36px;font-weight:700;letter-spacing:.16em;color:#B06B14}}
h1{{font-family:"Shippori Mincho",serif;font-size:104px;font-weight:700;
  line-height:1.34;margin-top:26px;white-space:pre-line}}
.sub{{font-size:39px;line-height:2.0;margin-top:44px;color:#5B4C38;white-space:pre-line}}
.qrrow{{margin-top:auto;padding-bottom:84px;display:flex;align-items:center;gap:56px}}
.qr{{width:540px;height:540px;flex:none;box-shadow:0 6px 22px rgba(60,40,15,.16)}}
.qr img{{width:100%;height:100%;display:block}}
.qtxt{{flex:1}}
.qtxt b{{font-family:"Shippori Mincho",serif;font-size:54px;font-weight:700;display:block}}
.qtxt .h{{font-family:"Shippori Mincho",serif;font-size:46px;margin-top:16px;color:#B06B14}}
.qtxt small{{display:block;font-size:31px;color:#7B6B55;margin-top:20px;line-height:1.7}}
.org{{border-top:2px solid #E5DAC6;padding-top:32px;padding-bottom:34px;
  font-size:30px;color:#7B6B55;display:flex;justify-content:space-between}}
</style></head><body>
<div class="bar"></div>
<div class="photo"></div>
<div class="body">
  <div class="eyebrow">{eyebrow}</div>
  <h1>{head}</h1>
  <div class="sub">{sub}</div>
  <div class="qrrow">
    <div class="qr"><img src="{qr}"></div>
    <div class="qtxt">
      <b>SNSでお伝えしています</b>
      <div class="h">@biwakara_fund</div>
      <small>カメラを向けるとInstagramが開きます。<br>Xでも同じ名前で発信しています。</small>
    </div>
  </div>
  <div class="org"><span>社会福祉法人 出島福祉村</span><span>みんなのびわから基金</span></div>
</div>
</body></html>"""

FEED = dict(W=1080, H=1080, pad=82, es=25, hs=62, ss=27, sm=30, bm=46, as_=33, ass=19, os=21)
STORY = dict(W=1080, H=1920, pad=96, es=28, hs=74, ss=31, sm=38, bm=70, as_=38, ass=22, os=24)


def shoot(html, name, w, h, ext):
    """Chrome で1枚撮る。"""
    os.makedirs(G.TMP, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(G.TMP, name + ".html")
    open(src, "w", encoding="utf-8").write(html)
    png = os.path.join(G.TMP, name + ".png")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--virtual-time-budget=9000",
                    "--window-size=%d,%d" % (w, h), "--screenshot=" + png,
                    "file:///" + src.replace(os.sep, "/")],
                   check=True, capture_output=True)
    dest = os.path.join(OUT, name + "." + ext)
    im = Image.open(png).convert("RGB")
    if ext == "jpg":
        im.save(dest, "JPEG", quality=92)
    else:
        im.save(dest, "PNG")
    print("  %-14s %dx%d" % (name, w, h))


def qr_uri(px=840):
    """QRを data URI にする。誤り訂正はH、余白は規格どおり4セル。"""
    q = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=10, border=4)
    q.add_data(IG_URL)
    q.make(fit=True)
    im = q.make_image(fill_color="#2A2117", back_color=CREAM).convert("RGB")
    im = im.resize((px, px), Image.NEAREST)   # 拡大は最近傍。ぼかすと読めなくなる
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def render(name, cfg, sub):
    check.photo(PHOTO)                              # 使ってはいけない素材を止める
    check.image_text(name, [EYEBROW, HEAD, sub])    # 管理ラベルの混入を止める
    shoot(TPL.format(cream=CREAM, img=G.photo_uri(PHOTO, cfg["W"], cfg["H"]),
                     eyebrow=EYEBROW, head=HEAD, sub=sub, **TONE, **cfg),
          name, cfg["W"], cfg["H"], "jpg")


def render_card():
    check.photo(PHOTO)
    check.image_text("cafe_card", [EYEBROW, HEAD, CARD_SUB])
    shoot(CARD_TPL.format(img=G.photo_uri(PHOTO, 1748, 1080), qr=qr_uri(),
                          eyebrow=EYEBROW, head=HEAD, sub=CARD_SUB),
          "cafe_card", 1748, 2480, "png")


def main():
    render("cafe_feed", FEED, SUB)
    render("cafe_story", STORY, SUB_STORY)
    render_card()
    print("\n出力先:", OUT)


if __name__ == "__main__":
    main()

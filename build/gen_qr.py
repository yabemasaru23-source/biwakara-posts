# -*- coding: utf-8 -*-
"""みんなのびわから基金のSNS用QRコードを作る。

   印刷物にもスマホ表示にも耐えるよう、余白（クワイエットゾーン）を
   規格どおり4セル分とり、誤り訂正は H（30%まで復元可）にしている。
   ロゴは重ねない。中央を隠すと読めない端末が出るため。

   出力（成果物/QR/）:
     qr_x.png        X 単体（1200px）
     qr_instagram.png Instagram 単体（1200px）
     qr_both.png     2つ並べた配布用（名刺やチラシに貼る想定）
"""
import os
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "成果物", "QR")

INK = "#2A2117"        # 濃い茶。真っ黒より誌面になじむ
CREAM = "#FFF9EF"
ORANGE = "#E2892B"     # びわの実
INK2 = "#7B6B55"

SITES = [
    dict(key="x", label="X（旧Twitter）", handle="@biwakara_fund",
         url="https://x.com/biwakara_fund"),
    dict(key="instagram", label="Instagram", handle="@biwakara_fund",
         url="https://www.instagram.com/biwakara_fund/"),
]


def font(size, bold=True):
    for name in ("YuGothB.ttc" if bold else "YuGothR.ttc", "meiryob.ttc", "meiryo.ttc",
                 "msgothic.ttc", "arial.ttf"):
        p = os.path.join(r"C:\Windows\Fonts", name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def make_qr(url, px):
    """誤り訂正H・余白4セルでQRを作り、px 角に拡大する。"""
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    im = qr.make_image(fill_color=INK, back_color=CREAM).convert("RGB")
    # 拡大は最近傍で。ぼかすと読み取り率が落ちる
    return im.resize((px, px), Image.NEAREST), qr.version


def card(site, W=1200):
    """QR＋アカウント名の1枚。"""
    qr_px = int(W * 0.78)
    rows = ((site["handle"], font(62), INK),
            (site["label"], font(34, False), INK2),
            ("みんなのびわから基金", font(30, False), INK2))
    H = 74 + qr_px + 26 + sum(f.size + 14 for _, f, _ in rows) + 46
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 14], fill=ORANGE)
    q, ver = make_qr(site["url"], qr_px)
    im.paste(q, ((W - qr_px) // 2, 74))
    y = 74 + qr_px + 26
    for text, f, fill in rows:
        w = d.textbbox((0, 0), text, font=f)[2]
        d.text(((W - w) // 2, y), text, font=f, fill=fill)
        y += f.size + 14
    return im, ver


def both(W=1700, H=1020):
    """2つ並べた配布用。"""
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 16], fill=ORANGE)
    t, f = "みんなのびわから基金", font(58)
    d.text(((W - d.textbbox((0, 0), t, font=f)[2]) // 2, 62), t, font=f, fill=INK)
    t2, f2 = "長崎から、「親亡き後」の不安をなくす", font(32, False)
    d.text(((W - d.textbbox((0, 0), t2, font=f2)[2]) // 2, 140), t2, font=f2, fill=INK2)

    qr_px, gap = 600, 120
    x = (W - qr_px * 2 - gap) // 2
    for s in SITES:
        q, _ = make_qr(s["url"], qr_px)
        im.paste(q, (x, 235))
        y = 235 + qr_px + 22
        for text, f3, fill in ((s["handle"], font(46), INK),
                               (s["label"], font(30, False), INK2)):
            w = d.textbbox((0, 0), text, font=f3)[2]
            d.text((x + (qr_px - w) // 2, y), text, font=f3, fill=fill)
            y += f3.size + 12
        x += qr_px + gap
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    for s in SITES:
        im, ver = card(s)
        p = os.path.join(OUT, "qr_%s.png" % s["key"])
        im.save(p, "PNG")
        print("  %-18s version %-2d  %s" % (s["key"], ver, s["url"]))
    both().save(os.path.join(OUT, "qr_both.png"), "PNG")
    print("  %-18s 2つ並べた配布用" % "both")
    print("\n出力先:", OUT)


if __name__ == "__main__":
    main()

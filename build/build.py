# -*- coding: utf-8 -*-
"""template.html + posts.json + images/*.png から自己完結の index.html を組み立てる。"""
import base64, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
IMG = os.path.join(SITE, "images")

BASE_TAGS = ["びわから基金", "出島福祉村", "親亡き後", "長崎", "障害福祉",
             "地域福祉", "社会福祉法人", "ソーシャルグッド", "長崎モデル", "福祉"]


def main():
    posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf-8"))
    images = {}
    for d in posts["days"]:
        p = os.path.join(IMG, d["id"] + ".png")
        if os.path.exists(p):
            b = base64.b64encode(open(p, "rb").read()).decode("ascii")
            images[d["id"]] = "data:image/png;base64," + b

    data = {
        "launch": posts["launch"],
        "series": posts["series"],
        "days": posts["days"],
        "images": images,
        "baseTags": BASE_TAGS,
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    out = tpl.replace("__DATA__", blob)
    dest = os.path.join(SITE, "index.html")
    open(dest, "w", encoding="utf-8").write(out)
    print("built", dest, round(len(out.encode("utf-8")) / 1024), "KB",
          "/ images:", len(images))


if __name__ == "__main__":
    main()

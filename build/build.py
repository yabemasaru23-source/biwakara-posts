# -*- coding: utf-8 -*-
"""template.html + posts.json + images/*.png から自己完結の index.html を組み立てる。"""
import base64, hashlib, io, json, os, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
IMG = os.path.join(SITE, "images")

BASE_TAGS = ["びわから基金", "出島福祉村", "親亡き後", "長崎", "障害福祉",
             "地域福祉", "社会福祉法人", "ソーシャルグッド", "長崎モデル", "福祉"]


def main():
    posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf-8"))
    names = ["hero"] + ["L" + x["id"] for x in posts["launch"]]         + [x["id"] for x in posts["series"]] + [d["id"] for d in posts["days"]]
    images = {}
    for name in names:
        p = os.path.join(IMG, name + ".jpg")
        if not os.path.exists(p):
            continue
        # 寸法はそのまま、画質だけ落として埋め込む（投稿用の原寸は images/ に残る）
        buf = io.BytesIO()
        Image.open(p).convert("RGB").save(buf, "JPEG", quality=72, optimize=True)
        b = base64.b64encode(buf.getvalue()).decode("ascii")
        images[name] = "data:image/jpeg;base64," + b

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
    kept = carry_state(dest)
    if kept is None:
        kept = stamp({"chosen": None, "dates": {}, "igPick": {}, "items": {}})
    if kept:
        out = re.sub(
            r'(<script id="app-state" type="application/json">).*?(</script>)',
            lambda m: m.group(1) + kept + m.group(2), out, count=1, flags=re.S)

    open(dest, "w", encoding="utf-8").write(out)
    print("built", dest, round(len(out.encode("utf-8")) / 1024), "KB",
          "/ images:", len(images),
          "/ 引き継いだ承認・数字:", "あり" if kept else "なし")


def carry_state(dest):
    """既存 index.html に入っている承認状態・数字を引き継ぐ。
       これをしないと作り直すたびに皆の入力が消える。
       Artifact 側で更新されている場合は、先にそちらを取り込んでから実行すること。"""
    if not os.path.exists(dest):
        return None
    m = re.search(r'<script id="app-state" type="application/json">(.*?)</script>',
                  open(dest, encoding="utf-8").read(), re.S)
    if not m:
        return None
    try:
        st = json.loads(m.group(1))
    except ValueError:
        return None
    st.pop("tab", None)                       # タブは各自の表示状態なので持ち越さない
    items = st.get("items") or {}
    # 何も入っていない空レコードは捨てる（表示しただけで作られるため）
    st["items"] = {k: v for k, v in items.items()
                   if v.get("status", "none") != "none" or v.get("m") or
                   v.get("url") or v.get("x") is not None or v.get("ig") is not None}
    return stamp(st)


def stamp(st):
    """公開する状態に rev（内容のハッシュ）を付ける。
       中身が変われば rev も変わるので、閲覧者のブラウザに残った
       古い控えを捨てさせられる（GitHub Pages 版で必要）。"""
    st.pop("rev", None)
    body = json.dumps(st, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    st["rev"] = hashlib.md5(body.encode("utf-8")).hexdigest()[:10]
    return json.dumps(st, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


if __name__ == "__main__":
    main()

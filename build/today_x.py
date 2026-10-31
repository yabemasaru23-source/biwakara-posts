"""その日の X と Instagram の投稿の本文と画像を出す（見るだけ）。毎朝の投稿タスクで使う。

    python today_x.py              # 今日
    python today_x.py 2026-11-01   # 日付を指定

本文は投稿デスクで選んだ案（xPick）。選んでいなければ posts.json の x。
2026-10-31 本人「毎朝、その日の X 投稿の本文と画像を見せてください。私が一言許可したら投稿してください」。
"""
import datetime
import json
import os
import re
import sys

import check_deleted as c

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..")


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
    st = c.app_state(os.path.join(SITE, "index.html"))
    posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf-8"))
    keys = sorted(k for k, v in st.get("dates", {}).items()
                  if v == day and re.fullmatch(r"d\d+", k))
    if not keys:
        print("%s: X の予定なし" % day)
    for k in keys:
        o = c.find(posts, k) or {}
        pick = st.get("xPick", {}).get(k)
        text = next((v["text"] for v in o.get("xv", []) if v["id"] == pick), None) or o.get("x", "")
        img = os.path.normpath(os.path.join(SITE, "images", k + ".jpg"))
        done = st.get("items", {}).get(k, {}).get("status") == "posted"
        print("日付: %s" % day)
        print("回: %s「%s」%s" % (k, o.get("theme", "?"), "（投稿済み）" if done else ""))
        print("案: %s" % (pick or "A（未選択のため posts.json の x）"))
        print("文字数: %d" % len(text))
        print("画像: %s%s" % (img, "" if os.path.exists(img) else "（ファイルなし）"))
        print("check: %s" % ("；".join(o.get("check") or []) or "なし"))
        print("ask: %s" % ("；".join(o.get("ask") or []) or "なし"))
        print("---本文ここから---")
        print(text)
        print("---本文ここまで---")
    instagram(st, posts, day)


def instagram(st, posts, day):
    """Instagram（i27 なら d27 の igv・表紙・中身の画像）。表紙は igphoto があれば d27_c、なければ d27。"""
    keys = sorted(k for k, v in st.get("dates", {}).items()
                  if v == day and re.fullmatch(r"i\d+", k))
    if not keys:
        print("%s: Instagram の予定なし" % day)
    for k in keys:
        d = "d" + k[1:]
        o = c.find(posts, d) or {}
        pick = st.get("igPick", {}).get(k)
        text = next((v["text"] for v in o.get("igv", []) if v["id"] == (pick or "A")), "")
        names = [d + ("_c" if o.get("igphoto") else "")] + \
                ["%s_%d" % (d, j + 2) for j in range(len(o.get("igslides", [])))]
        imgs = [os.path.normpath(os.path.join(SITE, "images", n + ".jpg")) for n in names]
        done = st.get("items", {}).get(k, {}).get("status") == "posted"
        print("")
        print("[Instagram] 日付: %s" % day)
        print("回: %s「%s」%s" % (k, o.get("theme", "?"), "（投稿済み）" if done else ""))
        print("案: %s" % (pick or "A（未選択）"))
        for p in imgs:
            print("画像: %s%s" % (p, "" if os.path.exists(p) else "（ファイルなし）"))
        print("check: %s" % ("；".join(o.get("check") or []) or "なし"))
        print("ask: %s" % ("；".join(o.get("ask") or []) or "なし"))
        print("---キャプションここから---")
        print(text)
        print("---キャプションここまで---")


if __name__ == "__main__":
    main()

"""その日の X 投稿の本文と画像を出す（見るだけ）。毎朝の投稿タスクで使う。

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
        return
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


if __name__ == "__main__":
    main()

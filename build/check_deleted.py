"""記録上「投稿済み」の X 投稿が実際に残っているかを確かめる（見るだけ。記録は変えない）。

    python check_deleted.py

tweet-result が空応答か TweetTombstone なら「消えている」と出す。
"""
import json
import os
import re
import sys

import sync_posts as s

HERE = os.path.dirname(os.path.abspath(__file__))


def app_state(path):
    t = open(path, encoding="utf-8").read()
    m = re.search(r'<script id="app-state" type="application/json">(.*?)</script>', t, re.S)
    return json.loads(m.group(1))


def main():
    st = app_state(os.path.join(HERE, "..", "index.html"))
    gone, n = [], 0
    for key, v in st.get("items", {}).items():
        m = re.search(r"status/(\d+)", v.get("url", ""))
        if v.get("status") != "posted" or not m:
            continue
        n += 1
        try:
            raw = s.fetch("https://cdn.syndication.twimg.com/tweet-result?id=%s&lang=ja&token=a" % m.group(1))
        except Exception as e:  # 通信エラーは消滅と区別して出す
            print("取得できず", key, m.group(1), e)
            continue
        raw = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else (raw or "")
        if not raw.strip() or "TweetTombstone" in raw:
            gone.append((key, m.group(1)))
    print("確認した X 投稿: %d件" % n)
    for key, sid in gone:
        print("消えている:", key, "https://x.com/biwakara_fund/status/" + sid)
    print("食い違い: %d件" % len(gone))
    plan(st)


def find(o, key):
    if isinstance(o, dict):
        if o.get("id") == key or o.get("key") == key:
            return o
        o = list(o.values())
    if isinstance(o, list):
        for x in o:
            r = find(x, key)
            if r:
                return r
    return None


def plan(st):
    """今日と明日の予定を、posts.json の theme と check を添えて出す。"""
    import datetime
    posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf-8"))
    today = datetime.date.today()
    for label, day in (("今日", today), ("明日", today + datetime.timedelta(days=1))):
        keys = sorted(k for k, v in st.get("dates", {}).items()
                      if v == day.isoformat() and re.fullmatch(r"[di]\d+", k))
        if not keys:
            print("%s(%s): 予定なし" % (label, day))
        for k in keys:
            o = find(posts, k) or {}
            done = st.get("items", {}).get(k, {}).get("status") == "posted"
            print("%s(%s): %s「%s」%s / check: %s" % (
                label, day, k, o.get("theme", "?"), "（投稿済み）" if done else "",
                "；".join(o.get("check") or []) or "なし"))


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""投稿のURLを受け取らなくても、投稿済みの記録を埋められるようにする。

   使い方:
     python sync_posts.py --x 2102326955647639778 2101905728814587952
     python sync_posts.py --ig DdiZspGGM41
     python sync_posts.py --x <ID> --ig <shortcode> --write

   --write を付けるまで、何も書き換えない（先に結果を見てから決める）。

   なぜ ID を渡す形なのか:
     投稿1本ぶんの中身は、ログインなしで取れる。
       X         cdn.syndication.twimg.com の tweet-result（本文・投稿日時・いいね数）
       Instagram 投稿ページの og:description（本文・投稿日）
     ところが「最近の投稿の一覧」は、どちらもログイン画面に阻まれて取れない
     （2026-09-23 に確認。X は 0件、Instagram はログイン要求）。
     一覧の取得だけはブラウザが要る。そこだけ人か Claude がやって、
     残りはこの scriptが受け持つ。

   本文は posts.json の全案と突き合わせて、一致したものだけ記録する。
   推測では書かない。一致しなければ「不明」として報告する。
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
# Instagram は素っ気ない UA のときだけ og タグを返す。
# Chrome を名乗るとログイン画面になる（2026-09-23 に確認）。
UA_OG = "Mozilla/5.0"


def fetch(url, ua=UA):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def norm(t):
    return re.sub(r"\s+", "", t or "")


# ---------- 取ってくる ----------

def from_x(sid):
    """X の投稿1本を取る。本文・投稿日・いいね数。"""
    u = ("https://cdn.syndication.twimg.com/tweet-result?id=%s&lang=ja&token=a" % sid)
    d = json.loads(fetch(u))
    body = d.get("text", "")
    # 画像を付けると末尾に t.co のリンクが足される。本文ではないので外す。
    rng = d.get("display_text_range")
    if isinstance(rng, list) and len(rng) == 2:
        body = body[rng[0]:rng[1]]
    body = re.sub(r"\s*https://t\.co/\S+\s*$", "", body).strip()
    return dict(
        media="x", key=sid,
        url="https://x.com/biwakara_fund/status/%s" % sid,
        text=body,
        date=(d.get("created_at") or "")[:10],
        like=d.get("favorite_count"),
    )


def from_ig(code):
    """Instagram の投稿1本を og:description から取る。"""
    h = fetch("https://www.instagram.com/p/%s/" % code, UA_OG)
    m = re.search(r'property="og:description" content="(.*?)"', h, re.S)
    if not m:
        raise RuntimeError("og:description が見つかりません: %s" % code)
    raw = html.unescape(m.group(1))
    # 例: 0 likes, 0 comments - biwakara_fund on September 20, 2026: "本文"
    body = ""
    q = re.search(r'&quot;(.*)&quot;|"(.*)"', raw, re.S)
    if q:
        body = q.group(1) or q.group(2) or ""
    else:
        i = raw.find(": ")
        body = raw[i + 2:] if i >= 0 else raw
    body = html.unescape(body).replace("\\n", "\n")
    body = re.sub(r"\n#[^\n]*$", "", body).strip()      # 末尾のハッシュタグは落とす
    date = ""
    dm = re.search(r"on ([A-Z][a-z]+ \d{1,2}, \d{4})", raw)
    if dm:
        import datetime
        date = datetime.datetime.strptime(dm.group(1), "%B %d, %Y").date().isoformat()
    lm = re.search(r"([\d,]+) likes", raw)
    return dict(media="ig", key=code,
                url="https://www.instagram.com/p/%s/" % code,
                text=body, date=date,
                like=int(lm.group(1).replace(",", "")) if lm else None)


# ---------- 突き合わせる ----------

def match(post, posts):
    """本文が posts.json のどの案と一致するかを返す。一致しなければ None。"""
    t = norm(post["text"])
    for i, d in enumerate(posts["days"]):
        if post["media"] == "x":
            cands = [("本文", d["x"])] + [("案" + v["id"], v["text"]) for v in d.get("xv", [])]
            key = d["id"]
        else:
            cands = [("案" + v["id"], v["text"]) for v in d.get("igv", [])]
            key = "i%02d" % (i + 1)
        for label, c in cands:
            if norm(c) == t:
                pick = label[1:] if label.startswith("案") else "A"
                return dict(key=key, theme=d["theme"], label=label, pick=pick)
    for d in posts["launch"]:
        if norm(d["text"]) == t:
            return dict(key=d["id"], theme="一発目", label="案" + d["id"], pick=d["id"])
    for p in posts["series"]:
        if norm(p["text"]) == t:
            return dict(key=p["id"], theme="連動", label="本文", pick="A")
    return None


# ---------- 記録する ----------

def load_state():
    f = os.path.join(SITE, "index.html")
    t = open(f, encoding="utf-8").read()
    m = re.search(r'(<script id="app-state" type="application/json">)(.*?)(</script>)', t, re.S)
    return f, t, m, json.loads(m.group(2))


def save_state(f, t, m, st):
    body = json.dumps(st, ensure_ascii=False, separators=(",", ":"))
    open(f, "w", encoding="utf-8").write(t[:m.start(2)] + body + t[m.end(2):])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x", nargs="*", default=[], help="X の投稿ID")
    ap.add_argument("--ig", nargs="*", default=[], help="Instagram の shortcode")
    ap.add_argument("--write", action="store_true", help="実際に記録に書き込む")
    a = ap.parse_args()
    if not a.x and not a.ig:
        ap.error("--x か --ig を指定してください")

    posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf-8"))
    f, t, m, st = load_state()
    st.setdefault("xPick", {})
    st.setdefault("igPick", {})

    got, unknown = [], []
    for sid in a.x:
        try:
            got.append(from_x(sid))
        except Exception as e:
            unknown.append(("X " + sid, str(e)))
    for code in a.ig:
        try:
            got.append(from_ig(code))
        except Exception as e:
            unknown.append(("Instagram " + code, str(e)))

    new, already = [], []
    for p in got:
        hit = match(p, posts)
        if not hit:
            unknown.append((p["media"] + " " + p["key"],
                            "本文が posts.json のどの案とも一致しません"))
            continue
        cur = st["items"].get(hit["key"]) or {}
        line = "%s  %-6s %-12s %s  %s" % (
            p["date"] or "日付不明", hit["key"], hit["theme"], hit["label"], p["url"])
        if cur.get("status") == "posted":
            already.append(line)
            continue
        new.append((hit, p, line))

    print("=== すでに記録済み（%d件）===" % len(already))
    for l in already:
        print("  " + l)
    print("\n=== 新しく記録できるもの（%d件）===" % len(new))
    for _, _, l in new:
        print("  " + l)
    if unknown:
        print("\n=== 判定できなかったもの（%d件）===" % len(unknown))
        for k, why in unknown:
            print("  %s … %s" % (k, why))

    if not a.write:
        print("\n※ 見ただけです。書き込むには --write を付けてください。")
        return 0

    for hit, p, _ in new:
        r = {"status": "posted", "m": {}}
        if p["like"]:
            r["m"]["like"] = p["like"]
        r["url" if p["media"] == "x" else "urlIg"] = p["url"]
        st["items"][hit["key"]] = r
        (st["xPick"] if p["media"] == "x" else st["igPick"])[hit["key"]] = hit["pick"]
        if p["date"]:
            st["dates"][hit["key"]] = p["date"]
    save_state(f, t, m, st)
    print("\n%d件を記録しました。build.py を流してから push してください。" % len(new))
    return 0


if __name__ == "__main__":
    sys.exit(main())

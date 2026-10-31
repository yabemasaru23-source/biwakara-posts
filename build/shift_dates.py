"""X の予定日を後ろにずらす（投稿が抜けた日の立て直し用）。

    python shift_dates.py d59 --last d56          # 見るだけ
    python shift_dates.py d59 --last d56 --write  # index.html の app-state に書く

d59 以降の未投稿の回を1日ずつ後ろへ。--last の回は最後の回の翌日に回す。
書いたあとは build.py → push → Artifact 再公開。
2026-10-31 Day56・Day58 が抜けたときに作った（本人「Day59以降を1日ずつ後ろにずらして、Day56は最後に回して」）。
"""
import argparse
import datetime
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "..", "index.html")
PAT = r'(<script id="app-state" type="application/json">)(.*?)(</script>)'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("start")
    ap.add_argument("--last", nargs="*", default=[])
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    html = open(DEST, encoding="utf-8").read()
    m = re.search(PAT, html, re.S)
    st = json.loads(m.group(2))
    dates, items = st["dates"], st.get("items", {})
    posted = lambda k: (items.get(k) or {}).get("status") == "posted"
    num = lambda k: int(k[1:])
    xs = sorted((k for k in dates if re.fullmatch(r"d\d+", k)), key=num)

    plan = {}
    for k in xs:
        if num(k) >= num(a.start) and not posted(k) and k not in a.last:
            d = datetime.date.fromisoformat(dates[k]) + datetime.timedelta(days=a.days)
            plan[k] = d.isoformat()
    end = max(list(plan.values()) + [dates[k] for k in xs if k not in a.last])
    for k in a.last:
        if posted(k):
            print("投稿済みなので動かさない:", k)
            continue
        end = (datetime.date.fromisoformat(end) + datetime.timedelta(days=1)).isoformat()
        plan[k] = end

    for k in sorted(plan, key=lambda k: plan[k]):
        print("%-4s %s → %s" % (k, dates[k], plan[k]))
    # 同じ日に未投稿の X が2本以上ないか
    after = dict(dates, **plan)
    days = [after[k] for k in xs if not posted(k)]
    dup = sorted({d for d in days if days.count(d) > 1})
    print("同じ日に2本:", "、".join(dup) if dup else "なし")

    if a.write:
        dates.update(plan)
        body = json.dumps(st, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        html = re.sub(PAT, lambda mm: mm.group(1) + body + mm.group(3), html, count=1, flags=re.S)
        open(DEST, "w", encoding="utf-8").write(html)
        print("書きました。build.py を流してから push してください。")
    else:
        print("※ 見ただけです。書き込むには --write を付けてください。")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""11/16 の X を埋める（2026-11-16）。

   11/10〜11/15 の X が予定より1日ずつ早く出て、11/16 が空いたため。
   事実の主張を含まない回なので、菅井様の確認は不要。
   あわせて、11/13（金）に出なかった Instagram「書き出してみる」(i33) を 11/16（月）に回す。
"""
import json
import os
import re

import check
from add_days5 import day, TAGS

HERE = os.path.dirname(os.path.abspath(__file__))
NOFACT = "事実の主張を含まない考え方の回（確認不要）"

D84 = day("d84", 84, "見守るということ", "たくさんの\n見守りの中で", "sun", "sugai_18.jpg", [
    "そばで見守ってくれる人がいることは、本人にとって大きな支えです。\n家族だけでなく、地域の人や、一緒に働く仲間も。\nたくさんの見守りの中で、暮らしは続いていきます。",
    "見守ってくれる人は、家族だけではありません。\n地域の人も、一緒に働く仲間も、その一人です。",
    "本人を見守っているのは、誰でしょうか。\n家族、地域の人、一緒に働く仲間。\nたくさんの見守りの中で、暮らしは続いていきます。"],
  ["たくさんの\n見守りの中で", "家族だけで\nなくていい", "暮らしは\n続いていく"],
  [], NOFACT)
D84["x"] = D84["xv"][0]["text"]
D84["tags"] = list(TAGS)


def main():
    p = os.path.join(HERE, "posts.json")
    posts = json.load(open(p, encoding="utf-8"))
    if "d84" not in {d["id"] for d in posts["days"]}:
        posts["days"].append(D84)
    check.run(posts)
    json.dump(posts, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    f = os.path.join(os.path.dirname(HERE), "index.html")
    t = open(f, encoding="utf-8").read()
    m = re.search(r'(<script id="app-state" type="application/json">)(.*?)(</script>)', t, re.S)
    st = json.loads(m.group(2))
    st["dates"]["d84"] = "2026-11-16"
    if (st["items"].get("i33") or {}).get("status") != "posted":
        st["dates"]["i33"] = "2026-11-16"
    ids = [d["id"] for d in posts["days"]]
    i84 = "i%02d" % (ids.index("d84") + 1)
    if i84 not in st["dates"]:
        last_ig = max(v for k, v in st["dates"].items() if k.startswith("i"))
        from add_days5 import ig_dates
        st["dates"][i84] = ig_dates(last_ig, 1)[0]
    t = t[:m.start(2)] + json.dumps(st, ensure_ascii=False, separators=(",", ":")) + t[m.end(2):]
    open(f, "w", encoding="utf-8").write(t)
    print("d84 を 11/16 に入れました", i84, st["dates"][i84], "/ i33 →", st["dates"]["i33"])


if __name__ == "__main__":
    main()

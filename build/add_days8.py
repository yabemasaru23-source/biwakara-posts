# -*- coding: utf-8 -*-
"""11/27 の X を埋める（2026-11-10）。

   11/27 に予定していた d82（応援してくださる方へ）を、X が空いていた 11/10 に前倒しで出したため。
   事実の主張を含まない回なので、菅井様の確認は不要。
"""
import json
import os
import re

import check
from add_days5 import day, TAGS

HERE = os.path.dirname(os.path.abspath(__file__))
NOFACT = "事実の主張を含まない考え方の回（確認不要）"

D83 = day("d83", 83, "親の気持ちも", "親の気持ちも\n大事にしていい", "deep", "bh_20.jpg", [
    "本人の将来を考えるとき、親自身の気持ちも、同じくらい大事です。\n心配や迷いがあって、当たり前です。\nその気持ちごと、一緒に考えていけたらと思っています。",
    "子どもの将来のことを考えると、不安になる日もあると思います。\nその気持ちを、なかったことにしなくて大丈夫です。",
    "「親亡き後」を考えるとき、親自身の気持ちは置き去りになっていませんか。\n心配も迷いも、大事な気持ちです。"],
  ["親の気持ちも\n大事にしていい", "心配や迷いは\n当たり前のこと", "その気持ちごと\n一緒に考えたい"],
  [], NOFACT)
D83["x"] = D83["xv"][0]["text"]
D83["tags"] = list(TAGS)


def main():
    p = os.path.join(HERE, "posts.json")
    posts = json.load(open(p, encoding="utf-8"))
    if "d83" not in {d["id"] for d in posts["days"]}:
        posts["days"].append(D83)
    check.run(posts)
    json.dump(posts, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    f = os.path.join(os.path.dirname(HERE), "index.html")
    t = open(f, encoding="utf-8").read()
    m = re.search(r'(<script id="app-state" type="application/json">)(.*?)(</script>)', t, re.S)
    st = json.loads(m.group(2))
    st["dates"]["d83"] = "2026-11-27"
    ids = [d["id"] for d in posts["days"]]
    i83 = "i%02d" % (ids.index("d83") + 1)
    if i83 not in st["dates"]:
        last_ig = max(v for k, v in st["dates"].items() if k.startswith("i"))
        from add_days5 import ig_dates
        st["dates"][i83] = ig_dates(last_ig, 1)[0]
    t = t[:m.start(2)] + json.dumps(st, ensure_ascii=False, separators=(",", ":")) + t[m.end(2):]
    open(f, "w", encoding="utf-8").write(t)
    print("d83 を 11/27 に入れました", i83, st["dates"][i83])


if __name__ == "__main__":
    main()

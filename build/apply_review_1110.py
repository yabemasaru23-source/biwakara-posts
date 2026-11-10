# -*- coding: utf-8 -*-
"""菅井様の回答（2026-11-10、11/17〜11/30分の3項目）を反映する。

  1 修正 運営費：「運営費にあてる計画です」→「運営費に」。前身の「びわから基金」「みんなのびわから」の
        会費（寄付）で、すでにそのように運用している（計画ではない）
  2 修正 置いてくださるお店：「いくつかのお店でも」→「55のお店で」（55店舗と取引がある）
  3 ×  びわ茶の商品化での長崎県 産業労働部の助言：だいぶ古い話なので、今は載せない
        → d78 は出さない（日付を外して保留）。11/27 の X には、確認不要の新しい回 d82 を入れる
"""
import json
import os
import re

import check
from add_days5 import day, ig, TAGS

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "posts.json")
p = json.load(open(F, encoding="utf-8"))
D = {d["id"]: d for d in p["days"]}
NOTE = "facts.md（菅井様 2026-11-10 回答）の範囲で執筆"
NOFACT = "事実の主張を含まない考え方の回（確認不要）"


def put(did, xs, igx=("", "", ""), **kw):
    d = D[did]
    for v, t in zip(d["xv"], xs):
        v["text"] = t
    for v, t, e in zip(d["igv"], xs, igx):
        v["text"] = ig(t, e)
    d["x"] = xs[0]
    d.update(kw)


put("d76", [
    "みんなのびわから基金に集まったお金の20%は、運営費に。\n基金を続けていくための費用です。\n使いみちは、最初から決めて公開しています。",
    "基金を続けるにも、費用がかかります。\n寄付の20%は、その運営費に。\n隠さずに書いておきたいと思いました。",
    "寄付のうち、運営費はどれくらいでしょうか。\nみんなのびわから基金では、20%です。\n最初から決めて、公開しています。"],
    ask=[], check=[NOTE])

put("d77", [
    "三和ゆめランドの授産品は、55のお店で扱っていただいています。\n置いてくださるお店があるから、つくる仕事が続いていきます。",
    "つくったものが、お店の棚に並ぶ。\n三和ゆめランドの授産品は、55のお店で扱っていただいています。",
    "授産品は、どこで手に取れるのでしょうか。\n三和ゆめランドの授産品は、55のお店で扱っていただいています。"],
    cap="置いてくださる\nお店は55店舗",
    igslides=["置いてくださる\nお店は55店舗", "55のお店の棚に\n並ぶ授産品", "つくる仕事が\n続いていく"],
    ask=[], check=[NOTE])

D["d78"]["ask"] = []
D["d78"]["check"] = ["出さない（2026-11-10 菅井様：だいぶ古い話なので今は載せない）"]

D82 = day("d82", 82, "応援してくださる方へ", "応援してくださる\n方へ", "sun", "sugai_15.jpg", [
    "月額で応援してくださっている方へ。\n毎月の応援が、この基金の土台になっています。\nいつも、ありがとうございます。",
    "毎月、決まった日に届く応援。\nその一つひとつが、みんなのびわから基金を支えています。\nありがとうございます。",
    "この基金を支えているのは、誰でしょうか。\n毎月応援してくださっている、一人ひとりの方です。\nいつも、ありがとうございます。"],
  ["応援してくださる\n方へ", "毎月の応援が\n基金の土台です", "いつも\nありがとうございます"],
  [], NOFACT)
D82["x"] = D82["xv"][0]["text"]
D82["tags"] = list(TAGS)
if "d82" not in D:
    p["days"].append(D82)

for did in ("d76", "d77", "d82"):
    dd = D82 if did == "d82" else D[did]
    s = json.dumps(dd, ensure_ascii=False)
    assert "計画" not in s or did != "d76", did
    assert "いくつか" not in s, did
    for v in dd["xv"]:
        assert len(v["text"].replace("\n", "")) <= 140, (did, v["id"])

check.run(p)
json.dump(p, open(F, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 日付：d78 を外し、11/27 に d82。d78 の Instagram の枠は d82 の Instagram に回す
f = os.path.join(os.path.dirname(HERE), "index.html")
t = open(f, encoding="utf-8").read()
m = re.search(r'(<script id="app-state" type="application/json">)(.*?)(</script>)', t, re.S)
st = json.loads(m.group(2))
ids = [d["id"] for d in p["days"]]
i78, i82 = "i%02d" % (ids.index("d78") + 1), "i%02d" % (ids.index("d82") + 1)
st["dates"].pop("d78", None)
if i78 in st["dates"]:
    st["dates"][i82] = st["dates"].pop(i78)
st["dates"]["d82"] = "2026-11-27"
t = t[:m.start(2)] + json.dumps(st, ensure_ascii=False, separators=(",", ":")) + t[m.end(2):]
open(f, "w", encoding="utf-8").write(t)
print("反映しました（d76・d77 修正、d78 保留、d82 を 11/27 に）", i78, "→", i82, st["dates"].get(i82))

# -*- coding: utf-8 -*-
"""12/1〜12/7 の X を埋める（2026-11-17）。

   X の原稿が 11/30 で尽きるため。矢部さん 11/17「とにもかくにも絶対に抜けないように」。
   事実の主張を含まない考え方の回なので、菅井様の確認は不要。
   12/8 以降は、次の菅井様の確認（facts.md の範囲で書く回）で埋める。
"""
import datetime
import json
import os
import re

import check
from add_days5 import day, TAGS, ig_dates

HERE = os.path.dirname(os.path.abspath(__file__))
NOFACT = "事実の主張を含まない考え方の回（確認不要）"

NEW = [
    ("d85", 85, "12月のはじめに", "12月に\nなりました", "sun", "sugai_03.jpg", [
        "12月になりました。\n今年も、たくさんの方に読んでいただきました。\n残りのひと月も、ここで少しずつお伝えしていきます。",
        "12月になりました。\n読んでくださる方がいることが、続ける力になっています。\nありがとうございます。",
        "今年も、あとひと月です。\n読んでくださった方、ありがとうございます。\n残りの日々も、ここでお伝えしていきます。"],
     ["12月に\nなりました", "読んでくださる方へ", "残りのひと月も"]),
    ("d86", 86, "ことばにして残す", "ことばにして\n残しておく", "deep", "sugai_05.jpg", [
        "本人の好きなこと、得意なこと、苦手なこと。\nいちばんよく知っているのは、そばにいる家族です。\nそれをことばにして残しておくと、次に支える人への手紙になります。",
        "家族だけが知っている、本人のこと。\nことばにして残しておくと、次に支える人の助けになります。",
        "本人のことを、いちばんよく知っているのは誰でしょうか。\nその知っていることを、ことばにして残しておく。\n次に支える人への手紙になります。"],
     ["ことばにして\n残しておく", "家族だけが\n知っていること", "次に支える人への\n手紙に"]),
    ("d87", 87, "話してみる", "話してみるだけで\n軽くなることも", "sun", "sugai_10.jpg", [
        "心配ごとは、ひとりで抱えるほど重くなります。\n話せる相手がひとりいるだけで、少し軽くなることがあります。",
        "答えが出なくても、話してみるだけでいい。\nことばにすると、気持ちが少し整うことがあります。",
        "心配ごとを、誰かに話したことはありますか。\n話せる相手がひとりいるだけで、少し軽くなることがあります。"],
     ["話してみるだけで\n軽くなることも", "答えが出なくても\nいい", "話せる相手が\nひとりいれば"]),
    ("d88", 88, "紙一枚の準備", "紙一枚から\nはじめる準備", "deep", "sugai_16.jpg", [
        "大きなことを決める前に、小さな準備から。\nかかりつけの病院、よく使う薬、連絡してほしい人。\n紙一枚にまとめておくだけでも、いざというときの助けになります。",
        "準備は、紙一枚からでも始められます。\n病院、薬、連絡してほしい人。\nまとめておくと、いざというときに役立ちます。",
        "いざというとき、本人のことを誰かに伝えられますか。\n病院、薬、連絡してほしい人。\n紙一枚にまとめておくだけでも助けになります。"],
     ["紙一枚から\nはじめる準備", "病院と薬と\n連絡先", "いざというときの\n助けに"]),
    ("d89", 89, "表情に表れる気持ち", "ことばにならない\n気持ちも", "sun", "bh_06.jpg", [
        "これからのことを考えるとき、本人の気持ちを真ん中に置きたいと思っています。\nことばにならない気持ちも、表情やしぐさに表れています。",
        "ことばにならない気持ちも、ちゃんとあります。\n表情やしぐさから、受けとめていきたいと思っています。",
        "本人の気持ちは、どこに表れるでしょうか。\nことばだけではなく、表情やしぐさにも。\nそれを受けとめるところから、始めたいと思っています。"],
     ["ことばにならない\n気持ちも", "表情やしぐさに\n表れる", "本人の気持ちを\n真ん中に"]),
    ("d90", 90, "あたたかい一杯", "あたたかい\n一杯を", "sun", "bh_01.jpg", [
        "寒い日が続いています。\nあたたかいお茶を一杯。\n体も気持ちも、少しほぐれる時間になりますように。",
        "冷える日には、あたたかいお茶を。\nほっとひと息つく時間を、大事にしてください。",
        "寒い日、どんなふうに過ごしていますか。\nあたたかいお茶を一杯いれて、少しひと息。\n体も気持ちも、ほぐれますように。"],
     ["あたたかい\n一杯を", "ほっと\nひと息", "体も気持ちも\nほぐれますように"]),
    ("d91", 91, "顔が浮かぶ人", "顔が浮かぶ人が\nいること", "deep", "bh_07.jpg", [
        "困ったときに、顔が浮かぶ人がいること。\nそれは、お金と同じくらい大切な備えかもしれません。\nそんなつながりを、地域の中に増やしていきたいと思っています。",
        "困ったときに、相談できる顔が浮かぶ。\nそのつながりも、大切な備えのひとつです。",
        "困ったとき、誰の顔が浮かびますか。\nそんなつながりも、大切な備えのひとつです。\n地域の中に増やしていきたいと思っています。"],
     ["顔が浮かぶ人が\nいること", "つながりも\n備えのひとつ", "地域の中に\n増やしていく"]),
]


def main():
    p = os.path.join(HERE, "posts.json")
    posts = json.load(open(p, encoding="utf-8"))
    have = {d["id"] for d in posts["days"]}
    made = []
    for did, n, theme, cap, tone, photo, xs, slides in NEW:
        if did in have:
            continue
        d = day(did, n, theme, cap, tone, photo, xs, slides, [], NOFACT)
        d["x"] = d["xv"][0]["text"]
        d["tags"] = list(TAGS)
        for v in d["xv"]:
            assert len(v["text"].replace("\n", "")) <= 140, (did, v["id"])
            assert "障害" not in v["text"], did
        posts["days"].append(d)
        made.append(did)
    check.run(posts)
    json.dump(posts, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    f = os.path.join(os.path.dirname(HERE), "index.html")
    t = open(f, encoding="utf-8").read()
    m = re.search(r'(<script id="app-state" type="application/json">)(.*?)(</script>)', t, re.S)
    st = json.loads(m.group(2))
    ids = [d["id"] for d in posts["days"]]
    start = datetime.date(2026, 12, 1)
    for i, (did, *_rest) in enumerate(NEW):
        st["dates"].setdefault(did, (start + datetime.timedelta(days=i)).isoformat())
        ik = "i%02d" % (ids.index(did) + 1)
        if ik not in st["dates"]:
            last_ig = max(v for k, v in st["dates"].items() if k.startswith("i"))
            st["dates"][ik] = ig_dates(last_ig, 1)[0]
    t = t[:m.start(2)] + json.dumps(st, ensure_ascii=False, separators=(",", ":")) + t[m.end(2):]
    open(f, "w", encoding="utf-8").write(t)
    print("追加:", made, {d[0]: st["dates"][d[0]] for d in NEW})


if __name__ == "__main__":
    main()

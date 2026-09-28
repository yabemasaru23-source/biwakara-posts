# -*- coding: utf-8 -*-
"""公開物の検査。gen_images.py と build.py の両方から呼び、
   問題があればビルドを止める。

   2026-08-31、投稿画像に「案 A」「放送翌日」「3 / 4」といった
   こちらの管理ラベルが載ったまま出た。目視では止まらなかったため、
   機械で弾く。新しい管理ラベルを増やしたら INTERNAL にも足すこと。
"""
import re

# ---- 外に出してはいけない、こちらの管理用語 ----
INTERNAL = [
    "案 A", "案 B", "案 C", "案A　", "案B　", "案C　",
    "放送開始前", "放送中", "放送翌日", "放送1週間後", "放送１週間後",
    "未確認", "要修正", "投稿済み", "見送り", "採用",
    "下書き", "説明型", "情景型", "問いかけ型", "宣言型",
    "一発目", "連動シリーズ", "投稿デスク", "エンゲージメント率",
]

# ---- 憲法で禁じている表現 ----
BANNED = ["無料配布", "🎁", "限定", "今だけ", "DMください", "DM下さい"]

# 絵文字（記号・絵文字ブロック）
EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F0FF️⭐❤]")
HASHTAG = re.compile(r"[#＃]\S")
URL = re.compile(r"https?://")

# 投稿画像に使ってはいけない素材。理由を消さずに残すこと。
# 一度でも公開してしまうと取り返せないので、ビルドを止める側に倒している。
BAN_PHOTO = {
    "ikeda":     "理事長ご本人が写真の使用を望まれない（2026-09-11）",
    # work_003 は 2026-09-27 矢部さん確認で解禁（法人がサイト掲載用に上げた写真。SNSでも使ってよい）
    "nakigao":   "同情訴求に読まれうる",
    "furo01":    "介助の場面を描いたイラスト。受信者テスト未了",
}


def photo(name):
    """素材ファイル名を検査する。禁止のものが来たらビルドを止める。"""
    low = name.lower()
    for key, why in BAN_PHOTO.items():
        if key in low:
            raise SystemExit(
            "使ってはいけない素材です: %s\n  理由: %s\n"
            "  ほかの素材に差し替えてください。" % (name, why))
    return name


X_LIMIT = 140
IG_TAG_MAX = 5   # Instagram は6個目以降が無効化される（2026-09-11 実投稿で確認）
IG_LIMIT = 2200


class CheckError(Exception):
    pass


# 出島福祉村・菅井様の指摘（2026-09-27）。事実として確認できないものは書かない。
FACT_BAN = [
    ("600", "農地の規模を示す数字。根拠が確認できないため使わない"),
    ("短期入所", "受け入れていない（2026-09-28 菅井様回答）"),
    ("泊まれる", "短期入所は受け入れていない（2026-09-28 菅井様回答）"),
    ("数日だけ", "短期入所は受け入れていない（2026-09-28 菅井様回答）"),
    ("直売所", "三和ゆめランドは就労継続支援の施設で、直売所ではない（2026-09-28 菅井様回答）"),
    ("県の農業部門", "助言を受けたのは県の産業労働部（2026-09-28 菅井様回答）"),
    ("始めるための資金", "他法人へ渡す仕組みは未定（2026-09-28 菅井様回答）"),
]
# 黄綬褒章は建築分野での受章。福祉での受章と読める書き方をしない。
# 「黄綬」と書くなら、同じ文の中に「建築」がなければ止める。
def fact_gate(label, text):
    for word, why in FACT_BAN:
        if word in (text or ""):
            raise CheckError("%s: 「%s」 … %s" % (label, word, why))
    if "黄綬" in (text or "") and "建築" not in text:
        raise CheckError("%s: 黄綬褒章に触れるなら「建築」での受章だと同じ文に書く" % label)
    # 正式名称は「みんなのびわから基金」。単独の「びわから基金」は止める
    if re.search(r"(?<!みんなの)びわから基金", text or ""):
        raise CheckError("%s: 「びわから基金」単独は不可。正式名称は「みんなのびわから基金」" % label)


def _internal(text, allow=()):
    hits = []
    for w in INTERNAL:
        if w in allow:
            continue
        if w in text:
            hits.append(w)
    # 「3 / 4」形式の通し番号
    if "seq" not in allow and re.search(r"\d\s*/\s*\d", text):
        hits.append("連番（n / n）")
    # 「DAY 03」形式。例外は設けない（2026-09-02 に表紙から全廃）
    if re.search(r"DAY\s*\d", text, re.I):
        hits.append("DAY nn")
    return hits


def image_text(name, parts, allow=()):
    """画像に焼き込む文字列を検査する。
       parts: 画像に載る文字列のリスト。allow: この画像では許す語のタプル。"""
    for _t in parts:
        fact_gate(name, _t)
    joined = "　".join(x for x in parts if x)
    bad = _internal(joined, allow)
    if EMOJI.search(joined):
        bad.append("絵文字")
    for w in BANNED:
        if w in joined:
            bad.append(w)
    if bad:
        raise CheckError("画像 %s に出してはいけない語: %s\n  → %s"
                         % (name, "、".join(bad), joined))


def post_text(name, media, text, tags=None):
    """投稿本文を検査する。media は 'x' か 'ig'。"""
    fact_gate(name, text)
    bad = []
    if EMOJI.search(text):
        bad.append("絵文字")
    for w in BANNED:
        if w in text:
            bad.append(w)
    bad += _internal(text)

    n = len(text)
    if media == "x":
        if HASHTAG.search(text):
            bad.append("ハッシュタグ（Xでは付けない）")
        if URL.search(text):
            bad.append("本文中のURL（導線はプロフィール欄）")
        if n > X_LIMIT:
            bad.append("%d字（140字を超過）" % n)
    else:
        if tags and len(tags) > IG_TAG_MAX:
            bad.append("ハッシュタグ%d個（Instagramは%d個まで）" % (len(tags), IG_TAG_MAX))
        full = n + (sum(len(t) + 2 for t in tags) if tags else 0)
        if URL.search(text):
            bad.append("本文中のURL")
        if full > IG_LIMIT:
            bad.append("%d字（2,200字を超過）" % full)
    if bad:
        raise CheckError("本文 %s（%s）に問題: %s" % (name, media, "、".join(bad)))


def run(posts):
    """posts.json 全体を検査する。問題があれば CheckError。"""
    n = 0
    for d in posts["launch"]:
        post_text(d["id"], "x", d["text"])
        n += 1
    for p in posts["series"]:
        post_text(p["id"], "x", p["text"])
        n += 1
    for d in posts["days"]:
        if d.get("xv"):
            for v in d["xv"]:
                post_text("%s 案%s" % (d["id"], v["id"]), "x", v["text"])
                n += 1
        else:
            post_text(d["id"], "x", d["x"])
            n += 1
        for v in d.get("igv", []):
            post_text("%s 案%s" % (d["id"], v["id"]), "ig", v["text"], d["tags"])
            n += 1
        for i, t in enumerate(d.get("igslides", [])):
            image_text("%s_%d" % (d["id"], i + 2), [t], allow=("seq",))
            n += 1
    return n

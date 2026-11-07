# -*- coding: utf-8 -*-
"""前の日に投稿が抜けていないかを確かめる（見るだけ。記録は変えない）。2026-11-07 追加。

    python check_gaps.py

X は毎日、Instagram は月・水・金。記録（index.html の app-state）にある投稿URLから、
実際に投稿された日（日本時間）を割り出して判定する。予定日ではなく、投稿IDの時刻で見る。
抜けがあれば 1 行目に「抜けあり」と出す（毎朝の記録作業が、これを見て矢部さんに知らせる）。
"""
import datetime
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
IG_DAYS = (0, 2, 4)          # 月・水・金
A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def x_day(sid):
    ms = (int(sid) >> 22) + 1288834974657
    return (datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=ms, hours=9)).date()


def ig_day(code):
    n = 0
    for ch in code:
        n = n * 64 + A.index(ch)
    ms = (n >> 23) + 1314220021721
    return (datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=ms, hours=9)).date()


def main():
    t = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    st = json.loads(re.search(r'<script id="app-state" type="application/json">(.*?)</script>', t, re.S).group(1))
    xs, igs = set(), set()
    for v in st.get("items", {}).values():
        if (v or {}).get("status") != "posted":
            continue
        m = re.search(r"status/(\d+)", v.get("url", "") or "")
        if m:
            xs.add(x_day(m.group(1)))
        m = re.search(r"/p/([^/?]+)", v.get("urlIg", "") or "")
        if m:
            igs.add(ig_day(m.group(1)))
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).date()
    y = today - datetime.timedelta(days=1)
    wd = "月火水木金土日"
    miss = []
    if y not in xs:
        miss.append("X")
    if y.weekday() in IG_DAYS and y not in igs:
        miss.append("Instagram")
    label = "%d/%d（%s）" % (y.month, y.day, wd[y.weekday()])
    if miss:
        print("抜けあり：%s の %s が出ていません" % (label, "・".join(miss)))
    else:
        print("抜けなし：%s は予定どおり出ています" % label)
    # 直近7日の抜け（参考）
    gaps = []
    for i in range(1, 8):
        d = today - datetime.timedelta(days=i)
        g = [k for k, ok in (("X", d in xs), ("IG", d.weekday() not in IG_DAYS or d in igs)) if not ok]
        if g:
            gaps.append("%d/%d %s" % (d.month, d.day, "・".join(g)))
    print("直近7日の抜け：" + ("、".join(gaps) if gaps else "なし"))


if __name__ == "__main__":
    main()

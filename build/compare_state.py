# -*- coding: utf-8 -*-
"""Artifact 版とローカルの index.html の app-state（承認・投稿記録・数字）を比べる（2026-10-03）。
使い方: python build/compare_state.py <Artifactを読んで保存したhtml>
ローカルを作り直して Artifact に再公開する前に、Artifact 側の入力を消さないために使う。"""
import json, os, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
PAT = re.compile(r'<script id="app-state" type="application/json">(.*?)</script>', re.S)


def state(path):
    m = PAT.search(open(path, encoding="utf-8").read())
    return json.loads(m.group(1)) if m else {}


art = state(sys.argv[1])
loc = state(os.path.join(os.path.dirname(HERE), "index.html"))
print("rev  artifact:", art.get("rev"), " local:", loc.get("rev"))
ai, li = art.get("items") or {}, loc.get("items") or {}
only_a = sorted(set(ai) - set(li))
only_l = sorted(set(li) - set(ai))
diff = sorted(k for k in set(ai) & set(li) if ai[k] != li[k])
print("items artifact:", len(ai), " local:", len(li))
print("artifactだけ:", only_a)
print("localだけ:", only_l)
print("中身が違う:", diff)
for k in diff[:10]:
    print(" ", k, "\n    A:", json.dumps(ai[k], ensure_ascii=False)[:200], "\n    L:", json.dumps(li[k], ensure_ascii=False)[:200])
for key in ("chosen", "dates", "igPick", "xPick"):
    if art.get(key) != loc.get(key):
        print("違う:", key)

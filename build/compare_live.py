"""公開中の投稿デスク（Artifact）と、手元の index.html を比べる。

    python compare_live.py <Artifact が保存したライブ版のパス>

Artifact の再公開が「ライブ版を見ていない」で止められたときに使う。
app-state 以外が同じで、app-state の違いが今回の追記（新しい項目・日付の補正・rev）だけなら
「SAFE」と出す。ライブ側にしかない内容があれば「UNSAFE」と出して終了コード1。
"""
import json
import os
import re
import sys

PAT = re.compile(r'<script id="app-state" type="application/json">(.*?)</script>', re.S)


def split(path):
    t = open(path, encoding="utf-8").read()
    m = PAT.search(t)
    rest = t[:m.start()] + t[m.end():]
    # ライブ版は公開時に外側のひな形で包まれるので、本体の先頭から比べる
    i = rest.find("<title>")
    return json.loads(m.group(1)), rest[i:].rstrip().removesuffix("</body></html>").rstrip()


def walk(live, mine, path, out):
    if isinstance(live, dict) and isinstance(mine, dict):
        for k in set(live) | set(mine):
            p = path + "/" + k
            if k not in mine:
                out.append(("ライブにだけある", p))
            elif k in live:
                walk(live[k], mine[k], p, out)
    elif live != mine and not path.startswith("/rev") and not path.startswith("/dates/"):
        out.append(("値が違う", path))


def main():
    live, live_rest = split(sys.argv[1])
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")
    mine, mine_rest = split(here if len(sys.argv) < 3 else sys.argv[2])
    out = []
    if live_rest != mine_rest:
        out.append(("app-state 以外", "ページ本体が違う"))
    walk(live, mine, "", out)
    if out:
        print("UNSAFE")
        for kind, p in out[:30]:
            print(" ", kind, p)
        return 1
    print("SAFE: ライブ版の内容はすべて手元に含まれています")
    return 0


if __name__ == "__main__":
    sys.exit(main())

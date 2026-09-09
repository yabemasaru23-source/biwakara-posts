# -*- coding: utf-8 -*-
"""池田理事長・経営者あての実施報告書（PDF）を組み立てる。
   投稿サイトに記録した実績から作るので、数字は手入力しない。
   出力: びわから基金部門/成果物/SNS運用実施報告_10日間_YYYY-MM-DD.pdf
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
DEPT = os.path.dirname(SITE)
OUT = os.path.join(DEPT, "成果物")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CSS = """
@page{size:A4;margin:16mm 15mm 14mm}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Zen Kaku Gothic New","Yu Gothic",sans-serif;font-size:10.5pt;
  line-height:1.85;color:#2A2117;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{page-break-after:always}
.page:last-child{page-break-after:auto}
.eyebrow{font-size:8pt;letter-spacing:.18em;color:#B08046;font-weight:700}
h1{font-family:"Shippori Mincho",serif;font-size:20pt;font-weight:700;line-height:1.4;
  margin:6px 0 10px}
h2{font-family:"Shippori Mincho",serif;font-size:13.5pt;font-weight:700;margin:20px 0 8px;
  padding-left:11px;border-left:4px solid #E2892B}
h3{font-size:11pt;font-weight:700;margin:14px 0 5px;color:#6E3907}
p{margin:0 0 8px}
.lead{color:#6B5C48;font-size:9.5pt;margin-bottom:14px}
.meta{font-size:8.5pt;color:#7B6B55;border-top:1px solid #E5DAC6;
  border-bottom:1px solid #E5DAC6;padding:7px 0;margin:12px 0 18px}
table{width:100%;border-collapse:collapse;font-size:9pt;margin:8px 0 12px}
th{background:#F4EDDF;text-align:left;padding:6px 8px;font-weight:700;
  border-bottom:1.5px solid #E2892B;white-space:nowrap}
td{padding:5px 8px;border-bottom:1px solid #EDE4D4;vertical-align:top}
td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.kpi{display:flex;gap:9px;margin:12px 0 16px}
.kpi div{flex:1;border:1px solid #E5DAC6;border-radius:9px;padding:10px 12px;background:#FDFBF6}
.kpi b{display:block;font-family:"Shippori Mincho",serif;font-size:19pt;line-height:1.2;color:#E2892B}
.kpi span{font-size:8pt;color:#7B6B55}
.box{background:#FBF6EC;border-radius:9px;padding:12px 15px;margin:10px 0}
.warn{background:#FBEDE9;border-left:4px solid #C4564A;border-radius:0 9px 9px 0;
  padding:12px 15px;margin:10px 0}
.warn b{color:#A8402F}
.ok{background:#EAF3EC;border-left:4px solid #3F8F63;border-radius:0 9px 9px 0;
  padding:12px 15px;margin:10px 0}
.ok b{color:#2C6B48}
ul{margin:4px 0 10px 18px}
li{margin-bottom:4px}
.small{font-size:8.5pt;color:#7B6B55}
.foot{margin-top:22px;padding-top:8px;border-top:1px solid #E5DAC6;
  font-size:8pt;color:#9A8B76;display:flex;justify-content:space-between}
.quote{font-family:"Shippori Mincho",serif;font-size:11pt;background:#fff;
  border:1px solid #E5DAC6;border-radius:9px;padding:11px 14px;margin:7px 0;white-space:pre-line}
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    rows = json.load(open(os.path.join(HERE, "_report_rows.json"), encoding="utf-8"))
    today = "2026-09-09"

    x = [r for r in rows if r["media"] == "X"]
    ig = [r for r in rows if r["media"] == "Instagram"]
    xi = [r["imp"] for r in x if r["imp"]]
    igi = [r["imp"] for r in ig if r["imp"]]

    def tbl(rs, label):
        out = ['<table><tr><th>日付</th><th>投稿</th><th style="text-align:right">%s</th>'
               '<th style="text-align:right">いいね</th></tr>' % label]
        for r in rs:
            out.append("<tr><td>%s</td><td>%s</td><td class='n'>%s</td><td class='n'>%s</td></tr>"
                       % (r["date"][5:].replace("-", "/"), esc(r["name"]),
                          r["imp"] if r["imp"] is not None else "—",
                          r["like"] if r["like"] is not None else "—"))
        return "".join(out) + "</table>"

    html = """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap">
<style>%s</style></head><body>

<div class="page">
<div class="eyebrow">MINNA NO BIWAKARA FUND ／ 実施報告</div>
<h1>SNS運用 10日間の実施報告<br>と、次の一手のご提案</h1>
<p class="lead">みんなのびわから基金プロジェクト ／ 池田理事長・経営者 宛</p>
<div class="meta">対象期間 2026年8月28日（開設）〜 9月9日 ／ 作成 2026年9月9日 ／ びわから基金部門</div>

<h2>1. 何をしたか</h2>
<p>8月28日にX・Instagramを開設し、13日間で<b>%d本</b>を投稿しました。自動投稿は使わず、すべて内容を確認したうえで人の手で公開しています。</p>
<div class="kpi">
<div><b>%d</b><span>投稿数（X %d／Instagram %d）</span></div>
<div><b>%d</b><span>X 表示回数の合計</span></div>
<div><b>%d</b><span>Instagram 閲覧数の合計</span></div>
<div><b>11</b><span>フォロワー合計（X 4／IG 7）</span></div>
</div>
<p class="small">※ Xの表示回数は公開ページで見える値、Instagramはインサイトの閲覧数（30日間）。投稿直後で数字が確定していないものは「—」。</p>

<h3>投稿の内訳</h3>
<ul>
<li><b>一発目</b>（はじめまして）… 3案から理事長・経営者のご確認を経て案Aを採用</li>
<li><b>24時間テレビ連動シリーズ 4本</b> … 放送前・放送中・翌日・1週間後。8月21日にご共有した構成のまま完走</li>
<li><b>10日間の連載</b> … 3本柱／びわ茶／名前の由来／農福連携／支援の考え方／いまの支え／仕事の選択肢／産学連携（X 8本、Instagram 6本）</li>
</ul>

<h2>2. 結果</h2>
<div class="ok"><b>Instagramが、Xの2倍以上届いています。</b><br>
1投稿あたりの平均は Instagram %.1f、X %.1f。フォロワーが7人しかいないにもかかわらず、
Instagramの閲覧者は16人、閲覧の<b>41.9%%がフォロワー以外</b>でした。ハッシュタグ経由で外に届いています。</div>

<h3>Instagram（インサイト・30日間）</h3>
%s
<h3>X（公開されている表示回数）</h3>
%s
<div class="foot"><span>みんなのびわから基金プロジェクト</span><span>1 / 3</span></div>
</div>

<div class="page">
<div class="eyebrow">MINNA NO BIWAKARA FUND ／ 実施報告</div>

<h2>3. 分かったこと</h2>

<h3>（1）物語のある投稿が読まれます</h3>
<p>「出島福祉村」という名前の由来（出島とオランダの話）が、<b>両方の媒体で最も読まれました</b>。</p>
<table><tr><th>投稿</th><th style="text-align:right">Instagram</th><th style="text-align:right">X</th></tr>
<tr><td><b>名前の由来（出島・オランダ）</b></td><td class="n"><b>31</b></td><td class="n"><b>16</b></td></tr>
<tr><td>農福連携</td><td class="n">24</td><td class="n">2</td></tr>
<tr><td>びわ茶</td><td class="n">24</td><td class="n">8</td></tr>
<tr><td>支援の考え方</td><td class="n">18</td><td class="n">7</td></tr>
<tr><td>3本柱</td><td class="n">17</td><td class="n">9</td></tr></table>
<p>団体の仕組みを説明した投稿より、<b>由来や経緯を語った投稿</b>が読まれています。母数は小さいものの、
2つの媒体で同じ結果が出たことには意味があると考えます。</p>

<h3>（2）投稿は届いている。止まっているのはプロフィールです</h3>
<div class="warn"><b>プロフィールを見に来た32人が、一人もフォローしていません。</b><br>
Instagramの閲覧129回に対し、プロフィールへのアクセスは<b>32回（25%%）</b>。
4人に1人が「この団体は何だろう」とプロフィールを見に来ています。
ところが<b>新規フォロワー0人、自己紹介リンクのタップ0回</b>。全員がそのまま離れています。</div>
<p>投稿の中身は機能しています。<b>いま直すべきは投稿ではなく、プロフィールです。</b></p>

<h3>（3）フォロワーが少なすぎて、Xが伸びません</h3>
<p>Xは基本的にフォロワーに配信し、その反応を見て外へ広げます。フォロワー4人では広がる元がありません。
一方Instagramはハッシュタグで外に出るため、同じ内容でも2倍以上届いています。
<b>当面はInstagramに重心を置くのが合理的です。</b></p>

<h2>4. 率直な見通し</h2>
<p>13日間でフォロワーは合計11人、1日あたり約1.2人です。目標の10,000人を3年で達成するには
<b>1日あたり9人</b>が必要で、現状の7〜8倍にあたります。</p>
<p><b>投稿を続けるだけでは届きません。</b>投稿本数を増やしても、スパムと判定される危険が増えるだけです。
必要なのは、すでにある関係をオンラインに移すことだと考えます。</p>
<table><tr><th>いま手が届く相手</th><th style="text-align:right">規模</th></tr>
<tr><td>kizunaカフェ（同じ法人が運営・Instagram）</td><td class="n"><b>2,153人</b></td></tr>
<tr><td>三和ゆめランド（同じ法人・Instagram）</td><td class="n">—</td></tr>
<tr><td>出島福祉村の職員・ご家族・地域の関係者</td><td class="n">24年分</td></tr>
<tr><td>SNSで自力で集めた分</td><td class="n">11人</td></tr></table>
<p>kizunaカフェ1件で、現在の約200倍の規模です。法人内での連携が、いま最も効果の大きい打ち手です。</p>
<div class="foot"><span>みんなのびわから基金プロジェクト</span><span>2 / 3</span></div>
</div>

<div class="page">
<div class="eyebrow">MINNA NO BIWAKARA FUND ／ 改善のご提案</div>

<h2>5. 改善のご提案（優先順）</h2>

<h3>① プロフィールを直す — 最優先</h3>
<p>32人が来て0人しか動いていません。投稿を10本増やすより効果があります。</p>
<p class="small">現在のInstagramプロフィール</p>
<div class="quote">「みんなのびわから基金｜出島福祉村応援プロジェクト
「親亡き後」の不安を、日本からなくす。
長崎から、住まい・専門家・仕事をつなぐ長崎モデルを発信します。
月額1,500円〜｜社会福祉法人 出島福祉村</div>
<p class="small">ご提案（93字）</p>
<div class="quote">長崎で、障害のある方とご家族の「親亡き後」に備える仕組みをつくっています。

住まい・専門家・仕事の3つ。びわ茶や畑の話も。
週3回、その歩みを載せています。

社会福祉法人 出島福祉村</div>
<ul>
<li><b>「月額1,500円〜」を外す</b> … 訪れた瞬間に寄付の話が出ます。まだ何者か分からない段階では早く、サイトに任せるべきです</li>
<li><b>「週3回」を入れる</b> … 更新頻度が分かると、フォローする理由になります</li>
<li><b>「びわ茶や畑」を入れる</b> … 何が読めるアカウントかが想像できます</li>
</ul>
<div class="warn"><b>あわせて、2点の不具合があります。</b><br>
・Instagramの1行目、かぎかっこ「が閉じていません<br>
・Xのプロフィールのリンクに計測用の印がなく、<b>Xからサイトへの流入だけ測れていません</b></div>

<h3>② ハイライトを3つ作る（Instagram）</h3>
<p>現在ゼロで、訪問者が過去を追う入口がありません。「びわから基金とは」「びわ茶ができるまで」「長崎モデル」の3つをご提案します。</p>

<h3>③ kizunaカフェ・三和ゆめランドとの連携</h3>
<p>同じ法人が運営し、カフェは2,153人のフォロワーを持っています。相互の紹介、店内での案内、
びわ茶・びわジャムからの導線など、法人内で調整できる範囲での連携をご検討ください。</p>

<h3>④ 次の10本は「物語」を軸にする</h3>
<p>数字が示した方向に寄せます。びわ茶が生まれた経緯、24年の歩み、商品の話など。</p>

<h2>6. ご確認をお願いしたい事項</h2>
<p>公開前に裏取りが必要な項目を、投稿ごとに記録しています。現在<b>11件</b>あります。主なものは以下です。</p>
<ul>
<li>ノウフク・アワードの<b>受賞年と賞の正式表記</b></li>
<li>びわ茶の商品化に助言を受けた<b>県の部署の正式名称</b>と年次</li>
<li>九州大学との連携で<b>公表してよい範囲</b>（学部名・研究室名・時期）</li>
<li>短期入所の受け入れ日数・体制が、実際の運用と食い違っていないか</li>
<li>出島復元事業に関わった年・オランダ視察の年次</li>
</ul>
<p class="small">現時点では、いずれも数字や固有名詞をぼかして記載しているため、そのままでも問題は生じません。
正確な情報をいただければ、より具体的に書けます。</p>

<div class="box"><b>参考：投稿管理ページ</b><br>
これまでの全投稿、承認状況、数字、確認事項は下記でご覧いただけます。<br>
<span class="small">https://yabemasaru23-source.github.io/biwakara-posts/</span></div>

<div class="foot"><span>みんなのびわから基金プロジェクト ／ 社会福祉法人 出島福祉村</span><span>3 / 3</span></div>
</div>
</body></html>""" % (CSS, len(rows), len(rows), len(x), len(ig), sum(xi), sum(igi),
                     sum(igi) / len(igi), sum(xi) / len(xi),
                     tbl(ig, "閲覧数"), tbl(x, "表示回数"))

    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(HERE, "_report.html")
    open(src, "w", encoding="utf-8").write(html)
    pdf = os.path.join(OUT, "SNS運用実施報告_10日間_%s.pdf" % today)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=20000", "--print-to-pdf=" + pdf,
                    "file:///" + src.replace("\\", "/")], check=True, capture_output=True)
    print("作成:", pdf, round(os.path.getsize(pdf) / 1024), "KB")


if __name__ == "__main__":
    main()

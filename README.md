# びわから基金 投稿デスク

社会福祉法人 出島福祉村「びわから基金」の SNS 投稿を、公開前に共有・確認するための静的サイト。

- 公開URL: https://yabemasaru23-source.github.io/biwakara-posts/
- 対象アカウント: X / Instagram ともに @biwakara_fund

## できること
- これから出す投稿（一発目3案・24時間テレビ連動4本・10日分のストーリー）を先に一覧で見る
- X と Instagram の文面を切り替えて確認する
- 文面をその場で直す
- 承認・要修正の状態をつける
- 投稿後にインプレッション・いいね等を記録し、投稿済み一覧で振り返る

## 注意
- **このサイトは自動投稿をしません。** 投稿ボタンを押すのは人です。
- 静的サイトのため、**入力した内容はその人のブラウザにだけ残ります**（GitHub Pages 版）。
  全員で同じ状態を共有したい場合は Claude Artifact 版を使ってください。
- 黄色の「公開前に確認すること」が残っている投稿は、裏取りが済むまで公開しないでください。

## 作り直し方
```
cd build
python gen_images.py   # posts.json の cap/tone から画像を再生成
python build.py        # template.html + posts.json + images → ../index.html
```
文面を直すときは `build/posts.json` を編集して `python build.py`。

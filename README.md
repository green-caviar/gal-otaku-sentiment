# gal-otaku-sentiment

自然言語処理 第2回 演習「ポジ／ネガ判定を2つのアプローチで」の提出物。オタク・ギャル風の SNS 投稿を、ルール（単語リスト）と LLM で判定して比べる。

- レポート：[docs/report.md](docs/report.md)
- ラベル付きデータ：[data/labeled_data.csv](data/labeled_data.csv)

## 構成

```text
data/labeled_data.csv   投稿と正解ラベル（id,text,label,note）
llm/prompt.txt          LLM に渡したプロンプト
llm/llm_preds.csv       LLM の答え
llm/extra_4.csv         追加の比較（投稿4）
src/run.py              ルールで判定し、ルールと LLM の正解数を数える
results/predictions.csv 正解と各手法の予測
docs/report.md          レポート
```

## 実行方法

```sh
python3 src/run.py
```

外部ライブラリは使わない（Python 3.9 以上の標準ライブラリだけ）。

# gal-otaku-sentiment

自然言語処理 第2回 演習「ポジ／ネガ判定を2つのアプローチで」の提出物。オタク・ギャル風の SNS 投稿12件を、ルール（単語リスト）と LLM（zero-shot、ペルソナ推論）で判定して比べる。

- レポート：[docs/report.md](docs/report.md)
- ラベル付きデータ：[data/labeled_data.csv](data/labeled_data.csv)

## 結果の要約

| 手法 | 正解数（12件中） |
|---|---|
| ルール（単語リスト） | 7 |
| LLM zero-shot（5回の平均） | 10.0 |
| LLM ペルソナ推論（5回の平均） | 11.0 |

## フォルダの地図

```text
README.md                  このファイル（概要・地図・列の意味・再現手順）
docs/report.md             レポート
data/labeled_data.csv      入力：自作の投稿と正解ラベル
prompts/zeroshot.txt       入力：LLM zero-shot のプロンプト
prompts/persona.txt        入力：LLM ペルソナ推論のプロンプト
outputs/zeroshot/runN.csv  記録：LLM zero-shot の N 回目の判定
outputs/persona/runN.csv   記録：LLM ペルソナ推論の N 回目の判定
outputs/persona/runN.md    記録：LLM ペルソナ推論の N 回目の推論過程（原文）
outputs/extra/post4_wara.csv  記録：追加の比較（投稿4の末尾に「笑」を付けた版）
src/run.py                 処理：ルールで判定し、全手法の正解数を数える
results/predictions.csv    結果：run.py が作る集計
```

| 役割 | 場所 | 扱い |
|---|---|---|
| 入力（人が作った） | `data/`、`prompts/` | 実験の前に固定した |
| 記録（LLM が出した） | `outputs/` | 生の出力。手で直していない |
| 処理 | `src/` | |
| 結果（コードが作った） | `results/` | `src/run.py` を実行すると作り直される |
| 説明 | `README.md`、`docs/` | |

## データの列

`data/labeled_data.csv`

| 列 | 意味 |
|---|---|
| `id` | 投稿の番号（1〜12） |
| `text` | 投稿の本文 |
| `label` | 正解ラベル。`pos`（ポジティブ）／`neg`（ネガティブ）。書き手の本当の気持ちで付けた |
| `note` | 投稿の型（否定語なのにポジ、皮肉、迷う投稿など）と、ラベルの判断理由 |

`outputs/*/runN.csv`

| 列 | 意味 |
|---|---|
| `id` | 投稿の番号 |
| `llm_raw` | LLM の答えの原文（「ポジ」／「ネガ」） |
| `llm_pred` | `llm_raw` を `pos`／`neg` に直したもの |

`results/predictions.csv`

| 列 | 意味 |
|---|---|
| `rule_pred` | ルールの予測 |
| `zeroshot_correct_of_5` | LLM zero-shot が5回中何回正解したか |
| `persona_correct_of_5` | LLM ペルソナ推論が5回中何回正解したか |

## 再現手順

```sh
python3 src/run.py
```

外部ライブラリは使わない（Python 3.9 以上の標準ライブラリだけ）。ルールの判定と集計を行い、`results/predictions.csv` を作る。LLM の判定は `outputs/` に保存した記録を読む（再実行はしない）。

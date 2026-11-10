"""オタク・ギャル風の投稿のポジ／ネガ判定：ルールと LLM の正解数を比べる。

使い方（リポジトリのルートで）:
    python3 src/run.py

入力:
    data/labeled_data.csv  id,text,label,note   （label は pos / neg）
    llm/llm_preds.csv      id,llm_raw,llm_pred  （llm_pred は pos / neg。LLM の答えを写す）
出力:
    画面に正解数と誤りの一覧
    results/predictions.csv  id,text,label,rule_pred,llm_pred
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "labeled_data.csv"
LLM = ROOT / "llm" / "llm_preds.csv"
OUT = ROOT / "results" / "predictions.csv"

LABELS = {"pos", "neg"}

# ルール（単語リスト）。どの語を入れるかは自分で決めて、README の「手法」に書く。
POS_WORDS = ["最高", "好き", "うれしい", "嬉しい", "ありがとう"]
NEG_WORDS = ["だるい", "だりー", "無理", "最悪", "しんどい", "死ぬ"]


def rule_classify(text: str) -> str:
    pos = sum(w in text for w in POS_WORDS)
    neg = sum(w in text for w in NEG_WORDS)
    if neg > pos:
        return "neg"
    return "pos"  # 同数・どちらも0件のときは pos（この扱いも README に書く）


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def evaluate(name: str, rows: list[dict], key: str) -> None:
    correct = sum(r[key] == r["label"] for r in rows)
    print(f"{name}: {correct}/{len(rows)} 正解")
    for r in rows:
        if r[key] != r["label"]:
            print(f"  誤り id={r['id']}: {r['text']}  正解={r['label']} 予測={r[key]}")


def main() -> None:
    rows = read_csv(DATA)
    if not rows:
        print(f"{DATA} にデータがない。投稿と正解ラベルを入れてから実行する。")
        return
    for r in rows:
        if r["label"] not in LABELS:
            raise SystemExit(f"id={r['id']} の label が pos / neg 以外: {r['label']!r}")
        r["rule_pred"] = rule_classify(r["text"])

    llm = {r["id"]: r["llm_pred"] for r in read_csv(LLM)}
    missing = [r["id"] for r in rows if r["id"] not in llm]
    for r in rows:
        r["llm_pred"] = llm.get(r["id"], "")

    evaluate("ルール", rows, "rule_pred")
    if missing:
        print(f"LLM: 答えがまだない id = {', '.join(missing)}（llm/llm_preds.csv に写す）")
    else:
        evaluate("LLM", rows, "llm_pred")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "text", "label", "rule_pred", "llm_pred"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})
    print(f"保存: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

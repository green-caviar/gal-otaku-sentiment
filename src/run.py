"""オタク・ギャル風の投稿のポジ／ネガ判定：ルールと LLM の正解数を比べる。

使い方（リポジトリのルートで）:
    python3 src/run.py

入力:
    data/labeled_data.csv  id,text,label,note   （label は pos / neg）
    llm/llm_preds.csv      id,llm_raw,llm_pred  （LLM zero-shot の答え。llm_pred は pos / neg）
    llm/persona_preds.csv  id,llm_raw,llm_pred  （LLM ペルソナ推論の答え）
出力:
    画面に正解数と誤りの一覧
    results/predictions.csv  id,text,label,rule_pred,llm_pred,persona_pred
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "labeled_data.csv"
# 比べる LLM の手法: (表示名, 予測ファイル, 出力の列名)
LLM_METHODS = [
    ("LLM zero-shot", ROOT / "llm" / "llm_preds.csv", "llm_pred"),
    ("LLM ペルソナ推論", ROOT / "llm" / "persona_preds.csv", "persona_pred"),
]
OUT = ROOT / "results" / "predictions.csv"

LABELS = {"pos", "neg"}

# ルール（単語リスト）。どの語を入れるかは自分で決めて、docs/report.md の「手法」に書く。
POS_WORDS = ["最高", "好き", "推す", "尊", "美し", "盛れ", "あげ", "優勝", "さすが"]
NEG_WORDS = ["死ぬ", "だりー", "だるい", "きも", "悪すぎ", "長すぎ", "えぐい", "キャパい", "会いたくない", "無理"]


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

    fields = ["id", "text", "label", "rule_pred"]
    evaluate("ルール", rows, "rule_pred")
    for name, path, key in LLM_METHODS:
        if not path.exists():
            print(f"{name}: {path.relative_to(ROOT)} がまだない")
            continue
        preds = {r["id"]: r["llm_pred"] for r in read_csv(path)}
        missing = [r["id"] for r in rows if r["id"] not in preds]
        for r in rows:
            r[key] = preds.get(r["id"], "")
        fields.append(key)
        if missing:
            print(f"{name}: 答えがまだない id = {', '.join(missing)}")
        else:
            evaluate(name, rows, key)

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})
    print(f"保存: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

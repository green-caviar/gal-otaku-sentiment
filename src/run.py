"""オタク・ギャル風の投稿のポジ／ネガ判定：ルールと LLM（2手法×複数回）の正解数を比べる。

使い方（リポジトリのルートで）:
    python3 src/run.py

入力:
    data/labeled_data.csv     id,text,label,note   （label は pos / neg）
    outputs/zeroshot/run*.csv   id,llm_raw,llm_pred  （LLM zero-shot の各回の答え）
    outputs/persona/run*.csv    id,llm_raw,llm_pred  （LLM ペルソナ推論の各回の答え）
出力:
    画面に、手法ごとの各回の正解数・平均・誤り
    results/predictions.csv   投稿ごとに、ルールの予測と、各 LLM 手法で正解した回数
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "labeled_data.csv"
# 比べる LLM の手法: (表示名, 各回の答えを置くフォルダ, 出力の列名)
LLM_METHODS = [
    ("LLM zero-shot", ROOT / "outputs" / "zeroshot", "zeroshot"),
    ("LLM ペルソナ推論", ROOT / "outputs" / "persona", "persona"),
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
    return "pos"  # 同数・どちらも0件のときは pos（この扱いもレポートに書く）


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    rows = read_csv(DATA)
    if not rows:
        print(f"{DATA} にデータがない。投稿と正解ラベルを入れてから実行する。")
        return
    n = len(rows)
    for r in rows:
        if r["label"] not in LABELS:
            raise SystemExit(f"id={r['id']} の label が pos / neg 以外: {r['label']!r}")
        r["rule_pred"] = rule_classify(r["text"])

    fields = ["id", "text", "label", "rule_pred"]
    rule_correct = sum(r["rule_pred"] == r["label"] for r in rows)
    print(f"ルール: {rule_correct}/{n} 正解")
    for r in rows:
        if r["rule_pred"] != r["label"]:
            print(f"  誤り id={r['id']}: {r['text']}  正解={r['label']} 予測={r['rule_pred']}")

    for name, folder, key in LLM_METHODS:
        runs = sorted(folder.glob("run*.csv"), key=lambda p: int(p.stem[3:]))
        if not runs:
            print(f"{name}: {folder.relative_to(ROOT)} に答えがまだない")
            continue
        k = len(runs)
        col = f"{key}_correct_of_{k}"
        for r in rows:
            r[col] = 0
        scores = []
        for path in runs:
            preds = {p["id"]: p["llm_pred"] for p in read_csv(path)}
            missing = [r["id"] for r in rows if r["id"] not in preds]
            if missing:
                raise SystemExit(f"{path.relative_to(ROOT)}: 答えがない id = {', '.join(missing)}")
            correct = 0
            for r in rows:
                if preds[r["id"]] == r["label"]:
                    r[col] += 1
                    correct += 1
            scores.append(correct)
        mean = sum(scores) / k
        print(f"{name}: 各回 {scores}（{k}回）、平均 {mean:.1f}/{n}（{mean / n:.1%}）、最小 {min(scores)}、最大 {max(scores)}")
        for r in rows:
            if r[col] < k:
                print(f"  誤りあり id={r['id']}: {r['text']}  正解={r['label']}  正解した回数 {r[col]}/{k}")
        fields.append(col)

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})
    print(f"保存: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

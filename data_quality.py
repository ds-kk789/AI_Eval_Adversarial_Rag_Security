import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Local embeddings (same model as rag_pipeline.py) — no API key/quota needed.
from langchain_huggingface import HuggingFaceEmbeddings

ROOT = Path(__file__).resolve().parent
DATASET_FILE = "golden_dataset.json"
REPORT_DIR = ROOT / "reports"
QUALITY_THRESHOLD = 0.95

SIMILARITY_FLAG_THRESHOLD = 0.90   # questions more similar than this = redundant
CONSISTENCY_MIN_THRESHOLD = 0.35   # question/answer embedding similarity below this = inconsistent

_embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def load_dataset(path=DATASET_FILE):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(text):
    text = text.strip().lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def check_duplicates(dataset):
    seen = {}
    duplicate_ids = set()

    for item in dataset:
        key = normalize(item["question"])

        if key in seen:
            duplicate_ids.add(item["id"])
            duplicate_ids.add(seen[key])
        else:
            seen[key] = item["id"]

    return duplicate_ids


def check_empty_fields(dataset):
    empty_ids = set()

    for item in dataset:
        question = (item.get("question") or "").strip()
        answer = (item.get("expected_answer") or "").strip()

        if not question or not answer:
            empty_ids.add(item["id"])

    return empty_ids


def check_similarity(dataset):
    questions = [item["question"] for item in dataset]
    embeddings = np.array(_embedding_model.embed_documents(questions))

    sim_matrix = cosine_similarity(embeddings)

    redundant_ids = set()

    for i in range(len(dataset)):
        for j in range(i + 1, len(dataset)):
            if sim_matrix[i][j] >= SIMILARITY_FLAG_THRESHOLD:
                redundant_ids.add(dataset[i]["id"])
                redundant_ids.add(dataset[j]["id"])

    return redundant_ids


def consistency_scores(dataset):
    """Per-item question/answer cosine similarity, plus the set below threshold."""
    questions = [item["question"] for item in dataset]
    answers = [item["expected_answer"] for item in dataset]

    q_embeddings = np.array(_embedding_model.embed_documents(questions))
    a_embeddings = np.array(_embedding_model.embed_documents(answers))

    scores = {}
    inconsistent_ids = set()
    for i, item in enumerate(dataset):
        score = float(cosine_similarity([q_embeddings[i]], [a_embeddings[i]])[0][0])
        scores[item["id"]] = score
        if score < CONSISTENCY_MIN_THRESHOLD:
            inconsistent_ids.add(item["id"])

    return inconsistent_ids, scores


def check_consistency(dataset):
    inconsistent_ids, _ = consistency_scores(dataset)
    return inconsistent_ids


def build_report(path=DATASET_FILE):
    """Run all four checks and return the full structured report (per-item detail
    included), so both the console summary and the HTML renderer can share one
    source of truth."""
    dataset = load_dataset(path)
    total = len(dataset)

    empty_ids = check_empty_fields(dataset)
    duplicate_ids = check_duplicates(dataset)
    similarity_ids = check_similarity(dataset)
    consistency_ids, consistency_by_id = consistency_scores(dataset)

    failing_ids = empty_ids | duplicate_ids | similarity_ids | consistency_ids
    passing_count = total - len(failing_ids)
    pass_rate = (passing_count / total) if total else 0.0

    items = []
    for item in dataset:
        item_id = item["id"]
        checks = {
            "empty_fields": item_id not in empty_ids,
            "duplicate": item_id not in duplicate_ids,
            "similarity": item_id not in similarity_ids,
            "consistency": item_id not in consistency_ids,
        }
        items.append({
            "id": item_id,
            "question": item.get("question", ""),
            "expected_answer": item.get("expected_answer", ""),
            "checks": checks,
            "consistency_score": round(consistency_by_id.get(item_id, 0.0), 4),
            "overall_pass": all(checks.values()),
        })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dataset_file": str(path),
        "total": total,
        "pass_rate": round(pass_rate, 4),
        "threshold": QUALITY_THRESHOLD,
        "thresholds": {
            "similarity_flag": SIMILARITY_FLAG_THRESHOLD,
            "consistency_min": CONSISTENCY_MIN_THRESHOLD,
        },
        "failing": {
            "empty_fields": sorted(empty_ids),
            "duplicate": sorted(duplicate_ids),
            "similarity": sorted(similarity_ids),
            "consistency": sorted(consistency_ids),
        },
        "items": items,
        "passed": pass_rate >= QUALITY_THRESHOLD,
    }


def run_validation(path=DATASET_FILE, write_report=True):
    report = build_report(path)
    total = report["total"]

    if total == 0:
        print("Dataset is empty.")
        return 0.0

    print("=" * 60)
    print("DATA QUALITY REPORT")
    print("=" * 60)
    print(f"Total entries: {total}")
    print(f"Empty field failures: {report['failing']['empty_fields'] or 'none'}")
    print(f"Duplicate question failures: {report['failing']['duplicate'] or 'none'}")
    print(f"Similarity (redundant) failures: {report['failing']['similarity'] or 'none'}")
    print(f"Consistency failures: {report['failing']['consistency'] or 'none'}")
    print("-" * 60)
    print(f"Pass rate: {report['pass_rate'] * 100:.2f}% (threshold: {QUALITY_THRESHOLD * 100:.0f}%)")

    if report["passed"]:
        print("RESULT: PASSED")
    else:
        print("RESULT: FAILED — update golden_dataset.json and rerun.")

    print("=" * 60)

    if write_report:
        REPORT_DIR.mkdir(exist_ok=True)
        out_path = REPORT_DIR / "data_quality_results.json"
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Report data: {out_path}")

    return report["pass_rate"]


if __name__ == "__main__":
    rate = run_validation()
    sys.exit(0 if rate >= QUALITY_THRESHOLD else 1)

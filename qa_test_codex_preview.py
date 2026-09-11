"""Preview the RAG evaluation through the signed-in Codex desktop runtime.

This is intentionally separate from the assignment's API evaluator (qa_test.py).
It does not change or replace the FastAPI/Groq implementation in main.py.
"""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from rag_pipeline import RAGPipeline


ROOT = Path(__file__).resolve().parent
DATASET_FILE = ROOT / "golden_dataset.json"
REPORT_DIR = ROOT / "reports"


def find_codex() -> str | None:
    """Prefer the desktop-bundled executable over a stale global npm shim."""
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        bundled = sorted(
            Path(local_app_data).glob("OpenAI/Codex/bin/*/codex.exe"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if bundled:
            return str(bundled[0])
    return shutil.which("codex")


def run_codex(prompt: str) -> str:
    codex = find_codex()
    if not codex:
        raise RuntimeError("The Codex command-line bridge was not found.")

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".txt", delete=False
    ) as output_file:
        output_path = Path(output_file.name)

    try:
        completed = subprocess.run(
            [
                codex,
                "exec",
                "-",
                "--ephemeral",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--output-last-message",
                str(output_path),
                "--color",
                "never",
            ],
            input=prompt,
            text=True,
            encoding="utf-8",
            capture_output=True,
            cwd=ROOT,
        )
        if completed.returncode != 0:
            details = (completed.stderr or completed.stdout).strip()
            raise RuntimeError(f"Codex invocation failed: {details}")
        return output_path.read_text(encoding="utf-8").strip()
    finally:
        output_path.unlink(missing_ok=True)


def answer_prompt(question: str, context: str) -> str:
    return f"""You are an e-commerce customer support assistant.

Answer the user's question using ONLY the provided context. If the answer is not
present, say exactly: I don't have enough information to answer that question.
Do not use tools, browse, inspect files, or add commentary. Return only the answer.

CONTEXT:
{context}

QUESTION:
{question}
"""


def judge_prompt(items: list[dict]) -> str:
    payload = [
        {
            "id": item["id"],
            "question": item["question"],
            "expected_answer": item["expected_answer"],
            "actual_answer": item["actual_answer"],
            "retrieved_context": item["retrieved_context"],
        }
        for item in items
    ]
    return f"""Act only as an impartial evaluator. Do not use tools or browse.

For every item, score the actual answer from 0.0 to 1.0 on:
- faithfulness: no contradiction or unsupported invention relative to the retrieved context
- answer_relevance: directly addresses the question
- correctness: matches the expected answer's meaning

Also give a concise reason. Return ONLY a valid JSON array. Each object must contain
exactly: id, faithfulness, answer_relevance, correctness, reason.

ITEMS:
{json.dumps(payload, ensure_ascii=False, indent=2)}
"""


def parse_judgments(raw: str) -> list[dict]:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
    value = json.loads(cleaned)
    if not isinstance(value, list):
        raise ValueError("Judge output was not a JSON array.")
    return value


def write_reports(results: list[dict], preview: bool) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(exist_ok=True)
    suffix = "_one_question" if preview else ""
    json_path = REPORT_DIR / f"codex_eval_results{suffix}.json"
    markdown_path = REPORT_DIR / f"codex_eval_report{suffix}.md"

    metrics = ("faithfulness", "answer_relevance", "correctness")
    averages = {
        metric: sum(float(item[metric]) for item in results) / len(results)
        for metric in metrics
    }
    output = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "evaluation_backend": "Codex desktop account runtime (preview)",
        "entries": len(results),
        "averages": averages,
        "results": results,
    }
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Codex Desktop RAG Evaluation Preview",
        "",
        "> This preview used the Codex desktop account runtime. The assignment's",
        "> FastAPI/Groq implementation was not changed, and these results are not",
        "> evidence that the deployed API endpoint itself was tested.",
        "",
        f"- Generated: {output['generated_at']}",
        f"- Evaluated entries: {len(results)}",
        f"- Faithfulness: {averages['faithfulness']:.2f}",
        f"- Answer relevance: {averages['answer_relevance']:.2f}",
        f"- Correctness: {averages['correctness']:.2f}",
        "",
        "## Per-question results",
        "",
    ]
    for item in results:
        lines.extend(
            [
                f"### {item['id']}. {item['question']}",
                "",
                f"**Expected:** {item['expected_answer']}",
                "",
                f"**Actual:** {item['actual_answer']}",
                "",
                (
                    "**Scores:** "
                    f"faithfulness {float(item['faithfulness']):.2f}; "
                    f"relevance {float(item['answer_relevance']):.2f}; "
                    f"correctness {float(item['correctness']):.2f}"
                ),
                "",
                f"**Judge note:** {item['reason']}",
                "",
            ]
        )
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit", type=int, default=None, help="Evaluate only the first N entries."
    )
    args = parser.parse_args()

    dataset = json.loads(DATASET_FILE.read_text(encoding="utf-8"))
    if args.limit is not None:
        dataset = dataset[: args.limit]
    if not dataset:
        raise RuntimeError("No dataset entries selected.")

    rag = RAGPipeline(knowledge_file=ROOT / "knowledge.txt", index_dir=ROOT / "data/faiss")
    generated = []
    for position, item in enumerate(dataset, 1):
        print(f"Generating answer {position}/{len(dataset)} (ID {item['id']})...")
        retrieved = rag.search(item["question"], top_k=3)
        context = "\n\n".join(result["chunk"] for result in retrieved)
        actual_answer = run_codex(answer_prompt(item["question"], context))
        generated.append({**item, "actual_answer": actual_answer, "retrieved_context": [r["chunk"] for r in retrieved]})

    print("Judging generated answers...")
    judgments = {item["id"]: item for item in parse_judgments(run_codex(judge_prompt(generated)))}
    results = [{**item, **judgments[item["id"]]} for item in generated]
    json_path, markdown_path = write_reports(results, preview=args.limit is not None)
    print(f"Raw results: {json_path}")
    print(f"Readable report: {markdown_path}")


if __name__ == "__main__":
    main()

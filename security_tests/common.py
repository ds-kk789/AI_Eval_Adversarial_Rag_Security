"""Shared config, HTTP+cache helper, and report writer for the security test scripts."""

import json
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
BASE_URL = "http://127.0.0.1:8002"
ASK_URL = f"{BASE_URL}/ask"

DATASET_FILE = ROOT / "attack_dataset.json"
REPORTS_DIR = ROOT / "reports"
CACHE_DIR = REPORTS_DIR / "_cache"


def load_dataset(path=DATASET_FILE):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_category(cases, category):
    return [case for case in cases if case["category"] == category]


def call_ask(test_id, prompt, replay=False, force=False):
    """POST prompt to /ask, with a per-test-id cache so reruns don't re-spend quota.

    - force=True: always call live and overwrite the cache.
    - replay=True: never call live; read from cache and error if it's missing.
    - default: reuse the cache if present, otherwise call live and cache the result.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{test_id}.json"

    if not force and cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        print(f"[{test_id}] cache hit, skipping API call")
        return cached["response"]

    if replay:
        raise FileNotFoundError(
            f"No cached response for {test_id}; run without --replay first to populate the cache."
        )

    print(f"[{test_id}] calling /ask (live)...")
    response = requests.post(ASK_URL, json={"question": prompt}, timeout=30)
    response.raise_for_status()
    answer = response.json()["answer"]

    cache_path.write_text(
        json.dumps({"test_id": test_id, "prompt": prompt, "response": answer}, indent=2),
        encoding="utf-8",
    )
    return answer


def generate_security_report(category_name, test_results, total_cases, success_attacks):
    """Generate a JSON security evaluation report containing
    vulnerability metrics and detailed test logs."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    vulnerability_rate = (success_attacks / total_cases * 100) if total_cases > 0 else 0.0

    report_payload = {
        "evaluation_category": category_name,
        "total_test_cases_processed": total_cases,
        "successful_exploits_detected": success_attacks,
        "vulnerability_compromise_rate": f"{vulnerability_rate:.2f}%",
        "detailed_logs": test_results,
    }

    slug = category_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    filename = REPORTS_DIR / f"{slug}_summary.json"

    with open(filename, "w", encoding="utf-8") as file_out:
        json.dump(report_payload, file_out, indent=4)

    print(f"Success! Security report written safely to {filename}")
    print(
        f"{total_cases} cases processed | {success_attacks} succeeded | "
        f"{vulnerability_rate:.2f}% compromise rate"
    )

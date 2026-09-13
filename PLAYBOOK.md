# Grading Playbook — Module 3b Adversarial Security Testing

This runs an end-to-end check of the RAG customer-support API plus the
adversarial security test suite (prompt injection, jailbreaking, PII
exfiltration) in `security_tests/`.

Estimated time: ~10 minutes setup + a few minutes per test run.

---

## 1. Prerequisites

- Python 3.10+
- A free Groq API key (you'll get your own in step 3 — do not ask the
  student for theirs)

## 2. Set up the environment

From the project root:

```bash
python -m venv aienv
```

Activate it:

```bash
# Windows (PowerShell)
.\aienv\Scripts\Activate.ps1

# Windows (Git Bash / cmd)
source aienv/Scripts/activate

# macOS / Linux
source aienv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 3. Configure your own API key

Create a `.env` file in the project root (it is git-ignored, so it won't
exist after cloning):

```
GROQ_API_KEY=your_own_key_here
```

Get a free key at https://console.groq.com/keys — no billing required, no
card needed.

## 4. Build the vector index

The FAISS index is git-ignored (it's a regenerable build artifact). Build it
from `knowledge.txt` once:

```bash
python rag_pipeline.py
```

You should see `FAISS index created successfully.` and a test Q&A printed
at the end — that confirms retrieval works before you touch the API layer.

## 5. Start the RAG API

In one terminal tab, start the FastAPI app on port 8002 (the security test
scripts are hardcoded to this port):

```bash
uvicorn main:app --port 8002
```

Leave this running. Wait for `Uvicorn running on http://127.0.0.1:8002` and
`FAISS index loaded.` before moving on — the first request also downloads a
small local embedding model, so the very first call may take a few extra
seconds.

## 6. Run the security test suites

In a **second** terminal tab (same venv activated, same project root), run
each of the three suites:

```bash
python security_tests/test_prompt_injection.py
python security_tests/test_jailbreak.py
python security_tests/test_pii_exfiltration.py
```

Each script prints a per-case pass/fail line, then writes a JSON report.

## 7. Where the results are

- `security_tests/reports/prompt_injection_summary.json`
- `security_tests/reports/jailbreak_summary.json`
- `security_tests/reports/pii_exfiltration_summary.json`

Each report contains: `evaluation_category`, `total_test_cases_processed`,
`successful_exploits_detected`, `vulnerability_compromise_rate`, and a
`detailed_logs` array with every test's `test_id`, `prompt`, `response`, and
`attack_succeeded` verdict.

Raw responses are also cached per-test in `security_tests/reports/_cache/`
so a script can be re-run without spending more API quota — see below.

## 8. Optional: re-run without spending API quota

Groq's free tier has a daily call limit. Every script supports:

```bash
python security_tests/test_prompt_injection.py --replay
```

`--replay` re-generates the report from the cached responses saved in step
6, with **zero** new API calls — useful for re-checking the report after the
fact. Add `--force` instead to ignore the cache and force fresh live calls.

## 9. Optional: Groq-quota-free fallback path

If the Groq free quota is exhausted before grading finishes, there is a
fallback runner that bypasses Groq entirely and answers via the local Codex
CLI bridge instead (requires the OpenAI Codex desktop app to be installed
and signed in — skip this step if that's not available):

```bash
python security_tests/run_via_codex_fallback.py
```

This is optional and not required for a normal grading pass — steps 1–7
above are the primary path.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `groq.AuthenticationError: ... expired_api_key` | Your key in `.env` is invalid/expired — get a new one at console.groq.com/keys |
| `ConnectionError` when running a test script | The FastAPI server (step 5) isn't running, or isn't on port 8002 |
| `faiss.read_index` / file-not-found error on startup | Run `python rag_pipeline.py` (step 4) to build the index first |
| Port 8002 already in use | Stop whatever is using it, or run `uvicorn main:app --port <other_port>` and update `BASE_URL` in `security_tests/common.py` to match |

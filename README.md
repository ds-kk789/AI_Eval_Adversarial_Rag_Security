# AI Eval Adversarial RAG Security

A FastAPI-based Retrieval-Augmented Generation (RAG) customer-support assistant for
an e-commerce use case, paired with a self-contained adversarial security-testing
suite that probes it for prompt injection, jailbreaking, and PII exfiltration.

## Architecture

```
knowledge.txt ──► rag_pipeline.py ──► data/faiss/ (FAISS index, local embeddings)
                                            │
                                            ▼
                               main.py (FastAPI, POST /ask)
                                            │
                                            ▼
                                   Groq (openai/gpt-oss-20b)
                                            │
                                            ▼
                              security_tests/ (adversarial test suite)
```

- **`main.py`** — FastAPI app exposing `POST /ask`. Retrieves top-3 relevant chunks
  from the FAISS index, builds a context-only prompt, and generates an answer via
  Groq's free-tier chat API.
- **`rag_pipeline.py`** — Chunks `knowledge.txt`, embeds it locally with
  `sentence-transformers/all-MiniLM-L6-v2` (no API key/quota needed), and builds/
  loads the FAISS index in `data/faiss/`.
- **`security_tests/`** — Adversarial evaluation suite (see below).
- **`qa_test.py`** + root `golden_dataset.json`** — a separate, earlier benign-QA
  eval harness (LLM-judge pattern), unrelated to the security suite.

## Security Testing Suite (`security_tests/`)

Deterministic (no LLM judge) adversarial evaluation across three attack categories,
run against the live `/ask` endpoint:

| Category | File | Validation |
|---|---|---|
| Prompt Injection | `test_prompt_injection.py` | Checks if a secret `canary` token the prompt tried to force was echoed back |
| Jailbreaking | `test_jailbreak.py` | Checks for `success_indicators` keywords, guarded against refusal phrases |
| PII Exfiltration | `test_pii_exfiltration.py` | Regex scan for email / phone / order-ID shaped strings in the response |

- **`attack_dataset.json`** — 15 adversarial test cases (5 per category).
- **`golden_dataset.json`** — 5 benign functional sanity-check prompts.
- **`common.py`** — shared `/ask` client with per-test-id response caching (so
  re-running a script or re-tuning the validators doesn't cost extra API quota) and
  the JSON report writer.
- **`run_via_codex_fallback.py`** — optional fallback that answers via the local
  Codex CLI bridge + direct FAISS retrieval instead of the live Groq-backed `/ask`
  endpoint, for use if the Groq free-tier quota is exhausted.
- **`reports/`** — generated JSON reports (`{category}_summary.json`), each with
  `evaluation_category`, `total_test_cases_processed`, `successful_exploits_detected`,
  `vulnerability_compromise_rate`, and per-test `detailed_logs`.

## Quick Start

```bash
python -m venv aienv
source aienv/Scripts/activate   # or aienv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

Create a `.env` file with your own free Groq key ([console.groq.com/keys](https://console.groq.com/keys)):

```
GROQ_API_KEY=your_own_key_here
```

Build the vector index, then start the API:

```bash
python rag_pipeline.py
uvicorn main:app --port 8002
```

In a second terminal, run the security suite:

```bash
python security_tests/test_prompt_injection.py
python security_tests/test_jailbreak.py
python security_tests/test_pii_exfiltration.py
```

Reports land in `security_tests/reports/`. Add `--replay` to re-generate a report
from cached responses with zero new API calls, or `--force` to bypass the cache.

For a fuller step-by-step walkthrough (including troubleshooting), see
[PLAYBOOK.md](PLAYBOOK.md).

## Results (last verified run)

| Category | Cases | Attacks Succeeded | Compromise Rate |
|---|---|---|---|
| Prompt Injection | 5 | 2 | 40.00% |
| Jailbreak | 5 | 0 | 0.00% |
| PII Exfiltration | 5 | 0 | 0.00% |

The two successful prompt-injection cases: one leaked the model's full system
prompt verbatim, the other complied with a secondary embedded instruction (append
a secret token) even while refusing the primary request. See
`security_tests/reports/*_summary.json` for full per-test logs.

## Tech Stack

FastAPI · Groq (`openai/gpt-oss-20b`) · FAISS · LangChain · sentence-transformers ·
Python `requests` + `re` for the security harness.

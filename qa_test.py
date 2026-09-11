import os
import sys
import json

import requests
from dotenv import load_dotenv
from groq import Groq

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

# API_URL = "http://127.0.0.1:8000/ask"
API_URL = "http://127.0.0.1:8001/ask"
DATASET_FILE = "golden_dataset.json"

judge_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_JUDGE_MODEL = "openai/gpt-oss-20b"

with open(DATASET_FILE, "r", encoding="utf-8") as file:
    dataset = json.load(file)


def judge_response(question, expected_answer, actual_answer):
    """Use Groq as an LLM-judge to score faithfulness, relevance, and
    correctness (0-1 each). These are semantic quality checks, unlike the
    mechanical checks in data_quality.py, so an LLM judge is the right tool."""

    prompt = f"""
You are evaluating an AI customer-support assistant's answer.

Question: {question}
Expected answer: {expected_answer}
Actual answer: {actual_answer}

Score the actual answer from 0.0 to 1.0 on each of these:
- faithfulness: does the actual answer avoid contradicting or making up
  information not supported by the expected answer?
- answer_relevance: does the actual answer directly address the question?
- correctness: does the actual answer match the expected answer's meaning?

Respond with ONLY a JSON object, no other text, in this exact form:
{{"faithfulness": 0.0, "answer_relevance": 0.0, "correctness": 0.0}}
"""

    completion = judge_client.chat.completions.create(
        model=GROQ_JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = completion.choices[0].message.content.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("Could not parse judge response:", raw)
        return {"faithfulness": None, "answer_relevance": None, "correctness": None}


results = []

for item in dataset:

    question = item["question"]

    response = requests.post(
        API_URL,
        json={"question": question}
    )

    response.raise_for_status()
    result = response.json()

    if "answer" not in result:
        raise RuntimeError(f"API returned no answer: {result}")

    actual_answer = result["answer"]

    print("=" * 70)
    print("ID:", item["id"])
    print("QUESTION:", question)
    print("EXPECTED:", item["expected_answer"])
    print("ACTUAL:", actual_answer)

    scores = judge_response(question, item["expected_answer"], actual_answer)
    print("SCORES:", scores)

    results.append({
        "id": item["id"],
        **scores
    })

print("\n" + "=" * 70)
print("METRICS SUMMARY")
print("=" * 70)

for metric in ("faithfulness", "answer_relevance", "correctness"):
    values = [r[metric] for r in results if r[metric] is not None]
    avg = sum(values) / len(values) if values else 0.0
    print(f"{metric}: {avg:.2f} (n={len(values)})")

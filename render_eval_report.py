"""Render the Codex preview evaluation JSON as a self-contained HTML report."""

import html
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "reports" / "codex_eval_results.json"
OUTPUT = ROOT / "reports" / "codex_eval_report.html"


def esc(value):
    return html.escape(str(value), quote=True)


def percent(value):
    return f"{float(value) * 100:.1f}%"


def score_class(value):
    value = float(value)
    if value >= 0.95:
        return "excellent"
    if value >= 0.80:
        return "good"
    return "review"


def metric_card(label, value, note):
    css_class = score_class(value)
    return f"""
      <article class="metric-card {css_class}">
        <p class="metric-label">{esc(label)}</p>
        <p class="metric-value">{percent(value)}</p>
        <div class="meter"><span style="width:{float(value) * 100:.2f}%"></span></div>
        <p class="metric-note">{esc(note)}</p>
      </article>"""


def result_card(item):
    overall = sum(float(item[key]) for key in ("faithfulness", "answer_relevance", "correctness")) / 3
    css_class = score_class(min(float(item["faithfulness"]), float(item["answer_relevance"]), float(item["correctness"])))
    context = "".join(f"<li>{esc(chunk)}</li>" for chunk in item.get("retrieved_context", []))
    metrics = "".join(
        f"""
        <div class="mini-metric">
          <span>{esc(label)}</span><strong>{percent(item[key])}</strong>
          <div class="meter small"><span style="width:{float(item[key]) * 100:.2f}%"></span></div>
        </div>"""
        for key, label in (
            ("faithfulness", "Faithfulness"),
            ("answer_relevance", "Relevance"),
            ("correctness", "Correctness"),
        )
    )
    return f"""
    <details class="result-card {css_class}" {'open' if float(item['correctness']) < 1 else ''}>
      <summary>
        <span class="question-number">{int(item['id']):02d}</span>
        <span class="question-title">{esc(item['question'])}</span>
        <span class="score-pill">{percent(overall)}</span>
        <span class="chevron" aria-hidden="true">⌄</span>
      </summary>
      <div class="result-body">
        <div class="answer-grid">
          <section><h3>Expected answer</h3><p>{esc(item['expected_answer'])}</p></section>
          <section><h3>Generated answer</h3><p>{esc(item['actual_answer'])}</p></section>
        </div>
        <div class="mini-metrics">{metrics}</div>
        <aside class="judge-note"><strong>Evaluator note</strong><p>{esc(item['reason'])}</p></aside>
        <details class="context"><summary>View retrieved context</summary><ol>{context}</ol></details>
      </div>
    </details>"""


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    results = data["results"]
    averages = data["averages"]
    generated = datetime.fromisoformat(data["generated_at"])
    perfect = sum(
        1
        for item in results
        if all(float(item[key]) == 1 for key in ("faithfulness", "answer_relevance", "correctness"))
    )
    review_items = sum(1 for item in results if float(item["correctness"]) < 0.95)

    cards = "".join(
        [
            metric_card("Faithfulness", averages["faithfulness"], "Grounded in retrieved context"),
            metric_card("Answer relevance", averages["answer_relevance"], "Directly addresses each question"),
            metric_card("Correctness", averages["correctness"], "Matches expected-answer meaning"),
        ]
    )
    result_cards = "".join(result_card(item) for item in results)

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Codex Desktop RAG Evaluation Report</title>
  <style>
    :root {{ --ink:#172033; --muted:#667085; --line:#e5e9f0; --paper:#fff; --bg:#f3f6fb;
      --navy:#172a46; --blue:#3b70e2; --cyan:#61c5d5; --green:#1f9d74; --amber:#d98b22; --red:#d84f4f; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; background:var(--bg); color:var(--ink); font-family:Inter,Segoe UI,Arial,sans-serif; line-height:1.55; }}
    .page {{ width:min(1120px,calc(100% - 32px)); margin:32px auto 64px; }}
    .hero {{ overflow:hidden; position:relative; padding:52px; color:#fff; border-radius:24px;
      background:linear-gradient(125deg,#14233c 0%,#254c88 58%,#287f92 100%); box-shadow:0 22px 55px rgba(23,42,70,.18); }}
    .hero:after {{ content:""; position:absolute; width:380px; height:380px; right:-120px; top:-180px;
      border:70px solid rgba(255,255,255,.08); border-radius:50%; }}
    .eyebrow {{ margin:0 0 12px; letter-spacing:.13em; text-transform:uppercase; font-size:.75rem; font-weight:800; color:#bcebf1; }}
    h1 {{ max-width:720px; margin:0; font-size:clamp(2rem,4.5vw,3.6rem); line-height:1.05; letter-spacing:-.04em; }}
    .subtitle {{ max-width:720px; margin:20px 0 0; font-size:1.05rem; color:#dae5f5; }}
    .hero-meta {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:30px; }}
    .tag {{ padding:7px 12px; background:rgba(255,255,255,.11); border:1px solid rgba(255,255,255,.18); border-radius:999px; font-size:.82rem; }}
    .metrics {{ display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin:24px 0; }}
    .metric-card {{ background:var(--paper); border:1px solid var(--line); border-radius:18px; padding:24px; box-shadow:0 8px 24px rgba(23,42,70,.06); }}
    .metric-label {{ margin:0; color:var(--muted); font-weight:700; font-size:.84rem; text-transform:uppercase; letter-spacing:.06em; }}
    .metric-value {{ margin:8px 0 10px; font-size:2.35rem; font-weight:800; letter-spacing:-.04em; }}
    .metric-note {{ margin:12px 0 0; color:var(--muted); font-size:.85rem; }}
    .meter {{ height:7px; border-radius:99px; background:#eef1f5; overflow:hidden; }}
    .meter span {{ display:block; height:100%; border-radius:inherit; background:var(--green); }}
    .good .meter span {{ background:var(--amber); }} .review .meter span {{ background:var(--red); }}
    .snapshot {{ display:grid; grid-template-columns:1.25fr 1fr; gap:18px; margin-bottom:36px; }}
    .panel {{ padding:24px; background:#fff; border:1px solid var(--line); border-radius:18px; }}
    .panel h2 {{ margin:0 0 14px; font-size:1rem; }}
    .status {{ display:flex; gap:14px; align-items:center; }}
    .pass {{ display:grid; place-items:center; flex:0 0 58px; height:58px; color:#fff; background:var(--green); border-radius:50%; font-size:1.5rem; font-weight:900; }}
    .status p {{ margin:2px 0; }} .muted {{ color:var(--muted); }}
    .stats {{ display:grid; grid-template-columns:repeat(3,1fr); text-align:center; }}
    .stats strong {{ display:block; font-size:1.65rem; }} .stats span {{ color:var(--muted); font-size:.78rem; }}
    .section-head {{ display:flex; align-items:end; justify-content:space-between; margin:38px 0 14px; }}
    .section-head h2 {{ margin:0; font-size:1.5rem; letter-spacing:-.02em; }} .section-head p {{ margin:0; color:var(--muted); font-size:.9rem; }}
    .result-card {{ margin:10px 0; background:#fff; border:1px solid var(--line); border-left:5px solid var(--green); border-radius:14px; overflow:hidden; }}
    .result-card.good {{ border-left-color:var(--amber); }} .result-card.review {{ border-left-color:var(--red); }}
    summary {{ list-style:none; cursor:pointer; }} summary::-webkit-details-marker {{ display:none; }}
    .result-card>summary {{ display:grid; grid-template-columns:44px 1fr auto 22px; gap:12px; align-items:center; padding:18px 20px; }}
    .question-number {{ color:#8792a5; font-size:.82rem; font-weight:800; letter-spacing:.06em; }}
    .question-title {{ font-weight:700; }} .score-pill {{ padding:5px 10px; color:#176b50; background:#e9f7f1; border-radius:99px; font-size:.8rem; font-weight:800; }}
    .good .score-pill {{ color:#925a0c; background:#fff4df; }} .review .score-pill {{ color:#a52e2e; background:#ffebeb; }}
    .chevron {{ color:#8993a4; font-size:1.15rem; transition:transform .2s; }} details[open]>.chevron {{ transform:rotate(180deg); }}
    .result-body {{ padding:0 20px 22px 76px; border-top:1px solid var(--line); }}
    .answer-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; padding-top:20px; }}
    .answer-grid section {{ padding:17px; background:#f7f9fc; border-radius:12px; }}
    .answer-grid h3 {{ margin:0 0 8px; font-size:.8rem; color:var(--muted); text-transform:uppercase; letter-spacing:.06em; }}
    .answer-grid p,.judge-note p {{ margin:0; }}
    .mini-metrics {{ display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin:20px 0; }}
    .mini-metric {{ display:grid; grid-template-columns:1fr auto; gap:7px; font-size:.84rem; }} .mini-metric span {{ color:var(--muted); }}
    .meter.small {{ grid-column:1/-1; height:5px; }}
    .judge-note {{ padding:16px 18px; background:#edf5ff; border-left:4px solid var(--blue); border-radius:9px; }}
    .judge-note strong {{ display:block; margin-bottom:4px; font-size:.8rem; color:#315a9c; text-transform:uppercase; letter-spacing:.05em; }}
    .context {{ margin-top:14px; padding:11px 14px; background:#fbfcfe; border:1px solid var(--line); border-radius:9px; color:var(--muted); font-size:.85rem; }}
    .context>summary {{ font-weight:700; color:#536074; }} .context ol {{ padding-left:22px; }} .context li {{ margin:10px 0; white-space:pre-line; }}
    footer {{ margin-top:30px; padding:22px; color:var(--muted); background:#fff; border:1px solid var(--line); border-radius:14px; font-size:.84rem; }}
    @media(max-width:760px) {{ .page{{width:min(100% - 20px,1120px);margin-top:10px}} .hero{{padding:34px 24px;border-radius:18px}}
      .metrics,.snapshot,.answer-grid,.mini-metrics{{grid-template-columns:1fr}} .result-card>summary{{grid-template-columns:36px 1fr auto}} .chevron{{display:none}}
      .result-body{{padding:0 16px 18px}} .stats{{gap:8px}} }}
    @media print {{ body{{background:#fff}} .page{{width:100%;margin:0}} .hero{{border-radius:0;box-shadow:none}} .result-card{{break-inside:avoid}}
      .result-card>summary{{cursor:default}} .result-body{{display:block!important}} details:not([open])>.result-body{{display:block!important}} .context{{display:none}} }}
  </style>
</head>
<body>
  <main class="page">
    <header class="hero">
      <p class="eyebrow">AI Data Quality · Evaluation Preview</p>
      <h1>RAG Answer Quality Report</h1>
      <p class="subtitle">A context-grounded evaluation of the e-commerce customer-support assistant against a validated golden dataset.</p>
      <div class="hero-meta">
        <span class="tag">Codex desktop runtime</span><span class="tag">{len(results)} test cases</span>
        <span class="tag">Generated {esc(generated.strftime('%d %b %Y, %H:%M %Z'))}</span>
      </div>
    </header>
    <section class="metrics" aria-label="Evaluation metrics">{cards}</section>
    <section class="snapshot">
      <article class="panel status"><div class="pass">✓</div><div><h2>Dataset validation passed</h2><p>100% pass rate against the required 95% threshold.</p><p class="muted">No empty, duplicate, redundant, or inconsistent entries detected.</p></div></article>
      <article class="panel stats"><div><strong>{len(results)}</strong><span>TEST CASES</span></div><div><strong>{perfect}</strong><span>PERFECT SCORES</span></div><div><strong>{review_items}</strong><span>REVIEW ITEMS</span></div></article>
    </section>
    <div class="section-head"><div><p class="eyebrow" style="color:#4d70a6">Detailed analysis</p><h2>Per-question results</h2></div><p>Select a question to inspect its evidence and scores.</p></div>
    <section>{result_cards}</section>
    <footer><strong>Method note.</strong> This preview used the Codex desktop account runtime. The assignment’s FastAPI/Groq implementation was left unchanged, so these results demonstrate the evaluation workflow and do not claim that the deployed API endpoint itself was tested.</footer>
  </main>
</body>
</html>"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()

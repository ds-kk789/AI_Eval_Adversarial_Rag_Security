"""Render data_quality.py's JSON output as a self-contained HTML report."""

import html
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "reports" / "data_quality_results.json"
OUTPUT = ROOT / "reports" / "data_quality_report.html"

CHECK_LABELS = (
    ("empty_fields", "Empty fields"),
    ("duplicate", "Duplicate"),
    ("similarity", "Similarity"),
    ("consistency", "Consistency"),
)


def esc(value):
    return html.escape(str(value), quote=True)


def percent(value):
    return f"{float(value) * 100:.1f}%"


def item_card(item):
    css_class = "pass" if item["overall_pass"] else "fail"
    checks = "".join(
        f"""
        <div class="check-pill {'pass' if item['checks'][key] else 'fail'}">
          <span>{esc(label)}</span><strong>{'OK' if item['checks'][key] else 'FLAG'}</strong>
        </div>"""
        for key, label in CHECK_LABELS
    )
    return f"""
    <details class="result-card {css_class}" {'' if item['overall_pass'] else 'open'}>
      <summary>
        <span class="question-number">{int(item['id']):02d}</span>
        <span class="question-title">{esc(item['question'])}</span>
        <span class="score-pill">{percent(item['consistency_score'])} consistency</span>
        <span class="chevron" aria-hidden="true">⌄</span>
      </summary>
      <div class="result-body">
        <section><h3>Expected answer</h3><p>{esc(item['expected_answer'])}</p></section>
        <div class="mini-metrics">{checks}</div>
      </div>
    </details>"""


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    items = data["items"]
    generated = datetime.fromisoformat(data["generated_at"])
    passed = data["passed"]
    total = data["total"]
    failing = data["failing"]
    fail_count = sum(1 for item in items if not item["overall_pass"])

    result_cards = "".join(item_card(item) for item in items)

    failing_lines = "".join(
        f"<li><strong>{esc(label)}:</strong> {', '.join(str(i) for i in failing[key]) or 'none'}</li>"
        for key, label in CHECK_LABELS
    )

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Data Quality Report</title>
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
    .snapshot {{ display:grid; grid-template-columns:1.25fr 1fr; gap:18px; margin:24px 0 36px; }}
    .panel {{ padding:24px; background:#fff; border:1px solid var(--line); border-radius:18px; }}
    .panel h2 {{ margin:0 0 14px; font-size:1rem; }}
    .status {{ display:flex; gap:14px; align-items:center; }}
    .badge {{ display:grid; place-items:center; flex:0 0 58px; height:58px; color:#fff; border-radius:50%; font-size:1.5rem; font-weight:900; }}
    .badge.pass {{ background:var(--green); }} .badge.fail {{ background:var(--red); }}
    .status p {{ margin:2px 0; }} .muted {{ color:var(--muted); }}
    .stats {{ display:grid; grid-template-columns:repeat(3,1fr); text-align:center; }}
    .stats strong {{ display:block; font-size:1.65rem; }} .stats span {{ color:var(--muted); font-size:.78rem; }}
    .failing-list {{ margin:0; padding-left:18px; color:var(--muted); font-size:.88rem; }}
    .failing-list li {{ margin:4px 0; }}
    .section-head {{ display:flex; align-items:end; justify-content:space-between; margin:38px 0 14px; }}
    .section-head h2 {{ margin:0; font-size:1.5rem; letter-spacing:-.02em; }} .section-head p {{ margin:0; color:var(--muted); font-size:.9rem; }}
    .result-card {{ margin:10px 0; background:#fff; border:1px solid var(--line); border-left:5px solid var(--green); border-radius:14px; overflow:hidden; }}
    .result-card.fail {{ border-left-color:var(--red); }}
    summary {{ list-style:none; cursor:pointer; }} summary::-webkit-details-marker {{ display:none; }}
    .result-card>summary {{ display:grid; grid-template-columns:44px 1fr auto 22px; gap:12px; align-items:center; padding:18px 20px; }}
    .question-number {{ color:#8792a5; font-size:.82rem; font-weight:800; letter-spacing:.06em; }}
    .question-title {{ font-weight:700; }} .score-pill {{ padding:5px 10px; color:#176b50; background:#e9f7f1; border-radius:99px; font-size:.8rem; font-weight:800; white-space:nowrap; }}
    .result-card.fail .score-pill {{ color:#a52e2e; background:#ffebeb; }}
    .chevron {{ color:#8993a4; font-size:1.15rem; transition:transform .2s; }} details[open]>.chevron {{ transform:rotate(180deg); }}
    .result-body {{ padding:0 20px 22px 76px; border-top:1px solid var(--line); }}
    .result-body section {{ padding:17px; margin-top:20px; background:#f7f9fc; border-radius:12px; }}
    .result-body h3 {{ margin:0 0 8px; font-size:.8rem; color:var(--muted); text-transform:uppercase; letter-spacing:.06em; }}
    .result-body p {{ margin:0; }}
    .mini-metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:18px 0 0; }}
    .check-pill {{ display:grid; grid-template-columns:1fr auto; gap:6px; padding:10px 12px; border-radius:10px; background:#eef7f1; font-size:.82rem; }}
    .check-pill.fail {{ background:#fdecec; }}
    .check-pill span {{ color:var(--muted); }} .check-pill strong {{ color:var(--green); }} .check-pill.fail strong {{ color:var(--red); }}
    footer {{ margin-top:30px; padding:22px; color:var(--muted); background:#fff; border:1px solid var(--line); border-radius:14px; font-size:.84rem; }}
    @media(max-width:760px) {{ .page{{width:min(100% - 20px,1120px);margin-top:10px}} .hero{{padding:34px 24px;border-radius:18px}}
      .snapshot,.mini-metrics{{grid-template-columns:1fr}} .result-card>summary{{grid-template-columns:36px 1fr auto}} .chevron{{display:none}}
      .result-body{{padding:0 16px 18px}} .stats{{gap:8px}} }}
    @media print {{ body{{background:#fff}} .page{{width:100%;margin:0}} .hero{{border-radius:0;box-shadow:none}} .result-card{{break-inside:avoid}}
      .result-card>summary{{cursor:default}} .result-body{{display:block!important}} details:not([open])>.result-body{{display:block!important}} }}
  </style>
</head>
<body>
  <main class="page">
    <header class="hero">
      <p class="eyebrow">AI Data Quality · Golden Dataset Validation</p>
      <h1>Data Quality Report</h1>
      <p class="subtitle">Duplicate, similarity, empty-field, and consistency checks against the golden dataset, ahead of the {esc(f"{data['threshold'] * 100:.0f}")}% quality gate the assignment requires before application testing.</p>
      <div class="hero-meta">
        <span class="tag">{total} dataset entries</span>
        <span class="tag">Generated {esc(generated.strftime('%d %b %Y, %H:%M %Z'))}</span>
      </div>
    </header>
    <section class="snapshot">
      <article class="panel status">
        <div class="badge {'pass' if passed else 'fail'}">{'✓' if passed else '✕'}</div>
        <div>
          <h2>{'Dataset validation passed' if passed else 'Dataset validation FAILED'}</h2>
          <p>{percent(data['pass_rate'])} pass rate against the required {esc(f"{data['threshold'] * 100:.0f}")}% threshold.</p>
          <p class="muted">Similarity flag ≥ {data['thresholds']['similarity_flag']}; consistency flag &lt; {data['thresholds']['consistency_min']}.</p>
        </div>
      </article>
      <article class="panel stats">
        <div><strong>{total}</strong><span>ENTRIES</span></div>
        <div><strong>{total - fail_count}</strong><span>PASSING</span></div>
        <div><strong>{fail_count}</strong><span>FLAGGED</span></div>
      </article>
    </section>
    <section class="panel">
      <h2>Failing IDs by check</h2>
      <ul class="failing-list">{failing_lines}</ul>
    </section>
    <div class="section-head"><div><p class="eyebrow" style="color:#4d70a6">Detailed analysis</p><h2>Per-entry results</h2></div><p>Flagged entries are expanded by default.</p></div>
    <section>{result_cards}</section>
    <footer><strong>Method note.</strong> Duplicate and empty-field checks are exact/string checks. Similarity and consistency both use local sentence-transformers embeddings (no API key, no quota) with cosine similarity — no LLM judge is involved in this report.</footer>
  </main>
</body>
</html>"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()

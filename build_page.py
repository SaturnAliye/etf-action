import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def fmt(value, default="-"):
    if value is None:
        return default
    return str(value)


def badge_class(decision: str) -> str:
    decision = (decision or "").upper()
    if decision == "BUY":
        return "buy"
    if decision == "WATCH":
        return "watch"
    return "no"


def trend_text(trend: str) -> str:
    mapping = {
        "UP": "偏强 / UP",
        "SIDE": "震荡 / SIDE",
        "DOWN": "偏弱 / DOWN",
    }
    return mapping.get((trend or "").upper(), fmt(trend))


def main():
    with open("result.json", "r", encoding="utf-8") as f:
        r = json.load(f)

    generated_at = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S GMT+8")
    decision = fmt(r.get("decision"))
    trend = fmt(r.get("week_trend"))
    cls = badge_class(decision)

    rows = [
        ("基金代码", r.get("symbol")),
        ("数据日期", r.get("date")),
        ("预测交易日", r.get("predict_date")),
        ("收盘价", r.get("close")),
        ("ATR%", f"{r.get('ATR_pct')}%"),
        ("BOLL 宽度", r.get("BOLL_width")),
        ("BOLL 位置", r.get("BOLL_pos")),
        ("MA20 斜率", r.get("MA20_slope")),
        ("量能比", r.get("VolRatio")),
        ("明日评分", r.get("score")),
        ("明日结论", decision),
        ("未来一周", trend_text(trend)),
    ]

    table_rows = "\n".join(
        f"<tr><th>{fmt(k)}</th><td>{fmt(v)}</td></tr>" for k, v in rows
    )

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>创业板 ETF 决策仪表盘</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card: #111827;
      --muted: #94a3b8;
      --text: #e5e7eb;
      --line: rgba(148, 163, 184, 0.25);
      --buy: #22c55e;
      --watch: #f59e0b;
      --no: #64748b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
      background: radial-gradient(circle at top, #1e293b 0, var(--bg) 55%);
      color: var(--text);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }}
    .wrap {{ width: min(920px, 100%); }}
    .card {{
      background: rgba(17, 24, 39, 0.9);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 28px;
      box-shadow: 0 24px 80px rgba(0,0,0,.35);
    }}
    .top {{
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: flex-start;
      margin-bottom: 22px;
    }}
    h1 {{ margin: 0 0 8px; font-size: clamp(26px, 4vw, 40px); }}
    .sub {{ color: var(--muted); line-height: 1.65; }}
    .badge {{
      white-space: nowrap;
      border-radius: 999px;
      padding: 10px 16px;
      font-weight: 800;
      letter-spacing: .5px;
      color: #06121f;
    }}
    .buy {{ background: var(--buy); }}
    .watch {{ background: var(--watch); }}
    .no {{ background: var(--no); color: #e5e7eb; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin: 22px 0;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      background: rgba(15, 23, 42, 0.72);
    }}
    .label {{ color: var(--muted); font-size: 14px; margin-bottom: 8px; }}
    .value {{ font-size: 26px; font-weight: 800; }}
    table {{ width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 18px; }}
    th, td {{ padding: 14px 16px; border-bottom: 1px solid var(--line); text-align: left; }}
    th {{ width: 38%; color: var(--muted); font-weight: 600; }}
    tr:last-child th, tr:last-child td {{ border-bottom: none; }}
    .note {{ margin-top: 18px; color: var(--muted); font-size: 13px; line-height: 1.7; }}
    @media (max-width: 720px) {{
      .top {{ flex-direction: column; }}
      .grid {{ grid-template-columns: 1fr; }}
      .badge {{ align-self: flex-start; }}
    }}
  </style>
</head>
<body>
  <main class="wrap">
    <section class="card">
      <div class="top">
        <div>
          <h1>📊 创业板 ETF 决策仪表盘</h1>
          <div class="sub">基于 T-1 数据自动生成，别再手动搬砖了，人类终于把重复劳动交给了机器。</div>
        </div>
        <div class="badge {cls}">{decision}</div>
      </div>

      <div class="grid">
        <div class="metric">
          <div class="label">明日评分</div>
          <div class="value">{fmt(r.get('score'))}</div>
        </div>
        <div class="metric">
          <div class="label">收盘价</div>
          <div class="value">{fmt(r.get('close'))}</div>
        </div>
        <div class="metric">
          <div class="label">未来一周</div>
          <div class="value">{trend_text(trend)}</div>
        </div>
      </div>

      <table>{table_rows}</table>

      <div class="note">
        更新时间：{generated_at}<br />
        提醒：这是量化辅助看板，不是投资保证书。市场要是讲道理，金融史会薄很多。
      </div>
    </section>
  </main>
</body>
</html>
"""

    site = Path("site")
    site.mkdir(exist_ok=True)
    (site / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()

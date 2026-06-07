from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "OnlineRetail.xlsx"
OUTPUT_FILE = PROJECT_ROOT / "dashboards" / "retail_dashboard.html"


def money(value: float) -> str:
    return f"${value:,.0f}"


def load_sales() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, engine="openpyxl")
    df = df.rename(
        columns={
            "InvoiceNo": "invoice_no",
            "StockCode": "stock_code",
            "Description": "description",
            "Quantity": "quantity",
            "InvoiceDate": "invoice_date",
            "UnitPrice": "unit_price",
            "CustomerID": "customer_id",
            "Country": "country",
        }
    )
    df["invoice_no"] = df["invoice_no"].astype(str)
    df["stock_code"] = df["stock_code"].astype(str).str.strip().str.upper()
    df["description"] = df["description"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")
    df["country"] = df["country"].astype(str).str.strip()

    return df[
        df["customer_id"].notna()
        & df["invoice_date"].notna()
        & ~df["invoice_no"].str.upper().str.startswith("C")
        & (df["quantity"] > 0)
        & (df["unit_price"] > 0)
    ].assign(sales_amount=lambda sales: sales["quantity"] * sales["unit_price"])


def build_payload(df: pd.DataFrame) -> dict:
    monthly = (
        df.assign(month=df["invoice_date"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False)["sales_amount"]
        .sum()
        .sort_values("month")
    )
    country = (
        df.groupby("country", as_index=False)
        .agg(revenue=("sales_amount", "sum"), orders=("invoice_no", "nunique"))
        .sort_values("revenue", ascending=False)
        .head(10)
    )
    products = (
        df.groupby(["stock_code", "description"], as_index=False)
        .agg(revenue=("sales_amount", "sum"), quantity=("quantity", "sum"))
        .sort_values("revenue", ascending=False)
        .head(10)
    )

    return {
        "kpis": {
            "revenue": money(df["sales_amount"].sum()),
            "orders": f"{df['invoice_no'].nunique():,}",
            "customers": f"{df['customer_id'].nunique():,}",
            "countries": f"{df['country'].nunique():,}",
        },
        "monthly": {
            "labels": monthly["month"].tolist(),
            "values": monthly["sales_amount"].round(2).tolist(),
        },
        "country": {
            "labels": country["country"].tolist(),
            "values": country["revenue"].round(2).tolist(),
            "orders": country["orders"].astype(int).tolist(),
        },
        "products": [
            {
                "stock_code": row.stock_code,
                "description": row.description,
                "quantity": int(row.quantity),
                "revenue": money(float(row.revenue)),
            }
            for row in products.itertuples(index=False)
        ],
    }


def render_dashboard(payload: dict) -> str:
    payload_json = json.dumps(payload)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Retail Analytics Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #667085;
      --line: #d9dee7;
      --blue: #2563eb;
      --green: #059669;
      --rose: #e11d48;
      --amber: #d97706;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, Segoe UI, Arial, sans-serif;
    }}
    header {{
      padding: 28px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: #fff;
    }}
    h1 {{
      margin: 0;
      font-size: 28px;
      font-weight: 760;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 14px;
    }}
    main {{
      padding: 24px 32px 36px;
      display: grid;
      gap: 20px;
    }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(4, minmax(160px, 1fr));
      gap: 14px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      min-width: 0;
    }}
    .label {{
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
      text-transform: uppercase;
    }}
    .value {{
      margin-top: 8px;
      font-size: 28px;
      font-weight: 780;
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.5fr) minmax(320px, 1fr);
      gap: 20px;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 17px;
      letter-spacing: 0;
    }}
    canvas {{
      width: 100%;
      height: 320px;
      display: block;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }}
    td:last-child, th:last-child {{
      text-align: right;
      white-space: nowrap;
    }}
    .product-code {{
      font-weight: 720;
      white-space: nowrap;
    }}
    @media (max-width: 920px) {{
      header, main {{ padding-left: 18px; padding-right: 18px; }}
      .kpis, .grid {{ grid-template-columns: 1fr; }}
      canvas {{ height: 280px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Retail Analytics Dashboard</h1>
    <div class="subtitle">Cleaned Online Retail sales summary from local Excel data</div>
  </header>
  <main>
    <section class="kpis">
      <div class="card"><div class="label">Revenue</div><div class="value" id="kpi-revenue"></div></div>
      <div class="card"><div class="label">Orders</div><div class="value" id="kpi-orders"></div></div>
      <div class="card"><div class="label">Customers</div><div class="value" id="kpi-customers"></div></div>
      <div class="card"><div class="label">Countries</div><div class="value" id="kpi-countries"></div></div>
    </section>
    <section class="grid">
      <div class="card">
        <h2>Monthly Revenue</h2>
        <canvas id="monthlyChart" width="900" height="320"></canvas>
      </div>
      <div class="card">
        <h2>Revenue by Country</h2>
        <canvas id="countryChart" width="520" height="320"></canvas>
      </div>
    </section>
    <section class="card">
      <h2>Top Products</h2>
      <table>
        <thead>
          <tr><th>Stock Code</th><th>Description</th><th>Qty Sold</th><th>Revenue</th></tr>
        </thead>
        <tbody id="products"></tbody>
      </table>
    </section>
  </main>
  <script>
    const data = {payload_json};
    const colors = ["#2563eb", "#059669", "#e11d48", "#d97706", "#7c3aed", "#0891b2", "#db2777", "#4f46e5", "#16a34a", "#ea580c"];

    document.getElementById("kpi-revenue").textContent = data.kpis.revenue;
    document.getElementById("kpi-orders").textContent = data.kpis.orders;
    document.getElementById("kpi-customers").textContent = data.kpis.customers;
    document.getElementById("kpi-countries").textContent = data.kpis.countries;

    document.getElementById("products").innerHTML = data.products.map(product => `
      <tr>
        <td class="product-code">${{product.stock_code}}</td>
        <td>${{product.description}}</td>
        <td>${{product.quantity.toLocaleString()}}</td>
        <td>${{product.revenue}}</td>
      </tr>
    `).join("");

    function money(value) {{
      return "$" + Math.round(value).toLocaleString();
    }}

    function setupCanvas(canvas) {{
      const ratio = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = Math.floor(rect.width * ratio);
      canvas.height = Math.floor(rect.height * ratio);
      const ctx = canvas.getContext("2d");
      ctx.scale(ratio, ratio);
      return {{ ctx, width: rect.width, height: rect.height }};
    }}

    function drawLineChart(canvas, labels, values) {{
      const {{ ctx, width, height }} = setupCanvas(canvas);
      const pad = {{ top: 18, right: 18, bottom: 48, left: 72 }};
      const plotW = width - pad.left - pad.right;
      const plotH = height - pad.top - pad.bottom;
      const max = Math.max(...values) * 1.12;
      ctx.clearRect(0, 0, width, height);
      ctx.strokeStyle = "#d9dee7";
      ctx.lineWidth = 1;
      ctx.font = "12px Segoe UI, Arial";
      ctx.fillStyle = "#667085";
      for (let i = 0; i <= 4; i++) {{
        const y = pad.top + plotH - (plotH * i / 4);
        const val = max * i / 4;
        ctx.beginPath();
        ctx.moveTo(pad.left, y);
        ctx.lineTo(width - pad.right, y);
        ctx.stroke();
        ctx.fillText(money(val), 8, y + 4);
      }}
      ctx.strokeStyle = "#2563eb";
      ctx.lineWidth = 3;
      ctx.beginPath();
      values.forEach((value, index) => {{
        const x = pad.left + (plotW * index / Math.max(values.length - 1, 1));
        const y = pad.top + plotH - (value / max * plotH);
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }});
      ctx.stroke();
      ctx.fillStyle = "#2563eb";
      values.forEach((value, index) => {{
        const x = pad.left + (plotW * index / Math.max(values.length - 1, 1));
        const y = pad.top + plotH - (value / max * plotH);
        ctx.beginPath();
        ctx.arc(x, y, 3.5, 0, Math.PI * 2);
        ctx.fill();
      }});
      ctx.fillStyle = "#667085";
      labels.forEach((label, index) => {{
        if (index % Math.ceil(labels.length / 8) !== 0) return;
        const x = pad.left + (plotW * index / Math.max(labels.length - 1, 1));
        ctx.save();
        ctx.translate(x - 16, height - 16);
        ctx.rotate(-0.55);
        ctx.fillText(label, 0, 0);
        ctx.restore();
      }});
    }}

    function drawBarChart(canvas, labels, values) {{
      const {{ ctx, width, height }} = setupCanvas(canvas);
      const pad = {{ top: 12, right: 18, bottom: 28, left: 132 }};
      const rowH = (height - pad.top - pad.bottom) / labels.length;
      const max = Math.max(...values) * 1.1;
      ctx.clearRect(0, 0, width, height);
      ctx.font = "12px Segoe UI, Arial";
      labels.forEach((label, index) => {{
        const y = pad.top + index * rowH;
        const barW = (width - pad.left - pad.right) * values[index] / max;
        ctx.fillStyle = "#667085";
        ctx.fillText(label.slice(0, 18), 8, y + rowH * 0.62);
        ctx.fillStyle = colors[index % colors.length];
        ctx.fillRect(pad.left, y + rowH * 0.2, barW, rowH * 0.5);
        ctx.fillStyle = "#17202a";
        ctx.fillText(money(values[index]), pad.left + barW + 8, y + rowH * 0.62);
      }});
    }}

    function drawAll() {{
      drawLineChart(document.getElementById("monthlyChart"), data.monthly.labels, data.monthly.values);
      drawBarChart(document.getElementById("countryChart"), data.country.labels, data.country.values);
    }}
    window.addEventListener("resize", drawAll);
    drawAll();
  </script>
</body>
</html>
"""


def main() -> None:
    payload = build_payload(load_sales())
    OUTPUT_FILE.write_text(render_dashboard(payload), encoding="utf-8")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()

"""Render customer documents (statements/letters) from templates + data."""
from __future__ import annotations

import html
import json
from pathlib import Path
from string import Template

REQUIRED_FIELDS = ("customer_id", "name", "account_no", "opening_balance", "transactions")


def load_customers(path: str | Path) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(record: dict) -> None:
    """Fail early on bad input instead of producing a wrong document."""
    missing = [f for f in REQUIRED_FIELDS if f not in record]
    if missing:
        raise ValueError(f"record {record.get('customer_id', '?')} missing fields: {missing}")


def mask_account(account_no: str) -> str:
    """Show only the last 4 digits, as real statements do."""
    return "X" * max(len(account_no) - 4, 0) + account_no[-4:]


def closing_balance(record: dict) -> float:
    return round(record["opening_balance"] + sum(t["amount"] for t in record["transactions"]), 2)


def render(template_text: str, record: dict) -> str:
    validate(record)
    rows = "\n".join(
        f"<tr><td>{html.escape(t['date'])}</td><td>{html.escape(t['description'])}</td>"
        f"<td class='amt'>{t['amount']:,.2f}</td></tr>"
        for t in record["transactions"]
    )
    values = {
        "customer_id": html.escape(str(record["customer_id"])),
        "name": html.escape(record["name"]),
        "account_masked": mask_account(str(record["account_no"])),
        "opening_balance": f"{record['opening_balance']:,.2f}",
        "closing_balance": f"{closing_balance(record):,.2f}",
        "rows": rows,
    }
    return Template(template_text).substitute(values)


def generate_all(data_path, template_path, out_dir) -> list[Path]:
    template_text = Path(template_path).read_text(encoding="utf-8")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    files = []
    for record in load_customers(data_path):
        target = out / f"{record['customer_id']}.html"
        target.write_text(render(template_text, record), encoding="utf-8")
        files.append(target)
    return files

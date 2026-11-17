import pytest

from docpipe import generator


def rec(**over):
    base = {"customer_id": "C1", "name": "A", "account_no": "1234567890",
            "opening_balance": 100.0,
            "transactions": [{"date": "2026-10-01", "description": "x", "amount": -40.0}]}
    base.update(over)
    return base


def test_mask_account():
    assert generator.mask_account("1234567890") == "XXXXXX7890"


def test_closing_balance():
    assert generator.closing_balance(rec()) == 60.0


def test_missing_field_rejected():
    r = rec()
    del r["name"]
    with pytest.raises(ValueError):
        generator.render("$name", r)


def test_html_is_escaped():
    txn = [{"date": "d", "description": "<b>", "amount": 1}]
    out = generator.render("$rows", rec(transactions=txn))
    assert "<b>" not in out and "&lt;b&gt;" in out


def test_generate_all(tmp_path):
    files = generator.generate_all("data/customers.json", "templates/statement.html", tmp_path)
    assert len(files) == 3 and all(f.exists() for f in files)

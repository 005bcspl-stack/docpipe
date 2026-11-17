"""Simulated delivery channels: print vendor batch and a SecureInbox portal."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def deliver_print(files: list[Path], out_dir: str | Path) -> Path:
    """Write an ordered print batch file, the way a print vendor expects it."""
    batch = Path(out_dir) / "print_batch.txt"
    lines = [f"{i:04d}|{Path(f).name}" for i, f in enumerate(sorted(files), start=1)]
    batch.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return batch


def deliver_secure_inbox(files: list[Path], out_dir: str | Path) -> list[Path]:
    """Copy each document to the customer's inbox folder and write a receipt."""
    inbox = Path(out_dir) / "secure_inbox"
    receipts = []
    for f in files:
        customer = Path(f).stem
        dest = inbox / customer
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest / Path(f).name)
        receipt = dest / "receipt.json"
        receipt.write_text(
            json.dumps(
                {"customer_id": customer, "document": Path(f).name,
                 "delivered_at": datetime.now(timezone.utc).isoformat()},
                indent=2,
            ),
            encoding="utf-8",
        )
        receipts.append(receipt)
    return receipts

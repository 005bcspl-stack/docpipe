"""Document integrity: SHA-256 manifest + optional HMAC signature."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path

MANIFEST = "manifest.json"


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _sign(payload: str, key: str) -> str:
    return hmac.new(key.encode(), payload.encode(), hashlib.sha256).hexdigest()


def build_manifest(files: list[Path], out_dir: str | Path) -> Path:
    out = Path(out_dir)
    entries = {Path(f).name: sha256_file(f) for f in sorted(files)}
    body = {"files": entries}
    key = os.environ.get("DOCPIPE_KEY")
    if key:
        body["signature"] = _sign(json.dumps(entries, sort_keys=True), key)
    path = out / MANIFEST
    path.write_text(json.dumps(body, indent=2), encoding="utf-8")
    return path


def verify_manifest(out_dir: str | Path) -> list[str]:
    """Return a list of problems; an empty list means everything is intact."""
    out = Path(out_dir)
    body = json.loads((out / MANIFEST).read_text(encoding="utf-8"))
    problems = []
    for name, expected in body["files"].items():
        f = out / name
        if not f.exists():
            problems.append(f"MISSING: {name}")
        elif sha256_file(f) != expected:
            problems.append(f"TAMPERED: {name}")
    key = os.environ.get("DOCPIPE_KEY")
    if key and "signature" in body:
        good = _sign(json.dumps(body["files"], sort_keys=True), key)
        if not hmac.compare_digest(good, body["signature"]):
            problems.append("MANIFEST SIGNATURE INVALID")
    return problems

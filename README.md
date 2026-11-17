# docpipe: Document Generation & Integrity Pipeline with CI/CD

A small project that mirrors how a bank produces customer communications:
**data in, documents out, integrity proven, delivered to multiple channels**, all
built, tested and shipped through an automated CI/CD pipeline.

## What it does
1. **Generate**: renders a personalised account statement per customer from a template + data
   (input validation, HTML escaping, account-number masking, balance calculation).
2. **Protect integrity**: writes a SHA-256 manifest of every document, with an optional HMAC
   signature (`DOCPIPE_KEY`). `verify` detects tampered or missing documents.
3. **Deliver**: simulates two channels, a print-vendor batch file and a SecureInbox-style
   portal folder with per-customer delivery receipts.

## Run it
```bash
python -m docpipe generate --out out     # create documents, manifest, deliveries
python -m docpipe verify --out out       # prints "All documents verified OK"
echo x >> out/C1001.html && python -m docpipe verify --out out   # now reports TAMPERED
```

## Test it
```bash
pip install -r requirements-dev.txt
ruff check .
pytest --cov=docpipe --cov-fail-under=85
```

## Docker
```bash
docker build -t docpipe .
docker run --rm -v "$PWD/out:/app/out" docpipe generate --out out
```

## CI/CD (`.github/workflows/ci.yml`)
| Stage | What happens |
|-------|--------------|
| Lint | `ruff` static checks |
| Test | `pytest` on Python 3.11 and 3.12, with an 85% coverage gate |
| Build | Docker image built on every push |
| Run | Pipeline executed inside the container, then `verify` confirms integrity |
| Artifact | Generated documents uploaded as a build artifact |

A failing test, lint error or integrity check stops the pipeline.

## Design choices (good talking points)
- **Fail early**: bad records are rejected before any document is produced.
- **Integrity as a first-class step**, not an afterthought.
- **Channel separation**: adding email or e-sign delivery means adding one function.
- **No external dependencies at runtime**, so images stay tiny and builds are reproducible.

## Possible next steps
PDF output, a queue for large batches, deployment via Kubernetes or a cloud function,
metrics and audit logging, a template versioning scheme.

## Sample data
All names and numbers in `data/` are fictional.

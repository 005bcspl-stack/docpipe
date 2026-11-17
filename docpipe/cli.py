from __future__ import annotations

import argparse
import sys

from . import channels, generator, integrity


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="docpipe")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="render documents, hash them, deliver")
    g.add_argument("--data", default="data/customers.json")
    g.add_argument("--template", default="templates/statement.html")
    g.add_argument("--out", default="out")

    v = sub.add_parser("verify", help="check documents against the manifest")
    v.add_argument("--out", default="out")

    args = p.parse_args(argv)

    if args.cmd == "generate":
        files = generator.generate_all(args.data, args.template, args.out)
        integrity.build_manifest(files, args.out)
        channels.deliver_print(files, args.out)
        channels.deliver_secure_inbox(files, args.out)
        print(f"Generated {len(files)} documents in {args.out}/")
        return 0

    problems = integrity.verify_manifest(args.out)
    if problems:
        print("\n".join(problems))
        return 1
    print("All documents verified OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

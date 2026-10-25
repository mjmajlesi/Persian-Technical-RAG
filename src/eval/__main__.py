"""Eval package CLI: run one model or compare frozen v2 reports."""

import sys

from .comparison import write_comparisons
from .run import main

if __name__ == "__main__":
    if sys.argv[1:2] == ["compare"]:
        if sys.argv[2:] != ["--set-version", "v2"]:
            raise SystemExit("usage: python -m src.eval compare --set-version v2")
        for json_path, md_path in write_comparisons():
            print(f"reports: {json_path} {md_path}")
    else:
        raise SystemExit(main())

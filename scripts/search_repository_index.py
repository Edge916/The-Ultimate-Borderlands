"""Read-only metadata search of the pinned repository inventory."""
import argparse
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--role", default="")
    parser.add_argument("--index", type=Path, default=Path(__file__).resolve().parents[1]/"docs/repository-file-index.json")
    args = parser.parse_args()
    index = json.loads(args.index.read_text(encoding="utf-8"))
    terms = args.query.casefold().split()
    matches = [f for f in index["files"] if (not args.role or f["role"] == args.role) and all(term in (f["path"]+" "+f["role"]).casefold() for term in terms)]
    print(json.dumps({"source_commit":index["source_commit"],"matches":matches,"search_scope":"File paths and roles only; inspect linked sources for content."},indent=2))

if __name__ == "__main__":
    main()

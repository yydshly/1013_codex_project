"""Generate the root README index, or check that it matches project metadata."""

import argparse
import sys

from project_index import update_readme


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without changing README")
    args = parser.parse_args()
    try:
        if not update_readme(check=args.check):
            print("README index or research workflow diagram is stale. Run: python scripts/update_index.py", file=sys.stderr)
            return 1
    except (ValueError, OSError) as error:
        print(f"Index validation failed: {error}", file=sys.stderr)
        return 1
    print("Project metadata and README index are valid." if args.check else "README index updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

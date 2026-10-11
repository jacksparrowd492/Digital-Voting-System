"""Load seed_data.sql into a SQLite database (voting.db by default).

Usage:
    python seed_db.py                  # seed only if the database has no proposals
    python seed_db.py --reset          # DESTRUCTIVE: delete all proposals/votes, then reseed
    python seed_db.py --db other.db    # target a different database file

Run `alembic upgrade head` first so the tables exist. This script is run by
setupdev.bat without --reset; it is never run when the application starts.
"""
import argparse
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "voting.db"
SEED_PATH = BASE_DIR / "seed_data.sql"


def seed(db_path: Path, reset: bool = False) -> int:
    conn = sqlite3.connect(db_path)
    try:
        try:
            count = conn.execute("SELECT COUNT(*) FROM proposals").fetchone()[0]
        except sqlite3.OperationalError:
            print(f"ERROR: proposals table not found in {db_path.name}. Run 'alembic upgrade head' first.")
            return 1

        if count and not reset:
            print(f"{db_path.name} already has {count} proposal(s); skipping seed. Use --reset to reseed.")
            return 0

        conn.executescript(SEED_PATH.read_text(encoding="utf-8"))
        print(f"Seeded {db_path.name} with sample proposals.")
        return 0
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reset", action="store_true", help="delete ALL existing proposals and votes before seeding")
    parser.add_argument("--db", type=Path, default=DB_PATH, help="database file (default: voting.db)")
    args = parser.parse_args()
    return seed(args.db.resolve(), reset=args.reset)


if __name__ == "__main__":
    sys.exit(main())

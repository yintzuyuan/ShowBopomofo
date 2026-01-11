#!/usr/bin/env python3
"""
Verify ShowChinesePhonetics SQLite database integrity.

This script performs various checks to ensure the database is valid and
contains expected data.

Checks:
1. Record count is within expected range (95,000 - 100,000)
2. All required columns exist
3. Sample characters have correct phonetic data
4. Multi-reading characters are properly formatted
5. Unicode format is valid (uppercase hex)
"""

import sqlite3
import sys
from pathlib import Path

# Expected record count range
MIN_RECORDS = 95000
MAX_RECORDS = 100000

# Sample characters to verify (unicode: expected phonetic patterns)
SAMPLE_CHECKS = {
    # Common characters
    "4E00": {"phonetic_contains": "ㄧ"},  # 一
    "4E2D": {"phonetic_contains": "ㄓㄨㄥ"},  # 中
    "6587": {"phonetic_contains": "ㄨㄣ"},  # 文
    "5B57": {"phonetic_contains": "ㄗ"},  # 字
    # Multi-reading character
    "884C": {"min_readings": 2},  # 行 (háng/xíng/etc.)
    # Extended characters (CJK Extension B)
    "20000": {"phonetic_contains": "ㄏㄜ"},  # 𠀀
}

# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent / (
    "Show Chinese Phonetics.glyphsReporter/Contents/Resources/"
    "ShowChinesePhonetics_data.db"
)


def verify_database(db_path: Path) -> tuple[bool, list[str]]:
    """
    Verify database integrity.

    Returns:
        (success, errors) tuple
    """
    errors = []

    if not db_path.exists():
        return False, [f"Database file not found: {db_path}"]

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check 1: Table exists and has expected columns
        cursor.execute("PRAGMA table_info(characters)")
        columns = {row[1] for row in cursor.fetchall()}
        expected_columns = {"unicode", "phonetic", "pinyin_han_dia", "pinyin_wei_dia"}

        missing_columns = expected_columns - columns
        if missing_columns:
            errors.append(f"Missing columns: {missing_columns}")

        # Check 2: Record count
        cursor.execute("SELECT COUNT(*) FROM characters")
        count = cursor.fetchone()[0]

        if count < MIN_RECORDS:
            errors.append(
                f"Record count too low: {count} (expected >= {MIN_RECORDS})"
            )
        elif count > MAX_RECORDS:
            errors.append(
                f"Record count too high: {count} (expected <= {MAX_RECORDS})"
            )
        else:
            print(f"Record count: {count} (OK)")

        # Check 3: Sample character verification
        for unicode_hex, checks in SAMPLE_CHECKS.items():
            cursor.execute(
                "SELECT phonetic FROM characters WHERE unicode = ?",
                (unicode_hex,),
            )
            result = cursor.fetchone()

            if not result:
                errors.append(f"Sample character U+{unicode_hex} not found")
                continue

            phonetic = result[0]

            if "phonetic_contains" in checks:
                if checks["phonetic_contains"] not in phonetic:
                    errors.append(
                        f"U+{unicode_hex}: phonetic '{phonetic}' does not contain "
                        f"'{checks['phonetic_contains']}'"
                    )

            if "min_readings" in checks:
                readings = phonetic.split(",")
                if len(readings) < checks["min_readings"]:
                    errors.append(
                        f"U+{unicode_hex}: expected at least {checks['min_readings']} "
                        f"readings, got {len(readings)}"
                    )

        # Check 4: Unicode format validation (sample)
        cursor.execute("SELECT unicode FROM characters LIMIT 100")
        for row in cursor.fetchall():
            unicode_hex = row[0]
            if not unicode_hex or not unicode_hex.isalnum():
                errors.append(f"Invalid unicode format: '{unicode_hex}'")
                break
            # Check uppercase
            if unicode_hex != unicode_hex.upper():
                errors.append(
                    f"Unicode not uppercase: '{unicode_hex}'"
                )
                break

        # Check 5: No empty phonetics
        cursor.execute(
            "SELECT COUNT(*) FROM characters WHERE phonetic IS NULL OR phonetic = ''"
        )
        empty_count = cursor.fetchone()[0]
        if empty_count > 0:
            errors.append(f"Found {empty_count} records with empty phonetic")

        conn.close()

    except sqlite3.Error as e:
        errors.append(f"SQLite error: {e}")

    success = len(errors) == 0
    return success, errors


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Verify ShowChinesePhonetics database integrity"
    )
    parser.add_argument(
        "database",
        type=Path,
        nargs="?",
        default=DEFAULT_DB_PATH,
        help="Path to database file",
    )

    args = parser.parse_args()

    print(f"Verifying database: {args.database}")
    print("-" * 60)

    success, errors = verify_database(args.database)

    if success:
        print("\nAll checks passed!")
        sys.exit(0)
    else:
        print("\nVerification FAILED:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()

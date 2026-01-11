#!/usr/bin/env python3
"""
Generate SQLite database from CNS11643-OpenData phonetics data.

This script downloads CNS11643 data and generates the ShowChinesePhonetics_data.db
SQLite database used by the Glyphs Reporter plugin.

Data sources:
- CNS_phonetic.txt: CNS code to Bopomofo (Zhuyin) mapping
- CNS_pinyin_2.txt: Bopomofo to Pinyin mapping (with tone marks)
- CNS2UNICODE_*.txt: CNS code to Unicode mapping

Output database schema:
    CREATE TABLE characters (
        unicode TEXT,
        phonetic TEXT,
        pinyin_han_dia TEXT,
        pinyin_wei_dia TEXT
    );
"""

import sqlite3
from collections import defaultdict
from pathlib import Path

import requests

# CNS11643-OpenData repository base URL
CNS_REPO_BASE = "https://raw.githubusercontent.com/yintzuyuan/CNS11643-OpenData/main"

# Data file paths (relative to repo)
CNS_FILES = {
    "phonetic": "Tables/Properties/CNS_phonetic.txt",
    "pinyin": "Tables/Properties/CNS_pinyin_2.txt",
    "unicode_bmp": "Tables/MapingTables/Unicode/CNS2UNICODE_Unicode%20BMP.txt",
    "unicode_2": "Tables/MapingTables/Unicode/CNS2UNICODE_Unicode%202.txt",
    "unicode_15": "Tables/MapingTables/Unicode/CNS2UNICODE_Unicode%2015.txt",
}

# Output database path (relative to script)
DEFAULT_OUTPUT_PATH = Path(__file__).parent.parent / (
    "Show Chinese Phonetics.glyphsReporter/Contents/Resources/"
    "ShowChinesePhonetics_data.db"
)


def download_file(url: str) -> str:
    """Download a file and return its content as string."""
    print(f"Downloading: {url}")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.text


def load_unicode_mapping(content: str) -> dict[str, str]:
    """
    Parse CNS2UNICODE file content.

    Format: CNS_CODE<tab>UNICODE_HEX

    Returns: {cns_code: unicode_hex}
    """
    mapping = {}
    for line in content.strip().split("\n"):
        if not line or "\t" not in line:
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            cns_code = parts[0].strip()
            unicode_hex = parts[1].strip().upper()
            mapping[cns_code] = unicode_hex
    return mapping


def load_phonetic_mapping(content: str) -> dict[str, list[str]]:
    """
    Parse CNS_phonetic.txt content.

    Format: CNS_CODE<tab>BOPOMOFO

    Returns: {cns_code: [bopomofo1, bopomofo2, ...]} (multiple readings per character)
    """
    mapping = defaultdict(list)
    for line in content.strip().split("\n"):
        if not line or "\t" not in line:
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            cns_code = parts[0].strip()
            bopomofo = parts[1].strip()
            if bopomofo and bopomofo not in mapping[cns_code]:
                mapping[cns_code].append(bopomofo)
    return dict(mapping)


def load_pinyin_mapping(content: str) -> dict[str, tuple[str, str]]:
    """
    Parse CNS_pinyin_2.txt content.

    Format: BOPOMOFO<tab>HANYU_PINYIN<tab>ZHUYIN2<tab>YALE<tab>WADE_GILES<tab>TONGYONG

    Returns: {bopomofo: (hanyu_pinyin, wade_giles)}
    """
    mapping = {}
    for line in content.strip().split("\n"):
        if not line or "\t" not in line:
            continue
        parts = line.split("\t")
        if len(parts) >= 5:
            bopomofo = parts[0].strip()
            hanyu_pinyin = parts[1].strip()
            wade_giles = parts[4].strip()
            mapping[bopomofo] = (hanyu_pinyin, wade_giles)
    return mapping


def generate_database(output_path: Path, cns_data_dir: Path | None = None) -> dict:
    """
    Generate the SQLite database from CNS data.

    Args:
        output_path: Path to output SQLite database
        cns_data_dir: Optional local directory containing CNS data files.
                      If None, downloads from GitHub.

    Returns:
        Statistics dict with record count and other info
    """
    # Load data (download if needed)
    if cns_data_dir:
        print(f"Loading data from local directory: {cns_data_dir}")

        def load_local(filename: str) -> str:
            # Handle URL-encoded filenames
            decoded = filename.replace("%20", " ")
            file_path = cns_data_dir / decoded
            return file_path.read_text(encoding="utf-8")

        phonetic_content = load_local(CNS_FILES["phonetic"])
        pinyin_content = load_local(CNS_FILES["pinyin"])
        unicode_bmp_content = load_local(CNS_FILES["unicode_bmp"])
        unicode_2_content = load_local(CNS_FILES["unicode_2"])
        unicode_15_content = load_local(CNS_FILES["unicode_15"])
    else:
        print("Downloading data from CNS11643-OpenData repository...")
        phonetic_content = download_file(f"{CNS_REPO_BASE}/{CNS_FILES['phonetic']}")
        pinyin_content = download_file(f"{CNS_REPO_BASE}/{CNS_FILES['pinyin']}")
        unicode_bmp_content = download_file(
            f"{CNS_REPO_BASE}/{CNS_FILES['unicode_bmp']}"
        )
        unicode_2_content = download_file(f"{CNS_REPO_BASE}/{CNS_FILES['unicode_2']}")
        unicode_15_content = download_file(f"{CNS_REPO_BASE}/{CNS_FILES['unicode_15']}")

    # Parse data files
    print("Parsing data files...")

    # Merge all Unicode mappings
    cns_to_unicode = {}
    cns_to_unicode.update(load_unicode_mapping(unicode_bmp_content))
    cns_to_unicode.update(load_unicode_mapping(unicode_2_content))
    cns_to_unicode.update(load_unicode_mapping(unicode_15_content))
    print(f"  Unicode mappings: {len(cns_to_unicode)}")

    # Load phonetic mapping
    cns_to_phonetic = load_phonetic_mapping(phonetic_content)
    print(f"  Phonetic entries: {len(cns_to_phonetic)}")

    # Load pinyin mapping
    bopomofo_to_pinyin = load_pinyin_mapping(pinyin_content)
    print(f"  Pinyin mappings: {len(bopomofo_to_pinyin)}")

    # Generate database records
    print("Generating database records...")
    records = []

    for cns_code, unicode_hex in cns_to_unicode.items():
        phonetics = cns_to_phonetic.get(cns_code, [])
        if not phonetics:
            continue

        # Convert each bopomofo to pinyin
        hanyu_pinyins = []
        wade_giles_pinyins = []

        for bopomofo in phonetics:
            if bopomofo in bopomofo_to_pinyin:
                hanyu, wade = bopomofo_to_pinyin[bopomofo]
                hanyu_pinyins.append(hanyu)
                wade_giles_pinyins.append(wade)
            else:
                # Fallback: keep empty if no pinyin mapping found
                hanyu_pinyins.append("")
                wade_giles_pinyins.append("")

        record = (
            unicode_hex,
            ",".join(phonetics),
            ",".join(hanyu_pinyins),
            ",".join(wade_giles_pinyins),
        )
        records.append(record)

    print(f"  Generated {len(records)} records")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to SQLite database
    print(f"Writing database to: {output_path}")

    # Remove existing database
    if output_path.exists():
        output_path.unlink()

    conn = sqlite3.connect(output_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE characters (
            unicode TEXT,
            phonetic TEXT,
            pinyin_han_dia TEXT,
            pinyin_wei_dia TEXT
        )
    """)

    # Insert records
    cursor.executemany(
        "INSERT INTO characters VALUES (?, ?, ?, ?)",
        records,
    )

    conn.commit()

    # Verify
    cursor.execute("SELECT COUNT(*) FROM characters")
    count = cursor.fetchone()[0]

    conn.close()

    stats = {
        "record_count": count,
        "unicode_mappings": len(cns_to_unicode),
        "phonetic_entries": len(cns_to_phonetic),
        "pinyin_mappings": len(bopomofo_to_pinyin),
        "output_path": str(output_path),
    }

    print(f"Database generated successfully: {count} records")
    return stats


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate ShowChinesePhonetics SQLite database from CNS11643 data"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output database path",
    )
    parser.add_argument(
        "--cns-data-dir",
        type=Path,
        help="Local directory containing CNS data files (downloads from GitHub if not specified)",
    )

    args = parser.parse_args()

    stats = generate_database(args.output, args.cns_data_dir)

    print("\nGeneration complete!")
    print(f"  Records: {stats['record_count']}")
    print(f"  Output: {stats['output_path']}")


if __name__ == "__main__":
    main()

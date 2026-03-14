# ShowHanPhonetics — Source Code

> **For users**: Please visit the [`main` branch](../../tree/main) to install the plugin via Glyphs Plugin Manager.

This branch contains the Objective-C source code for ShowHanPhonetics, a Glyphs 3 Reporter plugin that displays Han character phonetic annotations.

## Build

```bash
xcodebuild -project ShowHanPhonetics.xcodeproj -scheme ShowHanPhonetics -configuration Release build
```

The build output `Show Chinese Phonetics.glyphsReporter` can be found in `build/Release/`.

### Install to Glyphs

```bash
cp -R "build/Release/Show Chinese Phonetics.glyphsReporter" \
  ~/Library/Application\ Support/Glyphs\ 3/Plugins/
```

Restart Glyphs to load the plugin.

## Architecture

| File | Role |
|------|------|
| `ShowHanPhonetics.h/m` | UI logic, GlyphsReporter protocol, 8 display modes, context menu |
| `PhoneticDatabase.h/m` | Data access layer, SQLite queries, NSCache, EUI fallback |

### Database Schema

```sql
-- Phonetic readings (122,967 entries, WITHOUT ROWID)
CREATE TABLE readings (
    unicode TEXT PRIMARY KEY,
    zhuyin TEXT, pinyin TEXT, wade_giles TEXT,        -- CNS11643
    mandarin TEXT, cantonese TEXT, japanese_on TEXT,   -- Unicode Unihan
    japanese_kun TEXT, korean TEXT, vietnamese TEXT
) WITHOUT ROWID;

-- Kangxi / CJK radical mapping (348 entries, WITHOUT ROWID)
CREATE TABLE equiv_unified (
    unicode TEXT PRIMARY KEY,
    unified_unicode TEXT NOT NULL
) WITHOUT ROWID;
```

### Query Flow

1. Look up `readings` by Unicode code point
2. On miss → check `equiv_unified` for radical mapping
3. Re-query `readings` with the unified code point

## License

Copyright 2025 TzuYuan Yin — [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)

### Third-Party Data Sources

- **CNS11643** (Ministry of Digital Affairs, Taiwan) — [Government Open Data License](https://data.gov.tw/license)
- **Unicode Unihan Database** (Unicode Consortium) — [Unicode License](https://www.unicode.org/license.txt)

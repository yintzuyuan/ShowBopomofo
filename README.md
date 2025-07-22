# ShowChinesePhonetics

<div align="right">
  <a href="#ShowChinesePhonetics">繁體中文</a> | 
  <a href="#ShowChinesePhonetics-English">English</a>
</div>

---

ShowChinesePhonetics 是一個 [Glyphs.app](https://glyphsapp.com/) 外掛程式，用於在編輯字符時顯示對應的漢語發音標記。外掛程式支援三種顯示模式：

1. **注音符號（ㄅㄆㄇㄈ）** - 台灣標準注音符號
2. **漢語拼音（聲調符號）** - 現代標準中文拼音，帶聲調符號（如：píng yīn）
3. **威妥瑪拼音** - 威妥瑪拼音系統（Wade-Giles），包含數字聲調標記（如：p'ing2 yin1）

安裝後，可以透過選擇「顯示 > 顯示 漢語發音」來開啟或關閉此功能。您可以在字符上按右鍵選擇不同的顯示模式，或在系統偏好設定中設定快捷鍵。這對於處理中文字符特別有幫助，因為字符名稱通常不太直觀。

![ShowChinesePhonetics 截圖](ShowChinesePhonetics.gif)

當目前分頁的縮放比例低於 20% 時，發音標記將不會顯示。這樣可以避免在縮小檢視時干擾您的視線。

### 安裝方式

1. 在 Glyphs 的「視窗 > 外掛程式管理員」中一鍵安裝 Show Chinese Phonetics。
2. 重新啟動 Glyphs。

### 發音資料來源

本外掛程式使用的漢語發音資料來自中華民國（台灣）教育部「全字庫」，採用台灣標準發音，包含 95,766 個字符的完整發音資訊。資料儲存在 SQLite 資料庫中，包含：

- Unicode 編碼對應字符發音的資料表
- 支援注音符號、漢語拼音（聲調符號）和威妥瑪拼音三種格式
- 完整支援多音字，顯示所有可能的發音方式

資料庫確保了發音顯示的準確性、全面性和查詢效能。詳細的資料內容和格式說明可參考「全字庫屬性資料說明文件」。

### 系統需求

此外掛程式適用於 macOS Sonoma 上的 Glyphs 3.2.3 版本。我們只能在最新的應用程式和作業系統版本上進行測試，但它可能也適用於較早的版本。

### 授權條款

版權所有 © 2025 殷慈遠 (@yintzuyuan)。
基於 Rainer Erich Scheichelbauer (@mekkablue) 的範例程式碼開發。

本軟體依據 Apache License 2.0 授權條款授權；
除非符合授權條款，否則您不得使用本軟體。
您可以在以下網址取得授權條款的副本：

<http://www.apache.org/licenses/LICENSE-2.0>

有關詳細資訊，請參閱本儲存庫中包含的 License 檔案。

全字庫資料版權聲明：
本程式使用之全字庫資料是開放資料，並依據 [政府資料開放授權條款](https://data.gov.tw/license) 釋出。使用者於使用全字庫資料時，請註明來源為「數位發展部」。

---

# ShowChinesePhonetics (English)

ShowChinesePhonetics is a [Glyphs.app](https://glyphsapp.com/) plugin for displaying Chinese phonetic annotations when editing characters. The plugin supports three display modes:

1. **Bopomofo (ㄅㄆㄇㄈ)** - Taiwan standard phonetic symbols
2. **Hanyu Pinyin (Diacritics)** - Modern standard Chinese Pinyin with tone marks (e.g., píng yīn)
3. **Wade-Giles** - Wade-Giles romanization system with numerical tone markers (e.g., p'ing2 yin1)

After installation, you can turn it on or off by choosing "View > Show Chinese Phonetics". You can right-click on characters to switch between different display modes, or set a shortcut in System Preferences. This can be particularly helpful for handling Chinese characters, as glyph names are often not intuitive.

![ShowChinesePhonetics Screenshot](ShowChinesePhonetics.gif)

It will not display anything if the zoom of the current tab is below 20%. This prevents cluttering your view when zoomed out.

### Installation

1. One-click install Show Chinese Phonetics from "Window > Plugin Manager" in Glyphs.
2. Restart Glyphs.

### Phonetic Data Source

The Chinese phonetic data used in this plugin comes from the "CNS11643 Chinese Standard Interchange Code Mapping Table" provided by the Ministry of Education, Republic of China (Taiwan), using Taiwan standard pronunciations and containing complete phonetic information for 95,766 characters. The data is stored in an SQLite database, including:

- Unicode to character phonetic mapping table
- Support for Bopomofo, Hanyu Pinyin (diacritics), and Wade-Giles formats
- Full support for polyphones, displaying all possible pronunciations

The database ensures accuracy, comprehensiveness, and query performance for phonetic display. For detailed data content and format descriptions, please refer to the "CNS11643 Chinese Standard Interchange Code Mapping Table Documentation".

### Requirements

The plugin works in Glyphs 3.2.3 on macOS Sonoma. We can only test it in current app and OS versions, and perhaps it works on earlier versions too.

### License

Copyright 2025 Tzuyuan Yin (@yintzuyuan).
Based on sample code by Rainer Erich Scheichelbauer (@mekkablue).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

See the License file included in this repository for further details.

CNS11643 Data Copyright Notice:
The CNS11643 data used in this program is open data, released under the [Government Open Data License](https://data.gov.tw/license). When using the CNS11643 data, please attribute the source to "Ministry of Digital Affairs".

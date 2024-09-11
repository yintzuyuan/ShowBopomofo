# ShowBopomofo

<div align="right">
  <a href="#ShowBopomofo">繁體中文</a> | 
  <a href="#ShowBopomofo-English">English</a>
</div>

---

ShowBopomofo 是一個 [Glyphs.app](https://glyphsapp.com/) 外掛程式，用於在編輯字符時顯示對應的注音符號（ㄅㄆㄇㄈ）。安裝後，可以透過選擇「檢視 > 顯示 注音符號」來開啟或關閉此功能。這對於處理中文字符特別有幫助，因為字符名稱通常不太直觀。您可以在系統偏好設定中設定快捷鍵。

![ShowBopomofo 截圖](ShowBopomofo.gif)

當目前分頁的縮放比例低於 200% 時，注音符號將不會顯示。這樣可以避免在縮小檢視時干擾您的視線。

### 安裝方式

1. 在 Glyphs 的「視窗 > 外掛程式管理員」中一鍵安裝 Show Bopomofo。
2. 重新啟動 Glyphs。

### 注音資料來源

本外掛程式使用的注音和字符對應資料來自中華民國教育部「全字庫」。資料包含：

- Unicode 編碼對應 CNS 碼的對照表
- CNS 碼對應注音符號的資料表

這些資料確保了注音顯示的準確性和全面性。詳細的資料內容和格式說明可參考「全字庫屬性資料說明文件」。

### 系統需求

此外掛程式適用於 macOS Sonoma 上的 Glyphs 3.2.3 版本。我們只能在最新的應用程式和作業系統版本上進行測試，但它可能也適用於較早的版本。

### 授權條款

版權所有 © 2024 殷慈遠 (@yintzuyuan)。
基於 Rainer Erich Scheichelbauer (@mekkablue) 的範例程式碼開發。

本軟體依據 Apache License 2.0 授權條款授權；
除非符合授權條款，否則您不得使用本軟體。
您可以在以下網址取得授權條款的副本：

http://www.apache.org/licenses/LICENSE-2.0

有關詳細資訊，請參閱本儲存庫中包含的 License 檔案。

全字庫資料版權聲明：
本程式使用之全字庫資料是開放資料，並依據 [政府資料開放授權條款](https://data.gov.tw/license) 釋出。使用者於使用全字庫資料時，請註明來源為「數位發展部」。

---

# ShowBopomofo (English)

ShowBopomofo is a [Glyphs.app](https://glyphsapp.com/) plugin for displaying corresponding Bopomofo (ㄅㄆㄇㄈ) when editing characters. After installation, you can turn it on or off by choosing "View > Show Bopomofo". This can be particularly helpful for handling Chinese characters, as glyph names are often not intuitive. You can set a shortcut in System Preferences.

![ShowBopomofo Screenshot](ShowBopomofo.gif)

It will not display anything if the zoom of the current tab is below 200%. This prevents cluttering your view when zoomed out.

### Installation

1. One-click install Show Bopomofo from "Window > Plugin Manager" in Glyphs.
2. Restart Glyphs.

### Bopomofo Data Source

The Bopomofo and character correspondence data used in this plugin comes from the "CNS11643 Chinese Standard Interchange Code Mapping Table" provided by the Ministry of Education, Republic of China (Taiwan). The data includes:

- Unicode to CNS code mapping table
- CNS code to Bopomofo data table

These data ensure the accuracy and comprehensiveness of the Bopomofo display. For detailed data content and format descriptions, please refer to the "CNS11643 Chinese Standard Interchange Code Mapping Table Documentation".

### Requirements

The plugin works in Glyphs 3.2.3 on macOS Sonoma. We can only test it in current app and OS versions, and perhaps it works on earlier versions too.

### License

Copyright 2024 Tzuyuan Yin (@yintzuyuan).
Based on sample code by Rainer Erich Scheichelbauer (@mekkablue).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

See the License file included in this repository for further details.

CNS11643 Data Copyright Notice:
The CNS11643 data used in this program is open data, released under the [Government Open Data License](https://data.gov.tw/license). When using the CNS11643 data, please attribute the source to "Ministry of Digital Affairs".

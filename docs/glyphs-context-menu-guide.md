# Glyphs 外掛右鍵選單實作指南

## 概述

本指南說明如何在 Glyphs 外掛中實作右鍵選單功能，基於 ShowCrosshair 外掛的實作方式。

## 核心步骤

### 1. 匯入必要的模組

```python
from Cocoa import NSBezierPath, NSColor, NSImage, NSMenu, NSMenuItem, NSPoint, NSFont, NSFontAttributeName, NSForegroundColorAttributeName, NSAttributedString, NSSize, NSRect, NSMakeRect, NSLog, NSNotFound, NSOnState
```

### 2. 在 settings 方法中建立右鍵選單

```python
@objc.python_method
def settings(self):
    # 設定外掛名稱
    self.menuName = Glyphs.localize({
        'en': u'Your Plugin Name',
        'zh': u'你的外掛名稱',
    })
    
    # 註冊預設值
    Glyphs.registerDefault("com.yourname.yourplugin.setting1", 1)
    Glyphs.registerDefault("com.yourname.yourplugin.setting2", 0)
    
    # 建立右鍵選單
    self.generalContextMenus = self.buildContextMenus()
```

### 3. 實作 buildContextMenus 方法

```python
@objc.python_method
def buildContextMenus(self):
    # 建立圖示（可選）
    dot = None
    try:
        dot = NSImage.imageWithSystemSymbolName_accessibilityDescription_("circlebadge.fill", None)
        dot.setTemplate_(True)  # 讓圖示融入工具列
    except:
        pass
    
    # 建立選單項目列表
    contextMenus = []
    
    # 建立基本選單項目
    menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        Glyphs.localize({'en': "Menu Item Title", 'zh': "選單項目標題"}),
        self.menuAction,  # 對應的動作方法
        ""  # 快速鍵（空字串表示無快速鍵）
    )
    
    # 設定選單項目狀態（打勾）
    if Glyphs.defaults["com.yourname.yourplugin.setting1"]:
        menu.setState_(NSOnState)
    
    # 設定圖示
    if dot:
        menu.setOnStateImage_(dot)
    
    contextMenus.append({"menu": menu})
    
    # 建立分隔線
    contextMenus.append({"menu": NSMenuItem.separatorItem()})
    
    # 建立無法點擊的標題項目
    titleMenu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        Glyphs.localize({'en': "Section Title", 'zh': "章節標題"}),
        None,
        ""
    )
    titleMenu.setEnabled_(False)
    contextMenus.append({"menu": titleMenu})
    
    # 建立子選單
    subMenu = NSMenu.alloc().init()
    for item in contextMenus:
        item['menu'].setTarget_(self)  # 設定目標對象
        subMenu.addItem_(item['menu'])
    
    # 建立主選單項目
    mainMenu = NSMenuItem.alloc().init()
    mainMenu.setTitle_(Glyphs.localize({
        'en': u'Your Plugin Settings',
        'zh': u'你的外掛設定',
    }))
    mainMenu.setSubmenu_(subMenu)
    
    return [{'menu': mainMenu}]
```

### 4. 實作選單動作方法

```python
def menuAction(self):
    # 切換設定值
    self.toggleSetting("setting1")

@objc.python_method
def toggleSetting(self, prefName, extraParameter=None):
    if extraParameter is not None:
        Glyphs.defaults[f"com.yourname.yourplugin.{prefName}"] = extraParameter
    else:
        pref = f"com.yourname.yourplugin.{prefName}"
        oldSetting = Glyphs.boolDefaults[pref]
        Glyphs.defaults[pref] = int(not oldSetting)
    
    # 重新建立選單以更新狀態
    self.generalContextMenus = self.buildContextMenus()
```

## 進階功能

### 1. 多語言支援

使用 `Glyphs.localize()` 方法支援多語言：

```python
titleDict = {
    'en': "English Title",
    'zh': "中文標題",
    'ja': "日本語タイトル",
    'ko': "한국어 제목",
}
menu.setTitle_(Glyphs.localize(titleDict))
```

### 2. 動態選單項目

根據條件動態建立選單項目：

```python
# 基於某個條件建立不同的選單項目
if some_condition:
    menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        "Conditional Menu Item",
        self.conditionalAction,
        ""
    )
    contextMenus.append({"menu": menu})
```

### 3. 選單項目狀態管理

```python
# 設定選中狀態
if Glyphs.defaults["com.yourname.yourplugin.option"] == desired_value:
    menu.setState_(NSOnState)

# 設定圖示
if dot:
    menu.setOnStateImage_(dot)
```

## 注意事項

1. **命名規範**: 使用 `com.yourname.yourplugin.settingname` 格式命名設定項目
2. **目標設定**: 記得為每個選單項目設定 `setTarget_(self)`
3. **狀態更新**: 在設定變更後重新建立選單以更新顯示狀態
4. **錯誤處理**: 在建立圖示時使用 try/except 處理異常
5. **多語言**: 使用 `Glyphs.localize()` 確保多語言支援

## 完整範例

參考 ShowCrosshair 外掛的完整實作：
- 建立多層級選單結構
- 支援多語言
- 使用系統圖示
- 動態狀態管理
- 設定值持久化

這個指南提供了在 Glyphs 外掛中實作右鍵選單的完整方法，可以根據需要進行調整和擴展。
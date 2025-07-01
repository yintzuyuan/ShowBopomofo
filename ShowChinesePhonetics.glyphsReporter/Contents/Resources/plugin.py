# encoding: utf-8
from __future__ import division, print_function, unicode_literals

###########################################################################################################
#
#
#    一般外掛
#
#    閱讀文檔：
#    https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/General%20Plugin
#
#
###########################################################################################################


# https://developer.apple.com/library/content/documentation/Cocoa/Conceptual/CocoaViewsGuide/SubclassingNSView/SubclassingNSView.html

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from Cocoa import NSBezierPath, NSColor, NSImage, NSMenu, NSMenuItem, NSPoint, NSFont, NSFontAttributeName, NSForegroundColorAttributeName, NSAttributedString, NSSize, NSRect, NSMakeRect, NSLog, NSNotFound, NSOnState
import os
import sys
import re

# Add the cns_data_provider directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'cns_data_provider'))
from provider import CNSDataProvider

class ShowChinesePhonetics(ReporterPlugin):

    @objc.python_method
    def settings(self):
        # 設定外掛的選單名稱，支持多語言
        self.menuName = Glyphs.localize({
            'en': u'Chinese Phonetics',
            'zh-Hant': u'漢語發音',
            'zh-Hans': u'汉语发音',
            'ja': u'中国語発音',
            'ko': u'중국어 발음',
        })
        
        # 註冊預設值
        Glyphs.registerDefault("com.yintzuyuan.showphonetics.displayMode", 0)  # 0: 注音, 1: 拼音, 2: 拼音數字
        
        self.cns_provider = CNSDataProvider()
        self.load_data()  # 載入 Unicode 對應的注音符號
        
        # 建立右鍵選單
        self.generalContextMenus = self.buildContextMenus()

    @objc.python_method
    def start(self):
        # 移除可能導致錯誤的方法
        pass
    
    @objc.python_method
    def stop(self):
        # 關閉資料庫連線
        if hasattr(self, 'cns_provider') and self.cns_provider:
            self.cns_provider.disconnect()

    @objc.python_method
    def load_data(self):
        # 初始化 CNS 資料提供者連線
        try:
            if not self.cns_provider.connect():
                print("Failed to connect to CNS database")
        except Exception as e:
            print(f"Error connecting to CNS database: {str(e)}")

    @objc.python_method
    def get_resource_path(self, filename):
        return os.path.join(os.path.dirname(__file__), filename)

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
        
        # 顯示模式選項
        displayModes = [
            {'key': 0, 'name': {
                'en': 'Zhuyin (Bopomofo)', 
                'zh-Hant': '注音符號', 
                'zh-Hans': '注音符号',
                'ja': '注音符号', 
                'ko': '주음부호'
                }},
            {'key': 1, 'name': {
                'en': 'Pinyin (Diacritics)', 
                'zh-Hant': '拼音（聲調符號）', 
                'zh-Hans': '拼音（声调符号）',
                'ja': 'ピンイン（声調記号）', 
                'ko': '병음（성조부호）'
            }},
            {'key': 2, 'name': {
                'en': 'Pinyin (Numbers)', 
                'zh-Hant': '拼音（數字）', 
                'zh-Hans': '拼音（数字）',
                'ja': 'ピンイン（数字）', 
                'ko': '병음（숫자）'
            }},
        ]
        
        currentMode = Glyphs.defaults["com.yintzuyuan.showphonetics.displayMode"]
        
        for mode in displayModes:
            menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                Glyphs.localize(mode['name']),
                "switchDisplayMode:",
                ""
            )
            menu.setTag_(mode['key'])
            
            # 設定選中狀態
            if currentMode == mode['key']:
                menu.setState_(NSOnState)
                if dot:
                    menu.setOnStateImage_(dot)
            
            contextMenus.append({"menu": menu})
        
        # 建立子選單
        subMenu = NSMenu.alloc().init()
        for item in contextMenus:
            item['menu'].setTarget_(self)  # 設定目標對象
            subMenu.addItem_(item['menu'])
        
        # 建立主選單項目
        mainMenu = NSMenuItem.alloc().init()
        mainMenu.setTitle_(Glyphs.localize({
            'en': u'Chinese Phonetics Display Mode',
            'zh-Hant': u'漢語發音顯示模式',
            'zh-Hans': u'汉语发音显示模式',
            'ja': u'中国語発音表示モード',
            'ko': u'중국어 발음 표시 모드',
        }))
        mainMenu.setSubmenu_(subMenu)
        
        return [{'menu': mainMenu}]

    def switchDisplayMode_(self, sender):
        # 切換顯示模式
        newMode = sender.tag()
        Glyphs.defaults["com.yintzuyuan.showphonetics.displayMode"] = newMode
        
        # 重新建立選單以更新狀態
        self.generalContextMenus = self.buildContextMenus()
        
        # 強制重新繪製當前標籤頁
        try:
            font = Glyphs.font
            if font and font.currentTab:
                # 觸發重新繪製
                font.currentTab.forceRedraw()
                # 或者使用更新顯示的方法
                font.currentTab.updateInterface()
        except:
            pass


    @objc.python_method
    def drawTextAtPoint(self, text, textPosition, fontSize=10.0, fontColor=NSColor.blackColor(), align='topright'):
        # 在指定位置繪製文本
        try:
            alignment = {
                'topleft': 6, 'topcenter': 7, 'topright': 8,
                'left': 3, 'center': 4, 'right': 5,
                'bottomleft': 0, 'bottomcenter': 1, 'bottomright': 2,
            }
            
            textAlignment = alignment[align]  # 獲取對應的對齊方式
            currentZoom = self.getScale()  # 獲取目前縮放比例
            
            systemFont = NSFont.systemFontOfSize_(fontSize / currentZoom)  # 計算字體大小
            
            fontAttributes = {
                NSFontAttributeName: systemFont,
                NSForegroundColorAttributeName: fontColor,
            }
            displayText = NSAttributedString.alloc().initWithString_attributes_(text, fontAttributes)
            displayText.drawAtPoint_alignment_(textPosition, textAlignment)  # 繪製文本
        except Exception as e:
            print(e)  # 錯誤處理
            import traceback
            print(traceback.format_exc())
    
    @objc.python_method
    def foreground(self, layer):
        # 繪製前景層的注音符號
        try:
            glyph = layer.parent
            unicode_list = glyph.unicodes  # 獲取所有 Unicode 值
            
            # 如果字符名稱包含後綴，從字體中查找基礎字符的 Unicode 值
            if "." in glyph.name:
                nameWithoutSuffix = glyph.name[:glyph.name.find(".")]
                font = Glyphs.font
                baseGlyph = font.glyphs[nameWithoutSuffix]
                if baseGlyph and baseGlyph.unicodes:
                    unicode_list = baseGlyph.unicodes
            
            # 如果沒有 Unicode 值，使用原有的值作為回退
            if not unicode_list:
                unicode_list = glyph.unicodes
            
            if unicode_list:
                font = Glyphs.font
                tab = font.currentTab
                if tab and tab.scale > 0.1999:
                    master = layer.associatedFontMaster()
                    
                    # 計算 X 和 Y 座標
                    x = layer.width
                    y = max(master.ascender, layer.bounds.origin.y + layer.bounds.size.height + 50.0)
                    
                    fontSize = 24.0  # 字體大小
                    fontColor = NSColor.colorWithRed_green_blue_alpha_(0.5, 0.8, 0.9, 1.0)  # 字體顏色
                    
                    all_bopomofo = set()  # 使用集合自動去除重複的注音符號
                    for unicode_hex in unicode_list:
                        try:
                            # 確保資料庫連線
                            if not self.cns_provider.conn:
                                if not self.cns_provider.connect():
                                    continue
                            
                            # 查詢 SQLite 資料庫取得發音資料
                            cursor = self.cns_provider.conn.cursor()
                            cursor.execute("SELECT phonetic, pinyin_han, pinyin_han_dia FROM characters WHERE unicode = ?", (unicode_hex.upper(),))
                            row = cursor.fetchone()
                            if row and row['phonetic']:
                                # 根據顯示模式獲取對應的發音資料
                                displayMode = Glyphs.defaults["com.yintzuyuan.showphonetics.displayMode"]
                                
                                if displayMode == 0:  # 注音符號
                                    phonetic_data = row['phonetic']
                                elif displayMode == 1:  # 拼音（聲調符號）
                                    phonetic_data = row['pinyin_han_dia'] if row['pinyin_han_dia'] else row['phonetic']
                                elif displayMode == 2:  # 拼音（數字）
                                    phonetic_data = row['pinyin_han'] if row['pinyin_han'] else row['phonetic']
                                else:
                                    phonetic_data = row['phonetic']
                                
                                phonetic_list = [p.strip() for p in phonetic_data.split(',') if p.strip()]
                                all_bopomofo.update(phonetic_list)
                        except Exception as e:
                            print(f"Error querying database for {unicode_hex}: {str(e)}")
                    
                    if all_bopomofo:
                        # 將所有唯一的發音以半形逗號連接（已經根據顯示模式獲取了正確格式）
                        phonetics_text = ", ".join(sorted(all_bopomofo))  # 排序以保持一致的顯示順序
                        
                        self.drawTextAtPoint(
                            phonetics_text, 
                            NSPoint(x, y),
                            fontSize=fontSize, 
                            fontColor=fontColor,
                            align="bottomright",
                        )
        except Exception as e:
            print(f"Error in foreground method: {str(e)}")  # 錯誤處理
            import traceback
            print(traceback.format_exc())

    @objc.python_method
    def __file__(self):
        """Please leave this method unchanged"""
        return __file__

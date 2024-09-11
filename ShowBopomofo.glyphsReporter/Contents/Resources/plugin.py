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
import os

class ShowBopomofo(ReporterPlugin):

    @objc.python_method
    def settings(self):
        # 設定外掛的選單名稱，支持多語言
        self.menuName = Glyphs.localize({
            'en': u'Bopomofo',
            'zh': u'注音符號',
            'ja': u'注音符号',
            'ko': u'주음부호',
        })
        self.unicode_to_bopomofo = {}
        self.load_data()  # 載入 Unicode 對應的注音符號

    @objc.python_method
    def start(self):
        # 移除可能導致錯誤的方法
        pass

    @objc.python_method
    def load_data(self):
        # 載入 Unicode 對應的注音符號資料
        try:
            with open(self.get_resource_path('unicode_to_bopomofo.txt'), 'r', encoding='utf-8') as f:
                for line in f:
                    unicode, bopomofo = line.strip().split('\t')
                    self.unicode_to_bopomofo[unicode] = bopomofo.split(',')
        except Exception as e:
            print(f"Error reading unicode_to_bopomofo.txt: {str(e)}")  # 錯誤處理

    @objc.python_method
    def get_resource_path(self, filename):
        return os.path.join(os.path.dirname(__file__), filename)

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
            
            if not unicode_list and "." in glyph.name:
                nameWithoutSuffix = glyph.name[:glyph.name.find(".")]
                glyphInfo = Glyphs.glyphInfoForName(nameWithoutSuffix)
                if glyphInfo:
                    unicode_list = glyphInfo.unicodes
            
            if unicode_list:
                font = Glyphs.font
                tab = font.currentTab
                if tab and tab.scale > 0.1999:
                    master = layer.associatedFontMaster()
                    
                    # 計算 X 和 Y 座標
                    x = layer.bounds.origin.x + layer.bounds.size.width + 50.0
                    y = max(master.ascender, layer.bounds.origin.y + layer.bounds.size.height + 50.0)
                    
                    fontSize = 24.0  # 字體大小
                    fontColor = NSColor.colorWithRed_green_blue_alpha_(0.5, 0.8, 0.9, 1.0)  # 字體顏色
                    
                    all_bopomofo = set()  # 使用集合自動去除重複的注音符號
                    for unicode_hex in unicode_list:
                        bopomofo_list = self.unicode_to_bopomofo.get(unicode_hex, [])
                        all_bopomofo.update(bopomofo_list)  # 更新集合
                    
                    if all_bopomofo:
                        # 將所有唯一的注音以半形逗號連接
                        bopomofo_text = ", ".join(sorted(all_bopomofo))  # 排序以保持一致的顯示順序
                        
                        self.drawTextAtPoint(
                            bopomofo_text, 
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
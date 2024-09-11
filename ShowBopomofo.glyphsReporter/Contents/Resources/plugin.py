# encoding: utf-8
from __future__ import division, print_function, unicode_literals

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
import os

class ShowBopomofo(ReporterPlugin):

    @objc.python_method
    def settings(self):
        self.menuName = Glyphs.localize({
            'en': u'Bopomofo',
            'zh': u'注音符號',
            'ja': u'注音符号',
            'ko': u'주음부호',
        })
        self.unicode_to_bopomofo = {}
        self.load_data()

    @objc.python_method
    def start(self):
        # 移除可能導致錯誤的方法
        pass

    @objc.python_method
    def load_data(self):
        try:
            with open(self.get_resource_path('unicode_to_bopomofo.txt'), 'r', encoding='utf-8') as f:
                for line in f:
                    unicode, bopomofo = line.strip().split('\t')
                    self.unicode_to_bopomofo[unicode] = bopomofo.split(',')
        except Exception as e:
            print(f"Error reading unicode_to_bopomofo.txt: {str(e)}")

    @objc.python_method
    def get_resource_path(self, filename):
        return os.path.join(os.path.dirname(__file__), filename)

    @objc.python_method
    def drawTextAtPoint(self, text, textPosition, fontSize=10.0, fontColor=NSColor.blackColor(), align='topright'):
        try:
            alignment = {
                'topleft': 6, 'topcenter': 7, 'topright': 8,
                'left': 3, 'center': 4, 'right': 5,
                'bottomleft': 0, 'bottomcenter': 1, 'bottomright': 2,
            }
            
            textAlignment = alignment[align]
            currentZoom = self.getScale()
            
            systemFont = NSFont.systemFontOfSize_(fontSize / currentZoom)
            
            fontAttributes = {
                NSFontAttributeName: systemFont,
                NSForegroundColorAttributeName: fontColor,
            }
            displayText = NSAttributedString.alloc().initWithString_attributes_(text, fontAttributes)
            displayText.drawAtPoint_alignment_(textPosition, textAlignment)
        except Exception as e:
            print(e)
            import traceback
            print(traceback.format_exc())
    
    @objc.python_method
    def foreground(self, layer):
        try:
            glyph = layer.parent
            character = glyph.glyphInfo.unicharString()
            
            if not character and "." in glyph.name:
                nameWithoutSuffix = glyph.name[:glyph.name.find(".")]
                glyphInfo = Glyphs.glyphInfoForName(nameWithoutSuffix)
                character = glyphInfo.unicharString()
                
            if character:
                unicode_hex = f"{ord(character):04X}"
                bopomofo_list = self.unicode_to_bopomofo.get(unicode_hex, [])
                if bopomofo_list:
                    font = Glyphs.font
                    tab = font.currentTab
                    if tab and tab.scale > 0.1999:
                        master = layer.associatedFontMaster()
                        
                        # X 座標：設定在字符的右側
                        x = layer.bounds.origin.x + layer.bounds.size.width + 50.0
                        
                        # Y 座標：使用與原始程式碼相同的邏輯
                        y = max(master.ascender, layer.bounds.origin.y + layer.bounds.size.height + 50.0)
                        
                        # 調整參數：字體大小
                        fontSize = 24.0
                        
                        fontColor = NSColor.colorWithRed_green_blue_alpha_(0.5, 0.8, 0.9, 1.0)
                        
                        # 將多個注音以全形逗號連接
                        bopomofo_text = ", ".join(bopomofo_list)
                        
                        self.drawTextAtPoint(
                            bopomofo_text, 
                            NSPoint(x, y),
                            fontSize=fontSize, 
                            fontColor=fontColor,
                            align="bottomright",
                        )
        except Exception as e:
            print(f"Error in foreground method: {str(e)}")
            import traceback
            print(traceback.format_exc())

    @objc.python_method
    def __file__(self):
        """Please leave this method unchanged"""
        return __file__
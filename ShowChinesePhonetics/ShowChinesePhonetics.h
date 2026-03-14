//
//  ShowChinesePhonetics.h
//  ShowChinesePhonetics
//
//  Created by 殷慈遠 on 2025/11/13.
//
//

#import <Cocoa/Cocoa.h>
#import <GlyphsCore/GlyphsReporterProtocol.h>

// 發音顯示模式
typedef NS_ENUM(NSInteger, PhoneticDisplayMode) {
	// ── CNS11643 來源 ──
	PhoneticDisplayModeZhuyin = 0,        // 注音符號
	PhoneticDisplayModePinyin = 1,        // 漢語拼音（CNS）
	PhoneticDisplayModeWadeGiles = 2,     // 威妥瑪拼音
	// ── Unicode Unihan 來源 ──
	PhoneticDisplayModeMandarin = 3,      // 漢語拼音（Unihan）
	PhoneticDisplayModeCantonese = 4,     // 粵語拼音
	PhoneticDisplayModeJapanese = 5,      // 日本語（音讀+訓讀）
	PhoneticDisplayModeKorean = 6,        // 韓語
	PhoneticDisplayModeVietnamese = 7,    // 越南語
};

@interface ShowChinesePhonetics : NSObject <GlyphsReporter>

@end

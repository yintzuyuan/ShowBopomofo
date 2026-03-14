//
//  ShowChinesePhonetics.m
//  ShowChinesePhonetics
//
//  Created by 殷慈遠 on 2025/11/13.
//
//

#import "ShowChinesePhonetics.h"

// Debug logging macro
#ifdef DEBUG
	#define DLog(fmt, ...) NSLog((@"[ShowChinesePhonetics] %s " fmt), __PRETTY_FUNCTION__, ##__VA_ARGS__)
#else
	#define DLog(fmt, ...) // 正式版本不輸出
#endif

// Localization macro for plugin bundle
#define LocalizedString(key, comment) \
	[[NSBundle bundleForClass:[self class]] localizedStringForKey:(key) value:@"" table:nil]
#import "PhoneticDatabase.h"
#import <GlyphsCore/GlyphsFilterProtocol.h>
#import <GlyphsCore/GSFilterPlugin.h>
#import <GlyphsCore/GSGlyph.h>
#import <GlyphsCore/GSLayer.h>
#import <GlyphsCore/GSFont.h>
#import <GlyphsCore/GSFontMaster.h>
#import <GlyphsCore/GSComponent.h>

// UserDefaults key
static NSString * const kPhoneticDisplayModeKey = @"com.YinTzuYuan.ShowChinesePhonetics.displayMode";
static NSString * const kOldPhoneticDisplayModeKeys[] = {
	@"com.YinTzuYuan.ShowHanPhonetics.displayMode",
	@"com.YinTzuYuan.ShowHanziPhonetics.displayMode",
};

@implementation ShowChinesePhonetics {
	__weak NSViewController <GSGlyphEditViewControllerProtocol> *_editViewController;
	PhoneticDatabase *_database;
	PhoneticDisplayMode _displayMode;
}

// Synthesize controller property from GlyphsReporter protocol
@synthesize controller = _editViewController;

#pragma mark - Initialization

- (instancetype)init {
	self = [super init];
	if (self) {
		// UserDefaults 遷移：舊 key → 新 key（一次性，優先遷移最近的 key）
		NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
		NSUInteger oldKeyCount = sizeof(kOldPhoneticDisplayModeKeys) / sizeof(kOldPhoneticDisplayModeKeys[0]);
		for (NSUInteger i = 0; i < oldKeyCount; i++) {
			NSString *oldKey = kOldPhoneticDisplayModeKeys[i];
			if ([defaults objectForKey:oldKey] != nil) {
				NSInteger oldMode = [defaults integerForKey:oldKey];
				[defaults setInteger:oldMode forKey:kPhoneticDisplayModeKey];
				[defaults removeObjectForKey:oldKey];
				DLog("Migrated displayMode from %@: %ld", oldKey, (long)oldMode);
				break;
			}
		}

		// 載入使用者偏好（首次啟動時根據系統語言選擇預設模式）
		if ([defaults objectForKey:kPhoneticDisplayModeKey] != nil) {
			_displayMode = [defaults integerForKey:kPhoneticDisplayModeKey];
		} else {
			_displayMode = [self defaultDisplayModeForSystemLanguage];
			[defaults setInteger:_displayMode forKey:kPhoneticDisplayModeKey];
			[defaults synchronize];
			DLog("Set default display mode %ld for language: %@",
				 (long)_displayMode, [NSLocale preferredLanguages].firstObject);
		}

		// 初始化資料庫（從 Info.plist 讀取名稱，或使用預設值）
		NSBundle *bundle = [NSBundle bundleForClass:[self class]];
		NSString *dbName = [bundle objectForInfoDictionaryKey:@"PhoneticDatabaseName"];
		if (!dbName || dbName.length == 0) {
			dbName = @"ShowChinesePhonetics_data";
		}
		_database = [[PhoneticDatabase alloc] initWithDatabaseName:dbName];

		if (!_database.isConnected) {
			DLog("Warning: Database not connected!");
		}
	}
	return self;
}

- (void)dealloc {
	[_database closeDatabase];
}

#pragma mark - Phonetic Lookup

- (NSString *)phoneticStringForGlyph:(GSGlyph *)glyph {
	if (!glyph) {
		DLog("No glyph");
		return nil;
	}

	NSString *unicodeHex = nil;

	// 策略 1：優先使用 glyph.unicode 屬性（最可靠）
	unicodeHex = [self unicodeHexFromGlyph:glyph];

	// 策略 2：備援方案 - 從字符名稱提取 Unicode
	if (!unicodeHex) {
		unicodeHex = [self unicodeHexFromGlyphName:glyph.name];
		if (unicodeHex) {
			DLog("Extracted Unicode from name: %@ -> %@", glyph.name, unicodeHex);
		}
	}

	// 策略 3：最終備援 - 查找基礎字符（處理變體字符）
	if (!unicodeHex && [glyph.name containsString:@"."]) {
		NSString *baseName = [[glyph.name componentsSeparatedByString:@"."] firstObject];
		if (baseName && baseName.length > 0) {
			GSFont *font = glyph.parent;
			if (font) {
				GSGlyph *baseGlyph = [font glyphForName:baseName];
				if (baseGlyph) {
					unicodeHex = [self unicodeHexFromGlyph:baseGlyph];
					if (!unicodeHex) {
						unicodeHex = [self unicodeHexFromGlyphName:baseGlyph.name];
					}
					if (unicodeHex) {
						DLog("Using base glyph: %@ -> %@ (U+%@)", glyph.name, baseName, unicodeHex);
					}
				}
			}
		}
	}

	if (!unicodeHex) {
		DLog("No Unicode found for glyph: %@", glyph.name);
		return nil;
	}

	DLog("Looking up glyph: %@ (U+%@)", glyph.name, unicodeHex);

	NSDictionary *phoneticData = [_database phoneticDataForUnicode:unicodeHex];
	if (!phoneticData) {
		DLog("No phonetic data found for %@", unicodeHex);
		return nil;
	}

	NSString *result = [self selectPhoneticFromData:phoneticData];
	DLog("Returning phonetic: %@ (mode: %ld)", result, (long)_displayMode);

	return result;
}

- (nullable NSString *)unicodeHexFromGlyph:(GSGlyph *)glyph {
	NSString *unicode = glyph.unicode;

	if (!unicode) {
		DLog("Glyph %@ has no unicode", glyph.name);
		return nil;
	}

	// 處理 NSNumber 類型（舊版 Glyphs 相容性）
	if ([unicode isKindOfClass:[NSNumber class]]) {
		unsigned int unicodeInt = [(NSNumber *)unicode unsignedIntValue];
		if (unicodeInt == 0) {
			DLog("Glyph %@ has zero unicode value", glyph.name);
			return nil;
		}
		return [NSString stringWithFormat:@"%04X", unicodeInt];
	}

	if (unicode.length == 0) {
		DLog("Glyph %@ has empty unicode string", glyph.name);
		return nil;
	}

	NSString *unicodeHex = [unicode uppercaseString];
	if ([unicodeHex hasPrefix:@"U+"]) {
		unicodeHex = [unicodeHex substringFromIndex:2];
	}

	NSRegularExpression *hexRegex = [NSRegularExpression
		regularExpressionWithPattern:@"^[0-9A-F]{4,6}$"
		options:0
		error:nil];

	NSRange range = NSMakeRange(0, unicodeHex.length);
	if ([hexRegex numberOfMatchesInString:unicodeHex options:0 range:range] == 0) {
		DLog("Glyph %@ has invalid unicode format: %@", glyph.name, unicodeHex);
		return nil;
	}

	return unicodeHex;
}

- (nullable NSString *)unicodeHexFromGlyphName:(NSString *)glyphName {
	if (!glyphName || glyphName.length == 0) {
		return nil;
	}

	NSString *pattern = @"(?:^|\\.)(?:uni([0-9A-Fa-f]{4})|u([0-9A-Fa-f]{5,6}))(?:\\.|$|-)";
	NSRegularExpression *regex = [NSRegularExpression
		regularExpressionWithPattern:pattern
		options:0
		error:nil];

	NSTextCheckingResult *match = [regex firstMatchInString:glyphName
													options:0
													  range:NSMakeRange(0, glyphName.length)];

	if (!match) {
		return nil;
	}

	NSRange uni4Range = [match rangeAtIndex:1];
	NSRange u5_6Range = [match rangeAtIndex:2];

	if (uni4Range.location != NSNotFound && uni4Range.length > 0) {
		return [[glyphName substringWithRange:uni4Range] uppercaseString];
	} else if (u5_6Range.location != NSNotFound && u5_6Range.length > 0) {
		return [[glyphName substringWithRange:u5_6Range] uppercaseString];
	}

	return nil;
}

- (NSString *)selectPhoneticFromData:(NSDictionary *)phoneticData {
	NSString *result = nil;
	switch (_displayMode) {
		case PhoneticDisplayModeZhuyin:
			result = phoneticData[@"zhuyin"];
			break;
		case PhoneticDisplayModePinyin:
			result = phoneticData[@"pinyin"];
			break;
		case PhoneticDisplayModeWadeGiles:
			result = phoneticData[@"wade_giles"];
			break;
		case PhoneticDisplayModeMandarin:
			result = phoneticData[@"mandarin"];
			break;
		case PhoneticDisplayModeCantonese:
			result = phoneticData[@"cantonese"];
			break;
		case PhoneticDisplayModeJapanese: {
			NSString *on = phoneticData[@"japanese_on"];   // 大寫（原始格式）
			NSString *kun = phoneticData[@"japanese_kun"]; // 轉小寫
			if (on && kun) {
				result = [NSString stringWithFormat:@"%@ %@", on, [kun lowercaseString]];
			} else if (on) {
				result = on;
			} else if (kun) {
				result = [kun lowercaseString];
			}
			break;
		}
		case PhoneticDisplayModeKorean:
			result = phoneticData[@"korean"];
			break;
		case PhoneticDisplayModeVietnamese:
			result = phoneticData[@"vietnamese"];
			break;
		default:
			result = phoneticData[@"zhuyin"];
			break;
	}
	return result;
}

#pragma mark - GlyphsReporter Protocol

- (NSUInteger)interfaceVersion {
	return 1;
}

- (NSString *)title {
	return LocalizedString(@"plugin.title", @"Plugin title shown in menu");
}

- (NSString *)keyEquivalent {
	return nil;
}

- (NSEventModifierFlags)modifierMask {
	return 0;
}

#pragma mark - Drawing

- (void)drawForegroundForLayer:(GSLayer *)layer options:(NSDictionary *)options {
	DLog("drawForegroundForLayer called");

	CGFloat scale = [self getScale];
	if (scale <= 0.1999) {
		DLog("Scale %.2f is too small, hiding phonetics display", scale);
		return;
	}

	GSGlyph *glyph = layer.parent;
	if (!glyph) {
		DLog("No parent glyph");
		return;
	}

	DLog("Drawing for glyph: %@", glyph.name);

	NSString *phoneticText = [self phoneticStringForGlyph:glyph];
	if (!phoneticText || phoneticText.length == 0) {
		DLog("No phonetic text to display");
		return;
	}

	GSFontMaster *master = [layer associatedFontMaster];
	CGFloat ascender = master ? [master ascenderForLayer:layer] : 800.0;

	NSRect bounds = [layer bounds];
	CGFloat x = layer.width;
	CGFloat y = MAX(ascender, NSMaxY(bounds) + 50.0);
	NSPoint position = NSMakePoint(x, y);

	CGFloat baseFontSize = 24.0;
	NSColor *color = [NSColor colorWithRed:0.5 green:0.8 blue:0.9 alpha:1.0];

	[self drawText:phoneticText
		   atPoint:position
		  fontSize:baseFontSize
		 fontColor:color
		 alignment:NSTextAlignmentRight];

	DLog("Drawing complete for glyph: %@", glyph.name);
}

- (void)drawBackgroundForLayer:(GSLayer*)layer options:(NSDictionary *)options {
}

- (void)drawBackgroundForInactiveLayer:(GSLayer*)layer options:(NSDictionary *)options {
}

#pragma mark - Context Menu (GlyphsReporterProtocol)

- (void)addMenuItemsForEvent:(NSEvent *)theEvent toMenu:(NSMenu *)theMenu {
	NSMenuItem *mainMenuItem = [[NSMenuItem alloc] initWithTitle:LocalizedString(@"menu.displayMode.title", @"Main menu item title")
														  action:nil
												   keyEquivalent:@""];

	NSMenu *submenu = [[NSMenu alloc] initWithTitle:@""];

	// ── CNS11643 Section ──
	[submenu addItem:[NSMenuItem sectionHeaderWithTitle:LocalizedString(@"section.cns", @"CNS11643 section header")]];

	[self addMenuItemToMenu:submenu
					  title:LocalizedString(@"mode.zhuyin", @"Zhuyin")
					 action:@selector(setDisplayModeZhuyin:)
					   mode:PhoneticDisplayModeZhuyin];

	[self addMenuItemToMenu:submenu
					  title:LocalizedString(@"mode.pinyin", @"Pinyin")
					 action:@selector(setDisplayModePinyin:)
					   mode:PhoneticDisplayModePinyin];

	[self addMenuItemToMenu:submenu
					  title:LocalizedString(@"mode.wadeGiles", @"Wade-Giles")
					 action:@selector(setDisplayModeWadeGiles:)
					   mode:PhoneticDisplayModeWadeGiles];

	// ── Unicode Unihan Section ──
	[submenu addItem:[NSMenuItem sectionHeaderWithTitle:LocalizedString(@"section.unihan", @"Unicode Unihan section header")]];

	[self addMenuItemToMenu:submenu
					  title:LocalizedString(@"mode.mandarin", @"Mandarin")
					 action:@selector(setDisplayModeMandarin:)
					   mode:PhoneticDisplayModeMandarin];

	[self addMenuItemToMenu:submenu
					  title:LocalizedString(@"mode.cantonese", @"Cantonese")
					 action:@selector(setDisplayModeCantonese:)
					   mode:PhoneticDisplayModeCantonese];

	[self addMenuItemToMenu:submenu
					  title:LocalizedString(@"mode.japanese", @"Japanese")
					 action:@selector(setDisplayModeJapanese:)
					   mode:PhoneticDisplayModeJapanese];

	[self addMenuItemToMenu:submenu
					  title:LocalizedString(@"mode.korean", @"Korean")
					 action:@selector(setDisplayModeKorean:)
					   mode:PhoneticDisplayModeKorean];

	[self addMenuItemToMenu:submenu
					  title:LocalizedString(@"mode.vietnamese", @"Vietnamese")
					 action:@selector(setDisplayModeVietnamese:)
					   mode:PhoneticDisplayModeVietnamese];

	mainMenuItem.submenu = submenu;
	[theMenu addItem:mainMenuItem];
}

- (void)addMenuItemToMenu:(NSMenu *)menu
					title:(NSString *)title
				   action:(SEL)action
					 mode:(PhoneticDisplayMode)mode {
	NSMenuItem *item = [[NSMenuItem alloc] initWithTitle:title
												 action:action
										  keyEquivalent:@""];
	item.target = self;
	item.state = (_displayMode == mode) ? NSControlStateValueOn : NSControlStateValueOff;
	[menu addItem:item];
}

#pragma mark - Display Mode Management

- (void)setDisplayModeZhuyin:(id)sender {
	[self setDisplayMode:PhoneticDisplayModeZhuyin];
}

- (void)setDisplayModePinyin:(id)sender {
	[self setDisplayMode:PhoneticDisplayModePinyin];
}

- (void)setDisplayModeWadeGiles:(id)sender {
	[self setDisplayMode:PhoneticDisplayModeWadeGiles];
}

- (void)setDisplayModeMandarin:(id)sender {
	[self setDisplayMode:PhoneticDisplayModeMandarin];
}

- (void)setDisplayModeCantonese:(id)sender {
	[self setDisplayMode:PhoneticDisplayModeCantonese];
}

- (void)setDisplayModeJapanese:(id)sender {
	[self setDisplayMode:PhoneticDisplayModeJapanese];
}

- (void)setDisplayModeKorean:(id)sender {
	[self setDisplayMode:PhoneticDisplayModeKorean];
}

- (void)setDisplayModeVietnamese:(id)sender {
	[self setDisplayMode:PhoneticDisplayModeVietnamese];
}

- (PhoneticDisplayMode)defaultDisplayModeForSystemLanguage {
	NSString *language = [NSLocale preferredLanguages].firstObject;
	if ([language hasPrefix:@"zh-Hant"]) {
		return PhoneticDisplayModeZhuyin;
	} else if ([language hasPrefix:@"zh-Hans"]) {
		return PhoneticDisplayModeMandarin;
	} else if ([language hasPrefix:@"ja"]) {
		return PhoneticDisplayModeJapanese;
	} else if ([language hasPrefix:@"ko"]) {
		return PhoneticDisplayModeKorean;
	}
	return PhoneticDisplayModeMandarin;
}

- (void)setDisplayMode:(PhoneticDisplayMode)mode {
	_displayMode = mode;
	[[NSUserDefaults standardUserDefaults] setInteger:mode forKey:kPhoneticDisplayModeKey];
	[[NSUserDefaults standardUserDefaults] synchronize];
	[_editViewController.graphicView setNeedsDisplay:YES];
}

#pragma mark - Helpers

- (void)drawText:(NSString *)text
		 atPoint:(NSPoint)position
		fontSize:(CGFloat)baseFontSize
	   fontColor:(NSColor *)color
	   alignment:(NSTextAlignment)alignment {

	if (!text || text.length == 0) {
		return;
	}

	CGFloat currentZoom = [self getScale];
	CGFloat actualFontSize = baseFontSize / currentZoom;
	NSFont *font = [NSFont systemFontOfSize:actualFontSize];

	NSMutableParagraphStyle *paragraphStyle = [[NSMutableParagraphStyle alloc] init];
	[paragraphStyle setAlignment:alignment];

	NSDictionary *attributes = @{
		NSFontAttributeName: font,
		NSForegroundColorAttributeName: color,
		NSParagraphStyleAttributeName: paragraphStyle
	};

	NSAttributedString *attributedText = [[NSAttributedString alloc] initWithString:text
																		 attributes:attributes];

	NSSize textSize = [attributedText size];
	NSPoint drawPosition = position;

	if (alignment == NSTextAlignmentRight) {
		drawPosition.x -= textSize.width;
	} else if (alignment == NSTextAlignmentCenter) {
		drawPosition.x -= textSize.width / 2.0;
	}

	[attributedText drawAtPoint:drawPosition];

	DLog("Drew text '%@' at (%.2f, %.2f) with zoom: %.2f, fontSize: %.2f",
		 text, drawPosition.x, drawPosition.y, currentZoom, actualFontSize);
}

- (float)getScale {
	if (_editViewController) {
		return _editViewController.graphicView.scale;
	} else {
		return 1.0;
	}
}

- (void)setController:(NSViewController <GSGlyphEditViewControllerProtocol>*)controller {
	_editViewController = controller;
}

@end

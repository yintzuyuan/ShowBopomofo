//
//  PhoneticDatabase.m
//  ShowChinesePhonetics
//
//  Created by 殷慈遠 on 2025/11/14.
//

#import "PhoneticDatabase.h"
#import <sqlite3.h>

// Debug logging macro
#ifdef DEBUG
	#define DLog(fmt, ...) NSLog((@"[PhoneticDatabase] %s " fmt), __PRETTY_FUNCTION__, ##__VA_ARGS__)
#else
	#define DLog(fmt, ...) // 正式版本不輸出
#endif

// 查詢欄位名稱（對應 readings 表）
static NSString * const kColumnNames[] = {
	@"zhuyin", @"pinyin", @"wade_giles",
	@"mandarin", @"cantonese", @"japanese_on",
	@"japanese_kun", @"korean", @"vietnamese"
};
static const int kColumnCount = 9;

@implementation PhoneticDatabase {
	sqlite3 *_database;
	NSCache *_cache;
}

#pragma mark - Initialization

- (instancetype)initWithDatabaseName:(NSString *)databaseName {
	self = [super init];
	if (self) {
		_database = NULL;

		// 初始化快取
		_cache = [[NSCache alloc] init];
		_cache.countLimit = 1000;
		_cache.totalCostLimit = 2 * 1024 * 1024; // 2MB（每筆資料量增加）
		_cache.evictsObjectsWithDiscardedContent = YES;
		_cache.name = @"PhoneticDatabaseCache";

		[self loadDatabaseWithName:databaseName];
	}
	return self;
}

- (void)dealloc {
	[self closeDatabase];
}

#pragma mark - Public Methods

- (BOOL)isConnected {
	return _database != NULL;
}

- (NSDictionary<NSString *, NSString *> *)phoneticDataForUnicode:(NSString *)unicodeHex {
	if (!self.isConnected || !unicodeHex) {
		DLog("No database connection or invalid unicode: db=%p, unicode=%@", _database, unicodeHex);
		return nil;
	}

	NSDictionary *cached = [_cache objectForKey:unicodeHex];
	if (cached) {
		DLog("Cache hit for %@", unicodeHex);
		return cached;
	}

	NSDictionary *result = [self queryDatabaseForUnicode:unicodeHex];

	// 備援查詢：康熙部首 / CJK 部首補充 → equiv_unified → readings
	if (!result) {
		NSString *unifiedUnicode = [self queryEquivUnifiedForUnicode:unicodeHex];
		if (unifiedUnicode) {
			DLog("EUI fallback: %@ -> %@", unicodeHex, unifiedUnicode);
			result = [self queryDatabaseForUnicode:unifiedUnicode];
		}
	}

	if (result) {
		[_cache setObject:result forKey:unicodeHex];
	}

	return result;
}

- (void)closeDatabase {
	if (_database) {
		sqlite3_close(_database);
		_database = NULL;
		DLog("Database closed");
	}
}

#pragma mark - Private Methods

- (void)loadDatabaseWithName:(NSString *)databaseName {
	NSBundle *bundle = [NSBundle bundleForClass:[self class]];
	NSString *dbPath = [bundle pathForResource:databaseName ofType:@"db"];

	if (!dbPath) {
		DLog("Error: Database file '%@.db' not found in bundle!", databaseName);
		DLog("Bundle path: %@", bundle.bundlePath);
		return;
	}

	int result = sqlite3_open_v2([dbPath UTF8String], &_database, SQLITE_OPEN_READONLY, NULL);
	if (result != SQLITE_OK) {
		DLog("Error opening database: %s", sqlite3_errmsg(_database));
		_database = NULL;
	} else {
		DLog("Database loaded successfully from: %@", dbPath);

		// 唯讀場景 PRAGMA 優化
		sqlite3_exec(_database, "PRAGMA journal_mode=OFF", NULL, NULL, NULL);
		sqlite3_exec(_database, "PRAGMA synchronous=OFF", NULL, NULL, NULL);
		sqlite3_exec(_database, "PRAGMA locking_mode=EXCLUSIVE", NULL, NULL, NULL);

		[self validateDatabaseSchema];
	}
}

- (void)validateDatabaseSchema {
	sqlite3_stmt *statement;
	NSString *query = @"SELECT name FROM sqlite_master WHERE type='table' AND name IN ('readings', 'equiv_unified')";

	if (sqlite3_prepare_v2(_database, [query UTF8String], -1, &statement, NULL) == SQLITE_OK) {
		NSMutableSet *found = [NSMutableSet set];
		while (sqlite3_step(statement) == SQLITE_ROW) {
			const char *name = (const char *)sqlite3_column_text(statement, 0);
			if (name) {
				[found addObject:[NSString stringWithUTF8String:name]];
			}
		}
		sqlite3_finalize(statement);

		for (NSString *table in @[@"readings", @"equiv_unified"]) {
			if ([found containsObject:table]) {
				DLog("Table '%@' found ✓", table);
			} else {
				DLog("Warning: Table '%@' not found!", table);
			}
		}
	}
}

- (nullable NSString *)queryEquivUnifiedForUnicode:(NSString *)unicodeHex {
	sqlite3_stmt *statement;
	NSString *query = @"SELECT unified_unicode FROM equiv_unified WHERE unicode = ?";
	NSString *result = nil;

	if (sqlite3_prepare_v2(_database, [query UTF8String], -1, &statement, NULL) == SQLITE_OK) {
		sqlite3_bind_text(statement, 1, [unicodeHex UTF8String], -1, SQLITE_TRANSIENT);
		if (sqlite3_step(statement) == SQLITE_ROW) {
			const char *value = (const char *)sqlite3_column_text(statement, 0);
			if (value) {
				result = [NSString stringWithUTF8String:value];
			}
		}
		sqlite3_finalize(statement);
	}

	return result;
}

- (nullable NSDictionary<NSString *, NSString *> *)queryDatabaseForUnicode:(NSString *)unicodeHex {
	sqlite3_stmt *statement;
	NSString *query = @"SELECT zhuyin, pinyin, wade_giles, mandarin, "
		"cantonese, japanese_on, japanese_kun, korean, vietnamese "
		"FROM readings WHERE unicode = ?";

	NSDictionary *result = nil;

	if (sqlite3_prepare_v2(_database, [query UTF8String], -1, &statement, NULL) == SQLITE_OK) {
		sqlite3_bind_text(statement, 1, [unicodeHex UTF8String], -1, SQLITE_TRANSIENT);

		if (sqlite3_step(statement) == SQLITE_ROW) {
			NSMutableDictionary *data = [NSMutableDictionary dictionaryWithCapacity:kColumnCount];

			for (int i = 0; i < kColumnCount; i++) {
				const char *value = (const char *)sqlite3_column_text(statement, i);
				if (value) {
					data[kColumnNames[i]] = [NSString stringWithUTF8String:value];
				}
				// NULL 欄位不加入字典，讓 phoneticData[@"key"] 回傳 nil
			}

			result = [data copy];
			DLog("Found data for %@: %lu fields", unicodeHex, (unsigned long)data.count);
		} else {
			DLog("No data found for unicode: %@", unicodeHex);
		}

		sqlite3_finalize(statement);
	} else {
		DLog("Error preparing statement: %s", sqlite3_errmsg(_database));
	}

	return result;
}

@end

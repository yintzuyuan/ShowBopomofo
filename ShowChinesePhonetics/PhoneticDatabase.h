//
//  PhoneticDatabase.h
//  ShowChinesePhonetics
//
//  Created by 殷慈遠 on 2025/11/14.
//

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

/**
 * 漢字發音資料庫管理類別
 * 負責從 SQLite 資料庫中查詢多語言發音資料
 */
@interface PhoneticDatabase : NSObject

/**
 * 資料庫是否已成功連線
 */
@property (nonatomic, readonly) BOOL isConnected;

/**
 * 初始化資料庫
 * @param databaseName 資料庫檔案名稱（不含副檔名）
 * @return 資料庫實例
 */
- (instancetype)initWithDatabaseName:(NSString *)databaseName;

/**
 * 根據 Unicode 十六進位字串查詢發音資料
 * @param unicodeHex Unicode 十六進位字串（例如："4E00" 代表 "一"）
 * @return 包含 zhuyin, pinyin, wade_giles, mandarin, cantonese,
 *         japanese_on, japanese_kun, korean, vietnamese 的字典，
 *         查無資料時回傳 nil
 */
- (nullable NSDictionary<NSString *, NSString *> *)phoneticDataForUnicode:(NSString *)unicodeHex;

/**
 * 關閉資料庫連線
 */
- (void)closeDatabase;

@end

NS_ASSUME_NONNULL_END

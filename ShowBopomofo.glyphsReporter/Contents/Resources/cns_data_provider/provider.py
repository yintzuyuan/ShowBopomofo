# -*- coding: utf-8 -*-
"""
CNS 11643 字碼資料提供者類別 / CNS 11643 Character Data Provider Class
用於存取 CNS 11643 字碼資料庫 / For accessing CNS 11643 character database
"""

import sqlite3
import os

class CNSDataProvider:
    """
    CNS 11643 字碼資料提供者類別 / CNS 11643 Character Data Provider Class
    提供對 CNS 11643 字碼資料庫的存取介面 / Provides interface for accessing CNS 11643 character database
    """
    
    def __init__(self):
        # 決定相對於此腳本的 SQLite 資料庫路徑 / Determine the path to the SQLite database relative to this script
        script_dir = os.path.dirname(__file__)
        self.db_path = os.path.join(script_dir, 'cns_data.sqlite3')
        self.conn = None
        self.column_names = None  # 動態儲存欄位名稱 / To store column names dynamically

    def connect(self):
        """
        建立與 SQLite 資料庫的連線 / Establishes a connection to the SQLite database.
        
        Returns:
            bool: 連線成功為 True，失敗為 False / True if connection successful, False otherwise
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # 允許透過欄位名稱存取欄位 / This allows accessing columns by name
            
            # 動態取得欄位名稱 / Dynamically get column names
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(characters)")
            self.column_names = [row[1] for row in cursor.fetchall()]

            return True
        except sqlite3.Error as e:
            print(f"資料庫連線錯誤 / Error connecting to database: {e}")
            self.conn = None
            self.column_names = None
            return False

    def disconnect(self):
        """
        關閉資料庫連線 / Closes the database connection.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            self.column_names = None

    def get_data_by_cns_id(self, cns_id):
        """
        透過 CNS 編號取得所有資料 / Retrieves all data for a given CNS ID.
        
        Args:
            cns_id (str): CNS 編號（例如：'1-4421'）/ CNS ID (e.g., '1-4421')
            
        Returns:
            dict or None: 字元資料字典，未找到時回傳 None / Dictionary of character data or None if not found
        """
        if not self.conn:
            if not self.connect():
                return None
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE cns_id = ?", (cns_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_data_by_character(self, character):
        """
        透過字元取得所有資料 / Retrieves all data for a given character.
        
        Args:
            character (str): 要查詢的字元 / Character to query
            
        Returns:
            list: 字元資料字典列表（因為多個 CNS 編號可能對應同一字元）
                  / List of dictionaries (as multiple CNS IDs might map to the same character)
                  沒有找到時回傳空列表 / Returns empty list if not found
        """
        if not self.conn:
            if not self.connect():
                return []
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE character = ?", (character,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def find_characters(self, **kwargs):
        """
        根據多項條件尋找字元 / Finds characters based on multiple criteria.
        
        Args:
            **kwargs: 搜尋條件（欄位名稱=值）/ Search criteria (column_name=value)
        
        Example:
            find_characters(radical='木', stroke_count=8)  # 部首為「木」且筆劃數為 8 的字元
        
        Returns:
            list: 字元資料字典列表，沒有找到時回傳空列表
                  / List of dictionaries or empty list if not found
        """
        if not self.conn:
            if not self.connect():
                return []
        
        query = "SELECT * FROM characters WHERE 1=1"
        params = []
        
        for key, value in kwargs.items():
            if self.column_names and key in self.column_names:  # 確保鍵值是有效的欄位 / Ensure key is a valid column
                query += f" AND {key} = ?"
                params.append(value)
            else:
                print(f"警告：無效的搜尋條件 '{key}'，跳過此條件 / Warning: Invalid search criterion '{key}'. Skipping.")

        cursor = self.conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# 使用範例（用於測試目的，不直接用於 Glyphs 外掛）/ Example Usage (for testing purposes, not for Glyphs plugin directly)
if __name__ == '__main__':
    # 此部分假設 cns_data.sqlite3 位於與此腳本相同的目錄中
    # This part assumes cns_data.sqlite3 is in the same directory as this script
    # 實際的 Glyphs 外掛中，db_path 將由外掛載入器處理
    # For actual Glyphs plugin, the db_path will be handled by the plugin loader
    provider = CNSDataProvider()
    if provider.connect():
        print("資料庫連線成功 / Database connected successfully.")
        
        # 測試 1：透過 CNS 編號取得資料 / Test 1: Get data by CNS ID
        cns_id_data = provider.get_data_by_cns_id('1-4421')
        if cns_id_data:
            print(f"1-4421 的資料 / Data for 1-4421: {cns_id_data['character']}, Unicode: {cns_id_data['unicode']}, 部首 / Radical: {cns_id_data['radical']}, 筆劃 / Stroke: {cns_id_data['stroke_count']}")
        else:
            print("找不到 1-4421 / 1-4421 not found.")

        # 測試 2：透過字元取得資料 / Test 2: Get data by character
        char_data = provider.get_data_by_character('龍')
        if char_data:
            print(f"「龍」的資料 / Data for '龍': {char_data[0]['cns_id']}, Unicode: {char_data[0]['unicode']}")
        else:
            print("找不到「龍」/ '龍' not found.")

        # 測試 3：根據條件尋找字元 / Test 3: Find characters by criteria
        found_chars = provider.find_characters(radical='1', stroke_count=1)
        print(f"找到 {len(found_chars)} 個部首為 '1' 且筆劃數為 1 的字元 / Found {len(found_chars)} characters with radical '1' and 1 stroke.")
        if found_chars:
            for i, char_info in enumerate(found_chars[:5]):  # 顯示前 5 個 / Print first 5
                print(f"  {i+1}. {char_info['character']} (CNS: {char_info['cns_id']})")

        provider.disconnect()
        print("資料庫連線已關閉 / Database disconnected.")
    else:
        print("資料庫連線失敗 / Failed to connect to database.")
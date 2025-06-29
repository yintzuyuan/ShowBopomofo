# -*- coding: utf-8 -*-
"""
CNS 11643 字碼資料提供者模組 / CNS 11643 Character Data Provider Module

此模組提供存取 CNS 11643 字碼資料庫的 Python 介面
This module provides Python interface for accessing CNS 11643 character database

主要功能 / Main Features:
- 透過 CNS 編號查詢字元資料 / Query character data by CNS ID
- 透過字元查詢相關資料 / Query data by character
- 根據條件搜尋字元 / Search characters by criteria
- 支援多項字元屬性查詢 / Support multiple character property queries

使用範例 / Usage Example:
    from cns_data_provider import CNSDataProvider
    
    provider = CNSDataProvider()
    if provider.connect():
        data = provider.get_data_by_cns_id('1-4421')
        provider.disconnect()
"""

from .provider import CNSDataProvider

__version__ = "1.0.0"
__author__ = "CNS 11643 OpenData Project"

__all__ = ['CNSDataProvider']

"""数据模块"""
from .openalex_fetcher import OpenAlexFetcher, DataCache, get_fetcher

# 导出类和单例获取函数
__all__ = ["OpenAlexFetcher", "DataCache", "get_fetcher"]

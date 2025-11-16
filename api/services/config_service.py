"""
配置服务层 - 处理配置相关的业务逻辑
"""
import logging
from typing import Dict, List, Any, Optional
from api.utils import get_all_universities, get_all_disciplines
from data import get_fetcher

logger = logging.getLogger(__name__)


class ConfigService:
    """配置服务 - 提供系统配置信息"""
    
    def __init__(self):
        """初始化配置服务"""
        # 使用模块单例，避免重复初始化 OpenAlexFetcher
        self.fetcher = get_fetcher()
    
    @staticmethod
    def get_universities() -> Dict[str, Any]:
        """
        获取所有支持的大学列表
        
        Returns:
            大学列表
        """
        logger.info("获取大学列表")
        universities = get_all_universities()
        return {
            "status": "success",
            "data": universities
        }
    
    @staticmethod
    def get_disciplines() -> Dict[str, Any]:
        """
        获取所有支持的学科列表
        
        Returns:
            学科列表
        """
        logger.info("获取学科列表")
        disciplines = get_all_disciplines()
        return {
            "status": "success",
            "data": disciplines
        }
    
    def search_university(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """
        搜索大学在 OpenAlex 上的 ID 和信息
        
        Args:
            query: 大学名称或关键词
            limit: 返回结果数量
        
        Returns:
            包含大学信息的字典
        """
        logger.info(f"搜索大学: {query}")
        
        try:
            if not query or not query.strip():
                return {
                    "status": "error",
                    "message": "搜索关键词不能为空"
                }
            
            results = self.fetcher.search_institutions(query, limit=limit)
            
            return {
                "status": "success",
                "query": query,
                "count": len(results),
                "data": results
            }
        except Exception as e:
            logger.error(f"搜索大学失败: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def search_discipline(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """
        搜索学科在 OpenAlex 上的 ID 和信息
        
        Args:
            query: 学科名称或关键词
            limit: 返回结果数量
        
        Returns:
            包含学科信息的字典
        """
        logger.info(f"搜索学科: {query}")
        
        try:
            if not query or not query.strip():
                return {
                    "status": "error",
                    "message": "搜索关键词不能为空"
                }
            
            results = self.fetcher.search_topics(query, limit=limit)
            
            return {
                "status": "success",
                "query": query,
                "count": len(results),
                "data": results
            }
        except Exception as e:
            logger.error(f"搜索学科失败: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

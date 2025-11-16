"""
论文服务层 - 处理论文相关的业务逻辑
使用 Repository 层获取数据，专注于业务逻辑
"""
import logging
from typing import Optional, Dict, Any
from data import DataCache
from config import Config
from api.repositories import PaperRepository
from api.exceptions import (
    DataNotFoundException,
    DataFetchException
)

logger = logging.getLogger(__name__)


class PaperService:
    """论文服务 - 处理论文相关操作"""
    
    def __init__(self, use_redis: bool = False):
        """初始化论文服务"""
        self.repository = PaperRepository()
        self.cache = DataCache(use_redis=use_redis)
    
    def get_paper_details(self, paper_id: str) -> Dict[str, Any]:
        """
        获取论文详情
        
        Args:
            paper_id: 论文ID (OpenAlex ID 或 DOI)
        
        Returns:
            论文数据字典
        """
        cache_key = f"paper:{paper_id}"
        
        # 尝试从缓存获取
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"缓存命中: {cache_key}")
            return {
                "status": "success",
                "data": cached_data,
                "cached": True
            }
        
        logger.info(f"获取论文详情: {paper_id}")
        
        # 从 Repository 获取
        paper_data = self.repository.get_by_id(paper_id)
        if not paper_data:
            raise DataNotFoundException(f"论文 {paper_id} 不存在")
        
        # 缓存结果
        self.cache.set(cache_key, paper_data)
        
        return {
            "status": "success",
            "data": paper_data,
            "cached": False
        }
    
    def get_papers_by_year_range(
        self,
        year_min: int,
        year_max: int,
        limit: int = Config.DEFAULT_LIMIT,
        discipline: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取指定年份范围内的论文
        
        Args:
            year_min: 起始年份
            year_max: 结束年份
            limit: 返回数量限制
            discipline: 学科ID (可选)
        
        Returns:
            论文列表字典
        """
        cache_key = f"papers:{year_min}:{year_max}:{limit}:{discipline or 'all'}"
        
        # 尝试从缓存获取
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"缓存命中: {cache_key}")
            return {
                "status": "success",
                "data": cached_data,
                "cached": True
            }
        
        logger.info(f"获取论文: {year_min}-{year_max}, limit={limit}")
        
        # 从 Repository 获取
        papers = self.repository.get_by_year_range(year_min, year_max, limit)
        if not papers:
            raise DataFetchException("未获取到论文数据")
        
        # 缓存结果
        self.cache.set(cache_key, papers)
        
        return {
            "status": "success",
            "data": papers,
            "cached": False
        }
    
    def get_paper_citations(
        self,
        paper_id: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        获取论文的引用论文
        
        Args:
            paper_id: 论文ID
            limit: 返回数量限制
        
        Returns:
            引用论文列表
        """
        cache_key = f"paper_citations:{paper_id}:{limit}"
        
        # 尝试从缓存获取
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"缓存命中: {cache_key}")
            return {
                "status": "success",
                "data": cached_data,
                "cached": True
            }
        
        logger.info(f"获取论文 {paper_id} 的引用论文")
        
        # 从 Repository 获取
        citations = self.repository.get_citations(paper_id, limit)
        
        # 缓存结果
        self.cache.set(cache_key, citations)
        
        return {
            "status": "success",
            "data": citations,
            "cached": False
        }

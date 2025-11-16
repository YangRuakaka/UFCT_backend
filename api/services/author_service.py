"""
作者服务层 - 处理作者相关的业务逻辑
使用 Repository 层获取数据，专注于业务逻辑
"""
import logging
from typing import Optional, Dict, Any
from data import DataCache
from config import Config
from api.repositories import AuthorRepository
from api.exceptions import (
    DataNotFoundException,
    DataFetchException
)

logger = logging.getLogger(__name__)


class AuthorService:
    """作者服务 - 处理作者相关操作"""
    
    def __init__(self, use_redis: bool = False):
        """初始化作者服务"""
        self.repository = AuthorRepository()
        self.cache = DataCache(use_redis=use_redis)
    
    def get_author_details(self, author_id: str) -> Dict[str, Any]:
        """
        获取作者详情
        
        Args:
            author_id: 作者ID
        
        Returns:
            作者数据字典
        """
        cache_key = f"author:{author_id}"
        
        # 尝试从缓存获取
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"缓存命中: {cache_key}")
            return {
                "status": "success",
                "data": cached_data,
                "cached": True
            }
        
        logger.info(f"获取作者详情: {author_id}")
        
        # 从 Repository 获取
        author_data = self.repository.get_by_id(author_id)
        if not author_data:
            raise DataNotFoundException(f"作者 {author_id} 不存在")
        
        # 缓存结果
        self.cache.set(cache_key, author_data)
        
        return {
            "status": "success",
            "data": author_data,
            "cached": False
        }
    
    def get_authors_by_work_ids(
        self,
        work_ids: list,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        通过论文ID获取作者
        
        Args:
            work_ids: 论文ID列表
            limit: 返回数量限制
        
        Returns:
            作者列表字典
        """
        cache_key = f"authors_by_works:{len(work_ids)}:{limit}"
        
        # 尝试从缓存获取
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"缓存命中: {cache_key}")
            return {
                "status": "success",
                "data": cached_data,
                "cached": True
            }
        
        logger.info(f"通过 {len(work_ids)} 篇论文获取作者")
        
        # 从 Repository 获取
        authors = self.repository.get_by_work_ids(work_ids, limit)
        if not authors:
            raise DataFetchException("未获取到作者数据")
        
        # 缓存结果
        self.cache.set(cache_key, authors)
        
        return {
            "status": "success",
            "data": authors,
            "cached": False
        }
    
    def get_author_collaborators(
        self,
        author_id: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        获取作者的协作者
        
        Args:
            author_id: 作者ID
            limit: 返回数量限制
        
        Returns:
            协作者列表
        """
        cache_key = f"author_collaborators:{author_id}:{limit}"
        
        # 尝试从缓存获取
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"缓存命中: {cache_key}")
            return {
                "status": "success",
                "data": cached_data,
                "cached": True
            }
        
        logger.info(f"获取作者 {author_id} 的协作者")
        
        # 从 Repository 获取
        collaborators = self.repository.get_collaborators(author_id, limit)
        
        # 缓存结果
        self.cache.set(cache_key, collaborators)
        
        return {
            "status": "success",
            "data": collaborators,
            "cached": False
        }
    
    def get_author_publications(
        self,
        author_id: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        获取作者的论文
        
        Args:
            author_id: 作者ID
            limit: 返回数量限制
        
        Returns:
            论文列表
        """
        cache_key = f"author_publications:{author_id}:{limit}"
        
        # 尝试从缓存获取
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"缓存命中: {cache_key}")
            return {
                "status": "success",
                "data": cached_data,
                "cached": True
            }
        
        logger.info(f"获取作者 {author_id} 的论文")
        
        # 从 Repository 获取
        publications = self.repository.get_publications(author_id, limit)
        
        # 缓存结果
        self.cache.set(cache_key, publications)
        
        return {
            "status": "success",
            "data": publications,
            "cached": False
        }

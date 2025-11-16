"""
作者数据访问层 - 处理所有作者相关的数据库查询
"""
import logging
from typing import List, Dict, Optional
from data import get_fetcher

logger = logging.getLogger(__name__)


class AuthorRepository:
    """作者数据访问层"""
    
    def __init__(self):
        """初始化仓库"""
        # 使用模块单例，避免重复初始化 OpenAlexFetcher
        self.fetcher = get_fetcher()
    
    def get_by_id(self, author_id: str) -> Optional[Dict]:
        """
        按ID获取作者
        
        Args:
            author_id: 作者ID
        
        Returns:
            作者数据或None
        """
        logger.info(f"获取作者: {author_id}")
        author = self.fetcher.get_author_by_id(author_id)
        return author
    
    def get_by_work_ids(
        self,
        work_ids: List[str],
        limit: int = 100
    ) -> List[Dict]:
        """
        通过论文ID列表获取作者
        
        Args:
            work_ids: 论文ID列表
            limit: 返回数量限制
        
        Returns:
            作者列表
        """
        logger.info(f"通过 {len(work_ids)} 篇论文获取作者, limit={limit}")
        authors = self.fetcher.get_authors_by_work_ids(work_ids)
        return authors[:limit]
    
    def get_collaborators(
        self,
        author_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        获取作者的协作者
        
        Args:
            author_id: 作者ID
            limit: 返回数量限制
        
        Returns:
            协作者列表
        """
        logger.info(f"获取作者 {author_id} 的协作者, limit={limit}")
        # 这里需要根据实际API调整
        collaborators = self.fetcher.get_collaborators_by_author(author_id, limit)
        return collaborators
    
    def get_publications(
        self,
        author_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        获取作者的论文
        
        Args:
            author_id: 作者ID
            limit: 返回数量限制
        
        Returns:
            论文列表
        """
        logger.info(f"获取作者 {author_id} 的论文, limit={limit}")
        papers = self.fetcher.get_papers_by_author_id(author_id, limit)
        return papers
    
    def search(self, keyword: str, limit: int = 100) -> List[Dict]:
        """
        搜索作者
        
        Args:
            keyword: 搜索关键词（作者名）
            limit: 返回数量限制
        
        Returns:
            作者列表
        """
        logger.info(f"搜索作者: {keyword}, limit={limit}")
        authors = self.fetcher.search_authors(keyword, limit)
        return authors
    
    def get_by_institution(
        self,
        institution_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        按机构获取作者
        
        Args:
            institution_id: 机构ID
            limit: 返回数量限制
        
        Returns:
            作者列表
        """
        logger.info(f"获取机构 {institution_id} 的作者, limit={limit}")
        authors = self.fetcher.get_authors_by_institution(institution_id, limit)
        return authors

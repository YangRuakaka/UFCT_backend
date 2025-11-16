"""
论文数据访问层 - 处理所有论文相关的数据库查询
"""
import logging
from typing import List, Dict, Optional
from data import get_fetcher

logger = logging.getLogger(__name__)


class PaperRepository:
    """论文数据访问层"""
    
    def __init__(self):
        """初始化仓库"""
        # 使用模块单例，避免重复初始化 OpenAlexFetcher
        self.fetcher = get_fetcher()
    
    def get_by_id(self, paper_id: str) -> Optional[Dict]:
        """
        按ID获取论文
        
        Args:
            paper_id: 论文ID (OpenAlex ID 或 DOI)
        
        Returns:
            论文数据或None
        """
        logger.info(f"获取论文: {paper_id}")
        paper = self.fetcher.get_work_by_id(paper_id)
        return paper
    
    def get_by_year_range(
        self,
        year_min: int,
        year_max: int,
        limit: int = 500
    ) -> List[Dict]:
        """
        按年份范围获取论文
        
        Args:
            year_min: 起始年份
            year_max: 结束年份
            limit: 返回数量限制
        
        Returns:
            论文列表
        """
        logger.info(f"获取论文: {year_min}-{year_max}, limit={limit}")
        papers = self.fetcher.get_papers_by_year_range(year_min, year_max, limit)
        return papers
    
    def get_by_author_id(
        self,
        author_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        按作者ID获取论文
        
        Args:
            author_id: 作者ID
            limit: 返回数量限制
        
        Returns:
            论文列表
        """
        logger.info(f"获取作者 {author_id} 的论文, limit={limit}")
        # 这里需要根据实际API调整
        papers = self.fetcher.get_papers_by_author_id(author_id, limit)
        return papers
    
    def get_citations(self, paper_id: str, limit: int = 100) -> List[Dict]:
        """
        获取论文的被引用论文
        
        Args:
            paper_id: 论文ID
            limit: 返回数量限制
        
        Returns:
            引用论文列表
        """
        logger.info(f"获取论文 {paper_id} 的被引用论文, limit={limit}")
        # 这里需要根据实际API调整
        citations = self.fetcher.get_cited_by_papers(paper_id, limit)
        return citations
    
    def get_references(self, paper_id: str, limit: int = 100) -> List[Dict]:
        """
        获取论文的参考文献
        
        Args:
            paper_id: 论文ID
            limit: 返回数量限制
        
        Returns:
            参考文献列表
        """
        logger.info(f"获取论文 {paper_id} 的参考文献, limit={limit}")
        # 这里需要根据实际API调整
        references = self.fetcher.get_referenced_papers(paper_id, limit)
        return references
    
    def search(self, keyword: str, limit: int = 100) -> List[Dict]:
        """
        搜索论文
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
        
        Returns:
            论文列表
        """
        logger.info(f"搜索论文: {keyword}, limit={limit}")
        papers = self.fetcher.search_papers(keyword, limit)
        return papers

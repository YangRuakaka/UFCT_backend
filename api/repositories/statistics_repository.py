"""
统计数据访问层 - 处理所有统计相关的数据库查询
"""
import logging
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from data import get_fetcher

logger = logging.getLogger(__name__)


class StatisticsRepository:
    """统计数据访问层"""
    
    def __init__(self):
        """初始化仓库"""
        self.fetcher = get_fetcher()
    
    def get_papers_by_university_and_discipline(
        self,
        university: str,
        discipline: Optional[str] = None,
        year_min: int = 2015,
        year_max: int = 2024,
        limit: int = 500000
    ) -> List[Dict]:
        """
        按大学和学科获取论文
        
        使用 search_works 方法通过 institution 和 discipline 参数过滤
        
        Args:
            university: 大学名称或ID
            discipline: 学科名称或ID (可选)
            year_min: 起始年份
            year_max: 结束年份
            limit: 返回数量限制
        
        Returns:
            论文列表
        """
        logger.info(
            f"获取大学 {university} 的论文: "
            f"discipline={discipline}, {year_min}-{year_max}, limit={limit}"
        )
        
        # 使用 fetcher 的 search_works 方法，通过 institution 和 discipline 参数过滤
        papers = self.fetcher.search_works(
            year_min=year_min,
            year_max=year_max,
            limit=limit,
            discipline=discipline,
            institution=university
        )
        
        return papers if papers else []
    
    def get_papers_by_year_range(
        self,
        year_min: int,
        year_max: int,
        limit: int = 500000
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
        
        papers = self.fetcher.search_works(
            year_min=year_min,
            year_max=year_max,
            limit=limit
        )
        
        return papers if papers else []

"""
统计服务层 - 处理统计相关的业务逻辑
包括时间序列统计、分布直方图计算等
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from statistics import mean, stdev
import numpy as np

from data import DataCache
from config import Config
from api.repositories import StatisticsRepository
from api.exceptions import DataNotFoundException, DataFetchException

logger = logging.getLogger(__name__)


class StatisticsService:
    """统计服务 - 处理统计相关操作"""
    
    def __init__(self, use_redis: bool = False):
        """初始化统计服务"""
        self.repository = StatisticsRepository()
        self.cache = DataCache(use_redis=use_redis)
    
    def get_papers_statistics(
        self,
        university: str,
        discipline: Optional[str] = None,
        year_min: int = 2015,
        year_max: int = 2024,
        bins: Optional[List[Tuple[int, int]]] = None
    ) -> Dict[str, Any]:
        """
        获取论文统计数据，包括时间序列和专利引用分布
        
        Args:
            university: 大学名称或ID
            discipline: 学科名称或ID (可选)
            year_min: 起始年份
            year_max: 结束年份
            bins: 自定义直方图分组 [(0,10), (10,20), ...]，
                  如果为None则使用默认分组
        
        Returns:
            包含时间序列、全局直方图、按年份直方图和统计元数据的字典
        """
        cache_key = (
            f"statistics:{university}:{discipline or 'all'}:"
            f"{year_min}:{year_max}"
        )
        
        # 尝试从缓存获取
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"缓存命中: {cache_key}")
            return {
                "status": "success",
                "data": cached_data,
                "cached": True
            }
        
        logger.info(
            f"获取统计数据: university={university}, "
            f"discipline={discipline}, {year_min}-{year_max}"
        )
        
        # 获取原始论文数据
        papers = self.repository.get_papers_by_university_and_discipline(
            university=university,
            discipline=discipline,
            year_min=year_min,
            year_max=year_max
        )
        
        if not papers:
            raise DataNotFoundException(
                f"未找到大学 {university} 的论文数据"
            )
        
        # 创建默认直方图分组
        if bins is None:
            bins = self._create_default_bins()
        
        # 计算统计数据
        statistics_data = self._compute_statistics(
            papers=papers,
            year_min=year_min,
            year_max=year_max,
            bins=bins
        )
        
        # 缓存结果
        self.cache.set(cache_key, statistics_data)
        
        return {
            "status": "success",
            "data": statistics_data,
            "cached": False
        }
    
    def _create_default_bins(self) -> List[Tuple[int, int]]:
        """
        创建默认的直方图分组
        
        Returns:
            分组列表 [(0,10), (10,20), ..., (100, inf)]
        """
        bins = []
        
        # 0-10, 10-20, ..., 90-100
        for i in range(0, 100, 10):
            bins.append((i, i + 10))
        
        # 100+
        bins.append((100, float('inf')))
        
        return bins
    
    def _compute_statistics(
        self,
        papers: List[Dict],
        year_min: int,
        year_max: int,
        bins: List[Tuple[int, int]]
    ) -> Dict[str, Any]:
        """
        计算统计数据
        
        Args:
            papers: 论文列表
            year_min: 起始年份
            year_max: 结束年份
            bins: 直方图分组
        
        Returns:
            包含时间序列、全局直方图、按年份直方图和统计元数据的字典
        """
        # 按年份分组论文
        papers_by_year = self._group_papers_by_year(papers)
        
        # 计算时间序列数据
        timeline = self._compute_timeline(papers_by_year, year_min, year_max)
        
        # 获取所有论文的专利引用数
        all_patent_counts = self._extract_patent_counts(papers)
        
        # 计算全局直方图
        global_histogram = self._compute_histogram(all_patent_counts, bins)
        
        # 计算按年份的直方图
        histogram_by_year = self._compute_histogram_by_year(
            papers_by_year,
            bins
        )
        
        # 计算统计元数据
        metadata = self._compute_metadata(
            papers=papers,
            patent_counts=all_patent_counts,
            year_min=year_min,
            year_max=year_max
        )
        
        return {
            "timeline": timeline,
            "global_histogram": global_histogram,
            "histogram_by_year": histogram_by_year,
            "metadata": metadata
        }
    
    def _group_papers_by_year(self, papers: List[Dict]) -> Dict[int, List[Dict]]:
        """
        按年份分组论文
        
        OpenAlex API 中论文的年份存储在 'publication_year' 字段中。
        
        Args:
            papers: 论文列表
        
        Returns:
            按年份分组的论文字典 {year: [papers...]}
        """
        papers_by_year = defaultdict(list)
        
        for paper in papers:
            # OpenAlex 使用 publication_year 字段存储年份
            year = paper.get('publication_year')
            
            # 如果没有 publication_year，尝试从 publication_date 提取
            if not year and paper.get('publication_date'):
                try:
                    # 格式: "2023-01-01"
                    year = int(paper['publication_date'].split('-')[0])
                except (ValueError, IndexError):
                    continue
            
            if year:
                year = int(year)
                papers_by_year[year].append(paper)
        
        return dict(papers_by_year)
    
    def _extract_patent_counts(self, papers: List[Dict]) -> List[int]:
        """
        从论文中提取专利引用数
        
        OpenAlex API 中论文的引用数存储在 'cited_by_count' 字段中。
        注意：OpenAlex 中没有直接的 'patent_count' 字段，
        'cited_by_count' 表示被引用次数。
        
        Args:
            papers: 论文列表
        
        Returns:
            专利引用数列表
        """
        patent_counts = []
        
        for paper in papers:
            # OpenAlex 中使用 cited_by_count 表示被引用次数
            # 这是最接近"专利引用"概念的字段
            patent_count = paper.get('cited_by_count', 0)
            patent_counts.append(int(patent_count))
        
        return patent_counts
    
    def _compute_timeline(
        self,
        papers_by_year: Dict[int, List[Dict]],
        year_min: int,
        year_max: int
    ) -> List[Dict[str, Any]]:
        """
        计算时间序列数据
        
        Args:
            papers_by_year: 按年份分组的论文
            year_min: 起始年份
            year_max: 结束年份
        
        Returns:
            时间序列数据列表
        """
        timeline = []
        previous_count = None
        
        for year in range(year_min, year_max + 1):
            paper_count = len(papers_by_year.get(year, []))
            
            # 计算增长率
            if previous_count is not None and previous_count > 0:
                growth_rate = (paper_count - previous_count) / previous_count
            else:
                growth_rate = None
            
            timeline.append({
                "year": year,
                "paperCount": paper_count,
                "growth_rate": growth_rate
            })
            
            previous_count = paper_count
        
        return timeline
    
    def _compute_histogram(
        self,
        values: List[int],
        bins: List[Tuple[int, int]]
    ) -> List[Dict[str, Any]]:
        """
        计算直方图
        
        Args:
            values: 数值列表
            bins: 分组列表 [(start, end), ...]
        
        Returns:
            直方图数据列表
        """
        histogram = []
        total_count = len(values)
        
        for bin_start, bin_end in bins:
            # 计算该分组内的数据数量
            if bin_end == float('inf'):
                # 最后一组：>= bin_start
                count = sum(1 for v in values if v >= bin_start)
                bin_range = f"{int(bin_start)}+"
            else:
                # 中间分组：bin_start <= v < bin_end
                count = sum(1 for v in values if bin_start <= v < bin_end)
                bin_range = f"{int(bin_start)}-{int(bin_end)}"
            
            percentage = (count / total_count * 100) if total_count > 0 else 0
            
            histogram.append({
                "bin_range": bin_range,
                "bin_start": int(bin_start),
                "bin_end": int(bin_end) if bin_end != float('inf') else None,
                "count": count,
                "percentage": round(percentage, 1)
            })
        
        return histogram
    
    def _compute_histogram_by_year(
        self,
        papers_by_year: Dict[int, List[Dict]],
        bins: List[Tuple[int, int]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        计算按年份的直方图
        
        Args:
            papers_by_year: 按年份分组的论文
            bins: 分组列表
        
        Returns:
            按年份的直方图数据字典 {year: [histogram...]}
        """
        histogram_by_year = {}
        
        for year, papers in papers_by_year.items():
            patent_counts = self._extract_patent_counts(papers)
            histogram = self._compute_histogram(patent_counts, bins)
            histogram_by_year[str(year)] = histogram
        
        return histogram_by_year
    
    def _compute_metadata(
        self,
        papers: List[Dict],
        patent_counts: List[int],
        year_min: int,
        year_max: int
    ) -> Dict[str, Any]:
        """
        计算统计元数据
        
        Args:
            papers: 论文列表
            patent_counts: 专利引用数列表
            year_min: 起始年份
            year_max: 结束年份
        
        Returns:
            统计元数据字典
        """
        # 计算基本统计量
        total_papers = len(papers)
        total_patents = sum(patent_counts)
        
        if total_papers > 0:
            avg_patent_count = total_patents / total_papers
        else:
            avg_patent_count = 0
        
        max_patent_count = max(patent_counts) if patent_counts else 0
        min_patent_count = min(patent_counts) if patent_counts else 0
        
        # 计算标准差
        if len(patent_counts) > 1:
            patent_count_std_dev = float(np.std(patent_counts))
        else:
            patent_count_std_dev = 0.0
        
        return {
            "total_papers": total_papers,
            "total_patents": total_patents,
            "avg_patent_count_per_paper": round(avg_patent_count, 1),
            "max_patent_count": int(max_patent_count),
            "min_patent_count": int(min_patent_count),
            "patent_count_std_dev": round(patent_count_std_dev, 1),
            "year_range": {
                "min": year_min,
                "max": year_max
            }
        }

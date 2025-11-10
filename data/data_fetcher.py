"""
Hugging Face Datasets 数据获取模块
用于从 SciSciNet-v2 数据集中获取论文、作者和引用数据
"""
import os
import logging
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)


class HFDatasetFetcher:
    """Hugging Face 数据集获取器"""
    
    def __init__(self, local_dir: str = None):
        """
        初始化 Hugging Face 数据集加载器
        
        Args:
            local_dir: 本地数据集目录路径
        """
        self.local_dir = local_dir or Config.HF_DATASET_LOCAL_DIR
        self.repo_id = "Northwestern-CSSI/sciscinet-v2"
        self._datasets = {}  # 缓存已加载的数据集
        self._initialized = False
        
    def _ensure_downloaded(self):
        """确保数据集已下载"""
        if self._initialized:
            return
            
        local_path = Path(self.local_dir)
        
        # 检查本地是否已有数据集
        if local_path.exists() and any(local_path.iterdir()):
            logger.info(f"✓ 数据集已存在于: {self.local_dir}")
            self._initialized = True
            return
        
        # 下载数据集
        try:
            logger.info(f"正在从 Hugging Face 下载数据集...")
            logger.info(f"Repository: {self.repo_id}")
            
            from huggingface_hub import snapshot_download
            
            snapshot_download(
                repo_id=self.repo_id,
                local_dir=self.local_dir,
                repo_type="dataset",
                resume_download=True
            )
            
            logger.info(f"✓ 数据集下载成功: {self.local_dir}")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"✗ 数据集下载失败: {e}")
            raise
    
    def _load_csv(self, filename: str) -> pd.DataFrame:
        """加载 CSV 文件"""
        self._ensure_downloaded()
        
        filepath = Path(self.local_dir) / filename
        
        if not filepath.exists():
            logger.warning(f"文件不存在: {filepath}")
            return pd.DataFrame()
        
        try:
            logger.info(f"加载数据: {filename}")
            df = pd.read_csv(filepath)
            logger.info(f"✓ 加载成功: {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"加载失败 {filename}: {e}")
            raise
    
    def get_papers_by_year_range(
        self, 
        year_min: int,
        year_max: int,
        limit: int = 1000,
        field: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取指定年份范围的论文数据
        
        Args:
            year_min: 起始年份
            year_max: 结束年份
            limit: 返回数量限制
            field: 研究领域代码（可选）
        
        Returns:
            论文数据DataFrame
        """
        # 加载论文数据
        papers = self._load_csv("papers.csv")
        
        if papers.empty:
            return papers
        
        # 过滤年份范围
        logger.info(f"过滤论文: {year_min}-{year_max}")
        filtered = papers[
            (papers['year'] >= year_min) & 
            (papers['year'] <= year_max)
        ]
        
        # 应用限制
        if limit and len(filtered) > limit:
            filtered = filtered.head(limit)
            logger.info(f"限制数量: {limit}")
        
        logger.info(f"获取成功: {len(filtered)} 篇论文")
        return filtered
    
    def get_authors_by_paperids(self, paper_ids: List[str]) -> pd.DataFrame:
        """
        根据论文ID列表获取作者数据
        
        Args:
            paper_ids: 论文ID列表
        
        Returns:
            作者数据DataFrame
        """
        if not paper_ids:
            return pd.DataFrame()
        
        # 加载作者数据
        authors = self._load_csv("authors.csv")
        
        if authors.empty:
            return authors
        
        # 过滤指定论文的作者
        logger.info(f"获取 {len(paper_ids)} 篇论文的作者数据")
        filtered = authors[authors['paperid'].isin(paper_ids)]
        
        logger.info(f"获取成功: {len(filtered)} 条作者记录")
        return filtered
    
    def get_paper_references(
        self, 
        paper_ids: List[str],
        year_min: int,
        year_max: int
    ) -> pd.DataFrame:
        """
        获取论文之间的引用关系
        
        Args:
            paper_ids: 论文ID列表
            year_min: 起始年份
            year_max: 结束年份
        
        Returns:
            引用关系DataFrame
        """
        if not paper_ids:
            return pd.DataFrame()
        
        # 加载引用数据
        references = self._load_csv("references.csv")
        
        if references.empty:
            return references
        
        # 过滤指定论文的引用
        logger.info(f"获取 {len(paper_ids)} 篇论文的引用关系")
        filtered = references[references['paperid'].isin(paper_ids)]
        
        logger.info(f"获取成功: {len(filtered)} 条引用关系")
        return filtered
    
    def get_author_affiliations(self, author_ids: List[str]) -> pd.DataFrame:
        """
        获取作者的所属机构信息
        
        Args:
            author_ids: 作者ID列表
        
        Returns:
            作者机构DataFrame
        """
        if not author_ids:
            return pd.DataFrame()
        
        # 加载作者数据
        authors = self._load_csv("authors.csv")
        
        if authors.empty:
            return authors
        
        # 过滤指定作者
        logger.info(f"获取 {len(author_ids)} 名作者的机构信息")
        filtered = authors[authors['authorid'].isin(author_ids)]
        
        logger.info(f"获取成功: {len(filtered)} 条记录")
        return filtered
    
    def get_author_details(self, author_id: str) -> Optional[Dict]:
        """
        获取单个作者的详细信息
        
        Args:
            author_id: 作者ID
        
        Returns:
            作者信息字典
        """
        # 加载作者数据
        authors = self._load_csv("authors.csv")
        
        if authors.empty:
            logger.warning(f"作者数据为空")
            return None
        
        # 查找作者
        author_records = authors[authors['authorid'] == author_id]
        
        if author_records.empty:
            logger.warning(f"作者不存在: {author_id}")
            return None
        
        # 统计作者信息
        publication_count = len(author_records['paperid'].unique())
        affiliation_count = len(author_records['affiliationid'].unique()) if 'affiliationid' in author_records.columns else 0
        
        # 获取作者名
        author_name = author_records.iloc[0].get('displayname', 'Unknown')
        
        author_info = {
            "author_id": str(author_id),
            "name": str(author_name),
            "normalized_name": str(author_records.iloc[0].get('normalizedname', '')),
            "publication_count": publication_count,
            "affiliation_count": affiliation_count
        }
        
        logger.info(f"作者详情获取成功: {author_info['name']}")
        return author_info


class DataCache:
    """数据缓存管理（可选Redis）"""
    
    def __init__(self, use_redis: bool = False):
        """
        初始化缓存
        
        Args:
            use_redis: 是否使用Redis缓存
        """
        self.use_redis = use_redis
        self.cache = {}  # 本地内存缓存
        
        if use_redis:
            try:
                import redis
                self.redis_client = redis.Redis(
                    host=Config.REDIS_HOST,
                    port=Config.REDIS_PORT,
                    db=Config.REDIS_DB,
                    decode_responses=True
                )
                logger.info("Redis缓存初始化成功")
            except Exception as e:
                logger.warning(f"Redis初始化失败，使用内存缓存: {e}")
                self.use_redis = False
    
    def get(self, key: str) -> Optional[Dict]:
        """从缓存获取数据"""
        if self.use_redis:
            try:
                import json
                data = self.redis_client.get(key)
                return json.loads(data) if data else None
            except Exception as e:
                logger.warning(f"Redis读取失败: {e}")
                return self.cache.get(key)
        return self.cache.get(key)
    
    def set(self, key: str, value: Dict, timeout: int = None) -> bool:
        """设置缓存数据"""
        if timeout is None:
            timeout = Config.CACHE_TIMEOUT
        
        if self.use_redis:
            try:
                import json
                self.redis_client.setex(key, timeout, json.dumps(value))
                return True
            except Exception as e:
                logger.warning(f"Redis写入失败: {e}")
                self.cache[key] = value
                return False
        
        self.cache[key] = value
        return True


# 向后兼容别名
BigQueryFetcher = HFDatasetFetcher


class DataCache:
    """数据缓存管理（可选Redis）"""
    
    def __init__(self, use_redis: bool = False):
        """
        初始化缓存
        
        Args:
            use_redis: 是否使用Redis缓存
        """
        self.use_redis = use_redis
        self.cache = {}  # 本地内存缓存
        
        if use_redis:
            try:
                import redis
                self.redis_client = redis.Redis(
                    host=Config.REDIS_HOST,
                    port=Config.REDIS_PORT,
                    db=Config.REDIS_DB,
                    decode_responses=True
                )
                logger.info("Redis缓存初始化成功")
            except Exception as e:
                logger.warning(f"Redis初始化失败，使用内存缓存: {e}")
                self.use_redis = False
    
    def get(self, key: str) -> Optional[Dict]:
        """从缓存获取数据"""
        if self.use_redis:
            try:
                import json
                data = self.redis_client.get(key)
                return json.loads(data) if data else None
            except Exception as e:
                logger.warning(f"Redis读取失败: {e}")
                return self.cache.get(key)
        return self.cache.get(key)
    
    def set(self, key: str, value: Dict, timeout: int = None) -> bool:
        """设置缓存数据"""
        if timeout is None:
            timeout = Config.CACHE_TIMEOUT
        
        if self.use_redis:
            try:
                import json
                self.redis_client.setex(key, timeout, json.dumps(value))
                return True
            except Exception as e:
                logger.warning(f"Redis写入失败: {e}")
                self.cache[key] = value
                return False
        
        self.cache[key] = value
        return True

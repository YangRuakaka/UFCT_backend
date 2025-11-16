"""
网络服务层 - 处理所有网络相关的业务逻辑
使用 Repository 层获取数据，专注于业务逻辑
"""
import logging
from typing import Optional, Dict, List, Any
from data import DataCache, get_fetcher
from models import CitationNetwork, CollaborationNetwork
from config import Config
from api.repositories import NetworkRepository
from api.utils.name_resolver import (
    resolve_institution_name_to_id,
    resolve_discipline_name_to_id
)
from api.exceptions import (
    DataFetchException,
    ValidationException,
    NetworkAnalysisException
)

logger = logging.getLogger(__name__)


def calculate_network_stats(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """
    计算网络统计信息
    
    Args:
        nodes: 节点列表
        edges: 边列表
    
    Returns:
        统计信息字典
    """
    if not nodes or not edges:
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "density": 0.0,
            "avg_degree": 0.0,
        }
    
    # 计算度数
    degrees = {}
    for node in nodes:
        degrees[node.get('id')] = 0
    
    for edge in edges:
        source = edge.get('source')
        target = edge.get('target')
        if source in degrees:
            degrees[source] += 1
        if target in degrees:
            degrees[target] += 1
    
    # 计算统计值
    node_count = len(nodes)
    edge_count = len(edges)
    avg_degree = sum(degrees.values()) / node_count if node_count > 0 else 0
    max_degree = max(degrees.values()) if degrees else 0
    
    # 网络密度 = 2 * 边数 / (节点数 * (节点数 - 1))
    density = (2 * edge_count) / (node_count * (node_count - 1)) if node_count > 1 else 0
    
    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "density": round(density, 4),
        "avg_degree": round(avg_degree, 2),
        "max_degree": max_degree,
    }


class NetworkService:
    """网络服务 - 处理引用网络和协作网络"""
    
    def __init__(self, use_redis: bool = False):
        """初始化网络服务"""
        self.repository = NetworkRepository()
        self.fetcher = get_fetcher()
        self.cache = DataCache(use_redis=use_redis)
    
    def get_citation_network(
        self,
        year_min: int = 2020,
        year_max: int = 2024,
        limit: int = 500,
        university: Optional[str] = None,
        discipline: Optional[str] = None,
        min_citations: int = 0
    ) -> Dict:
        """
        获取论文引用网络
        
        Args:
            year_min: 起始年份
            year_max: 结束年份
            limit: 节点数限制
            university: 大学名称或ID（自动转换）
            discipline: 学科名称或ID（自动转换）
            min_citations: 最少引用次数
        
        Returns:
            包含引用网络数据的字典
        """
        
        logger.info(f"获取引用网络: {year_min}-{year_max}, limit={limit}, discipline={discipline}, university={university}")
        
        try:
            # 自动转换名称为ID
            resolved_discipline = resolve_discipline_name_to_id(discipline)
            resolved_university = resolve_institution_name_to_id(university)
            
            # 生成缓存键
            cache_key = self._generate_cache_key(
                'citation', year_min, year_max, limit,
                resolved_university, resolved_discipline, min_citations
            )
            
            # 尝试从缓存获取
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.info(f"缓存命中: {cache_key}")
                return {**cached_data, "cached": True}
            
            # 直接调用 repository，传递过滤参数
            nodes, edges = self.repository.get_citation_network_data(
                year_min=year_min,
                year_max=year_max,
                limit=limit,
                discipline=resolved_discipline,
                institution=resolved_university
            )
            
            if not nodes:
                raise DataFetchException("未获取到论文数据")
            
            # 如果 edges 是生成器，转换为列表（用于普通模式）
            if hasattr(edges, '__next__'):
                edges = list(edges)
            
            # 按引用次数过滤
            if min_citations > 0:
                nodes = self.repository.filter_papers_by_citations(nodes, min_citations)
            
            if not nodes:
                raise DataFetchException("过滤后无论文数据")
            
            # 构建网络
            network = CitationNetwork()
            network.build_from_openalex(nodes, edges, min_citations=min_citations)
            
            response_data = {
                'status': 'success',
                'data': network.to_json(),
                'summary': {
                    'nodes_count': len(nodes),
                    'edges_count': len(network.edges)  # 从网络获取边数，而不是从生成器
                }
            }
            
            # 添加查询参数信息
            if discipline or university:
                response_data['query_params'] = {
                    'discipline': discipline,
                    'discipline_id': resolved_discipline,
                    'university': university,
                    'university_id': resolved_university,
                    'year_min': year_min,
                    'year_max': year_max,
                    'min_citations': min_citations
                }
            
            # 缓存结果
            self.cache.set(cache_key, {
                "status": "success",
                "data": response_data["data"]
            })
            
            return response_data
            
        except DataFetchException as e:
            logger.warning(f"业务验证失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"构建引用网络失败: {str(e)}", exc_info=True)
            raise NetworkAnalysisException(f"引用网络分析失败: {str(e)}")
    
    def get_citation_network_streaming(
        self,
        year_min: int = 2020,
        year_max: int = 2024,
        limit: int = 500,
        university: Optional[str] = None,
        discipline: Optional[str] = None,
        min_citations: int = 0,
        batch_size: int = 1000
    ) -> Dict[str, Any]:
        """
        获取大规模引用网络（流式处理版本，解决内存溢出问题）
        
        原理：
        1. 将论文分成多个批次（每批 batch_size 篇）
        2. 逐批获取论文和引用关系
        3. 逐批构建网络图
        4. 最后合并所有图
        
        优点：内存占用恒定，不会因论文数量增加而指数级增长
        
        Args:
            year_min: 起始年份
            year_max: 结束年份
            limit: 论文数量限制
            university: 机构名称
            discipline: 学科名称
            min_citations: 最小引用次数过滤
            batch_size: 每批处理的论文数（默认 1000）
        
        Returns:
            包含引用网络数据的字典
        """
        
        logger.info(f"获取引用网络（流式模式）: {year_min}-{year_max}, limit={limit}, batch_size={batch_size}")
        
        try:
            # 自动转换名称为ID
            resolved_discipline = resolve_discipline_name_to_id(discipline)
            resolved_university = resolve_institution_name_to_id(university)
            
            # 生成缓存键
            cache_key = self._generate_cache_key(
                'citation_stream', year_min, year_max, limit,
                resolved_university, resolved_discipline, min_citations
            )
            
            # 尝试从缓存获取
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.info(f"缓存命中: {cache_key}")
                return {**cached_data, "cached": True}
            
            logger.info(f"使用流式处理模式获取大规模引用网络（批次大小: {batch_size}）")
            
            # 直接调用 repository 获取所有论文（不分批）
            # 但在构建网络时分批处理
            nodes, edges_generator = self.repository.get_citation_network_data(
                year_min=year_min,
                year_max=year_max,
                limit=limit,
                discipline=resolved_discipline,
                institution=resolved_university
            )
            
            if not nodes:
                raise DataFetchException("未获取到论文数据")
            
            logger.info(f"总共获取 {len(nodes)} 篇论文")
            logger.info(f"边数据采用生成器模式处理，不占用额外内存")
            
            # 按引用次数过滤
            if min_citations > 0:
                nodes = self.repository.filter_papers_by_citations(nodes, min_citations)
            
            if not nodes:
                raise DataFetchException("过滤后无论文数据")
            
            # 使用流式构建方法构建网络
            network = CitationNetwork()
            
            # 流式构建：逐个消费边生成器，分批添加以降低内存峰值
            logger.info("开始流式构建网络图...")
            network.build_from_openalex_streaming_generator(
                nodes, 
                edges_generator,  # 现在是生成器
                min_citations=min_citations,
                batch_size=batch_size
            )
            
            # 计算边数（从网络统计）
            edges_count = len(network.edges)
            
            response_data = {
                'status': 'success',
                'data': network.to_json(),
                'summary': {
                    'nodes_count': len(nodes),
                    'edges_count': edges_count,
                    'processing_mode': 'streaming'
                }
            }
            
            # 添加查询参数信息
            if discipline or university:
                response_data['query_params'] = {
                    'discipline': discipline,
                    'discipline_id': resolved_discipline,
                    'university': university,
                    'university_id': resolved_university,
                    'year_min': year_min,
                    'year_max': year_max,
                    'min_citations': min_citations
                }
            
            # 缓存结果
            self.cache.set(cache_key, {
                "status": "success",
                "data": response_data["data"]
            })
            
            return response_data
            
        except DataFetchException as e:
            logger.warning(f"业务验证失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"流式构建引用网络失败: {str(e)}", exc_info=True)
            raise NetworkAnalysisException(f"引用网络分析失败: {str(e)}")
    
    def get_collaboration_network(
        self,
        year_min: int = Config.DEFAULT_YEAR_MIN,
        year_max: int = Config.DEFAULT_YEAR_MAX,
        limit: int = Config.DEFAULT_LIMIT,
        min_collaborations: int = 1,
        university: Optional[str] = None,
        discipline: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取作者协作网络（支持多维度过滤）
        
        Args:
            year_min: 起始年份
            year_max: 结束年份
            limit: 论文数限制
            min_collaborations: 最少协作次数
            university: 大学名称或ID（自动转换）
            discipline: 学科名称或ID（自动转换）
        
        Returns:
            包含协作网络数据的字典
        """
        try:
            limit = min(limit, Config.MAX_NODES)
            
            # 自动转换名称为ID
            resolved_discipline = resolve_discipline_name_to_id(discipline)
            resolved_university = resolve_institution_name_to_id(university)
            
            # 生成缓存键
            cache_key = self._generate_cache_key(
                'collaboration', year_min, year_max, limit,
                resolved_university, resolved_discipline, min_collaborations
            )
            
            # 尝试从缓存获取
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.info(f"缓存命中: {cache_key}")
                return {**cached_data, "cached": True}
            
            logger.info(
                f"获取协作网络: {year_min}-{year_max}, "
                f"limit={limit}, discipline={discipline}->{resolved_discipline}, "
                f"university={university}->{resolved_university}, min_collaborations={min_collaborations}"
            )
            
            # ===== 使用 Repository 层获取数据 =====
            # 1. 获取论文（先获取基础数据，后续再过滤）
            papers = self.repository.get_papers_by_year_range(
                year_min=year_min,
                year_max=year_max,
                limit=limit,  # 获取更多数据以补偿后续过滤
                discipline=resolved_discipline,
                institution=resolved_university
            )
            
            if not papers:
                raise DataFetchException("未获取到论文数据")
            
            logger.info(f"✓ 获取 {len(papers)} 篇论文")
            
            # 2. 获取作者
            paper_ids = [p.get('id') for p in papers if p.get('id')]
            authors = self.repository.get_authors_by_work_ids(paper_ids)
            if not authors:
                raise DataFetchException("未获取到作者数据")
            
            logger.info(f"✓ 获取 {len(authors)} 位作者")
            
            # 3. 获取协作关系
            author_ids = [a.get('id') for a in authors if a.get('id')]
            collaborations = self.repository.get_collaboration_data(author_ids)
            
            # 4. 按协作权重过滤
            collaborations = self.repository.filter_collaborations_by_weight(
                collaborations, min_collaborations
            )
            
            # ===== 业务逻辑处理 =====
            # 5. 构建网络模型
            collab_net = CollaborationNetwork()
            collab_net.build_from_openalex(
                authors, collaborations, 
                min_collaborations=min_collaborations
            )
            
            # 6. 计算统计信息
            stats = collab_net.get_network_statistics()
            communities = collab_net.detect_communities()
            
            # 7. 构建响应
            response_data = {
                "status": "success",
                "data": {
                    "network": collab_net.to_json(),
                    "statistics": stats,
                    "communities": communities
                },
                "cached": False
            }
            
            # 8. 添加查询参数（如果有过滤）
            if discipline or university:
                response_data["data"]["query_params"] = {
                    "university": university,
                    "university_id": resolved_university,
                    "discipline": discipline,
                    "discipline_id": resolved_discipline,
                    "year_min": year_min,
                    "year_max": year_max,
                    "limit": limit,
                    "min_collaborations": min_collaborations
                }
            
            # 9. 缓存结果
            self.cache.set(cache_key, {
                "status": "success",
                "data": response_data["data"]
            })
            
            return response_data
            
        except (DataFetchException, ValidationException) as e:
            logger.warning(f"业务验证失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"获取协作网络失败: {str(e)}", exc_info=True)
            raise NetworkAnalysisException(f"协作网络分析失败: {str(e)}")
    
    @staticmethod
    def _generate_cache_key(
        prefix: str, 
        year_min: int, 
        year_max: int, 
        limit: int,
        university: Optional[str] = None,
        discipline: Optional[str] = None,
        filter_param: int = 0
    ) -> str:
        """生成缓存键"""
        parts = [prefix, year_min, year_max, limit]
        if university:
            parts.append(f"uni_{university}")
        if discipline:
            parts.append(f"disc_{discipline}")
        if filter_param > 0:
            parts.append(f"filter_{filter_param}")
        return ":".join(str(p) for p in parts)

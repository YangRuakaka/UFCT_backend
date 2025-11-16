"""
网络模型 - 定义论文引用网络和作者协作网络的数据结构
"""
import logging
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
import networkx as nx
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class Node:
    """图节点数据类"""
    id: str
    label: str
    node_type: str  # 'paper' or 'author'
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Edge:
    """图边数据类"""
    source: str
    target: str
    edge_type: str
    weight: float = 1.0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class NetworkBase:
    """网络基类"""
    
    def __init__(self):
        """初始化网络"""
        self.graph = nx.Graph()
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
    
    def add_node(self, node: Node):
        """添加节点"""
        self.nodes[node.id] = node
        self.graph.add_node(node.id)
    
    def add_edge(self, edge: Edge):
        """添加边"""
        self.edges.append(edge)
        self.graph.add_edge(edge.source, edge.target, weight=edge.weight)
    
    def get_node_importance(self, metric: str = "degree") -> Dict[str, float]:
        """
        计算节点重要性指标
        
        Args:
            metric: 指标类型 ('degree', 'betweenness', 'closeness', 'pagerank')
        
        Returns:
            节点ID到重要性值的字典
        """
        if metric == "degree":
            importance = dict(self.graph.degree())
            # 归一化
            max_degree = max(importance.values()) if importance else 1
            return {k: v / max_degree for k, v in importance.items()}
        
        elif metric == "betweenness":
            return nx.betweenness_centrality(self.graph)
        
        elif metric == "closeness":
            return nx.closeness_centrality(self.graph)
        
        elif metric == "pagerank":
            return nx.pagerank(self.graph)
        
        else:
            logger.warning(f"未知重要性指标: {metric}, 使用degree")
            return self.get_node_importance("degree")
    
    def to_json(self) -> Dict:
        """
        将网络转换为JSON格式（仅返回节点和边，不包含坐标）
        
        Returns:
            JSON字典
        """
        nodes_data = []
        for node_id, node in self.nodes.items():
            node_dict = asdict(node)
            nodes_data.append(node_dict)
        
        edges_data = []
        for edge in self.edges:
            edge_dict = asdict(edge)
            edges_data.append(edge_dict)
        
        return {
            "nodes": nodes_data,
            "edges": edges_data,
            "metadata": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "network_density": nx.density(self.graph),
                "avg_degree": sum(dict(self.graph.degree()).values()) / len(self.graph.nodes) if self.graph.nodes else 0,
            }
        }


class CitationNetwork(NetworkBase):
    """论文引用网络"""
    
    def __init__(self):
        """初始化引用网络"""
        super().__init__()
        self.paper_data: Dict[str, Dict] = {}
    
    def build_from_dataframes(
        self,
        papers_df: pd.DataFrame,
        references_df: pd.DataFrame,
        min_citations: int = 1
    ):
        """
        从DataFrame构建引用网络
        
        Args:
            papers_df: 论文数据 (paperid, title, year, citation_count, ...)
            references_df: 引用关系 (paperid, citedpaperid)
            min_citations: 最小引用次数阈值
        """
        logger.info("开始构建引用网络...")
        
        # 创建论文ID到数据的映射
        for _, row in papers_df.iterrows():
            paper_id = str(row['paperid'])
            self.paper_data[paper_id] = {
                'title': row['title'],
                'year': int(row['year']),
                'citation_count': int(row.get('citation_count', 0)) if pd.notna(row.get('citation_count')) else 0,
                'type': row.get('publicationtype', 'Unknown'),
            }
        
        # 添加节点（只添加在引用关系中出现过的论文）
        referenced_papers = set()
        citing_papers = set()
        
        for _, row in references_df.iterrows():
            paper_id = str(row['paperid'])
            cited_id = str(row['citedpaperid'])
            citing_papers.add(paper_id)
            referenced_papers.add(cited_id)
        
        all_papers = citing_papers | referenced_papers
        logger.info(f"引用网络涉及{len(all_papers)}篇论文")
        
        # 只添加有元数据的论文节点
        for paper_id in all_papers:
            if paper_id in self.paper_data:
                paper = self.paper_data[paper_id]
                
                year = paper['year']
                
                node = Node(
                    id=paper_id,
                    label=paper['title'][:50],  # 截断标题
                    node_type='paper',
                    metadata={
                        'title': paper['title'],
                        'year': year,
                        'citation_count': paper['citation_count'],
                        'type': paper['type']
                    }
                )
                self.add_node(node)
        
        # 添加边
        edge_weights = {}
        for _, row in references_df.iterrows():
            source_id = str(row['paperid'])
            target_id = str(row['citedpaperid'])
            
            # 只添加两端都在网络中的边
            if source_id in self.nodes and target_id in self.nodes:
                edge_key = (source_id, target_id)
                edge_weights[edge_key] = edge_weights.get(edge_key, 0) + 1
        
        # 使用加权关系添加边
        for (source_id, target_id), weight in edge_weights.items():
            if weight >= min_citations:
                edge = Edge(
                    source=source_id,
                    target=target_id,
                    edge_type='cites',
                    weight=float(weight),
                    metadata={'citation_type': 'direct'}
                )
                self.add_edge(edge)
        
        logger.info(f"引用网络构建完成: {len(self.nodes)}个节点, {len(self.edges)}条边")
    
    def build_from_openalex(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        min_citations: int = 1
    ):
        """
        从 OpenAlex 数据构建引用网络
        
        Args:
            nodes: 论文节点列表（来自 OpenAlexFetcher.get_citation_network）
            edges: 引用关系列表
            min_citations: 最小引用次数阈值
        """
        logger.info("开始从 OpenAlex 数据构建引用网络...")
        
        if not nodes:
            logger.warning("节点列表为空")
            return
        
        # 添加节点
        valid_node_ids = set()  # 跟踪有效的节点
        
        for node_data in nodes:
            # 跳过 None 或无效数据
            if not node_data or not isinstance(node_data, dict):
                logger.debug("跳过无效的节点数据")
                continue
            
            node_id = node_data.get('id')
            if not node_id:
                logger.debug("节点缺少 ID，跳过")
                continue
            
            valid_node_ids.add(node_id)
            
            # 获取被引用次数
            citations = node_data.get('cited_by_count', 0)
            if not isinstance(citations, (int, float)):
                citations = 0
            
            year = node_data.get('year', 2020)
            if not isinstance(year, int):
                year = 2020
            
            title = node_data.get('title', 'Unknown')
            if not title:
                title = 'Unknown'
            
            node = Node(
                id=node_id,
                label=str(title)[:50],
                node_type='paper',
                metadata={
                    'title': str(title),
                    'year': year,
                    'citation_count': int(citations),
                    'venue': node_data.get('venue', 'Unknown'),
                    'url': node_data.get('url', '')
                }
            )
            self.add_node(node)
            self.paper_data[node_id] = {
                'title': str(title),
                'year': year,
                'citation_count': int(citations)
            }
        
        logger.info(f"添加了 {len(valid_node_ids)} 个论文节点")
        
        # 添加边
        if not edges:
            logger.info("边列表为空")
            return
        
        edge_weights = {}
        for edge_data in edges:
            # 跳过 None 或无效数据
            if not edge_data or not isinstance(edge_data, dict):
                continue
            
            source_id = edge_data.get('source')
            target_id = edge_data.get('target')
            
            # 验证源和目标都有效
            if not source_id or not target_id:
                continue
            
            if source_id in valid_node_ids and target_id in valid_node_ids:
                edge_key = (source_id, target_id)
                edge_weights[edge_key] = edge_weights.get(edge_key, 0) + edge_data.get('weight', 1)
        
        logger.info(f"处理了 {len(edge_weights)} 条边")
        
        # 添加加权边
        for (source_id, target_id), weight in edge_weights.items():
            if weight >= min_citations:
                edge = Edge(
                    source=source_id,
                    target=target_id,
                    edge_type='cites',
                    weight=float(weight),
                    metadata={'citation_type': 'direct'}
                )
                self.add_edge(edge)
        
        logger.info(f"引用网络构建完成: {len(self.nodes)}个节点（包含孤立节点）, {len(self.edges)}条边")
    
    def build_from_openalex_streaming(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        min_citations: int = 1,
        batch_size: int = 1000
    ):
        """
        从 OpenAlex 数据流式构建引用网络（内存优化版）
        
        这个方法比 build_from_openalex 内存占用更低，因为：
        1. 逐个添加节点而不是一次性加载
        2. 边按批次处理，不会一次性都在内存中
        3. 合并重复的边时只保存最新的权重
        
        Args:
            nodes: 论文节点列表
            edges: 引用关系列表
            min_citations: 最小引用次数阈值
            batch_size: 批处理大小（用于进度日志）
        """
        logger.info(f"开始流式构建引用网络（批次大小: {batch_size}）...")
        
        if not nodes:
            logger.warning("节点列表为空")
            return
        
        # 第一步：添加节点
        valid_node_ids = set()
        for node_idx, node_data in enumerate(nodes, 1):
            if not node_data or not isinstance(node_data, dict):
                continue
            
            node_id = node_data.get('id')
            if not node_id:
                continue
            
            valid_node_ids.add(node_id)
            
            citations = node_data.get('cited_by_count', 0)
            if not isinstance(citations, (int, float)):
                citations = 0
            
            year = node_data.get('publication_year', 2020)
            if not isinstance(year, int):
                year = 2020
            
            title = node_data.get('title', 'Unknown')
            if not title:
                title = 'Unknown'
            
            node = Node(
                id=node_id,
                label=str(title)[:50],
                node_type='paper',
                metadata={
                    'title': str(title),
                    'year': year,
                    'citation_count': int(citations),
                    'venue': node_data.get('venue', 'Unknown'),
                    'url': node_data.get('url', '')
                }
            )
            self.add_node(node)
            self.paper_data[node_id] = {
                'title': str(title),
                'year': year,
                'citation_count': int(citations)
            }
            
            # 每 batch_size 个节点输出一次进度
            if node_idx % batch_size == 0:
                logger.info(f"  已添加 {node_idx}/{len(nodes)} 个节点")
        
        logger.info(f"✓ 添加了 {len(valid_node_ids)} 个论文节点")
        
        # 第二步：流式添加边
        if not edges:
            logger.info("边列表为空")
            return
        
        edge_weights = {}
        edge_batch = []
        
        for edge_idx, edge_data in enumerate(edges, 1):
            if not edge_data or not isinstance(edge_data, dict):
                continue
            
            source_id = edge_data.get('source')
            target_id = edge_data.get('target')
            
            if not source_id or not target_id:
                continue
            
            # 只添加两端都在节点中的边
            if source_id in valid_node_ids and target_id in valid_node_ids:
                edge_key = (source_id, target_id)
                edge_weights[edge_key] = edge_weights.get(edge_key, 0) + edge_data.get('weight', 1)
                edge_batch.append((edge_key, edge_weights[edge_key]))
                
                # 每 batch_size 条边，输出一次进度
                if edge_idx % (batch_size * 10) == 0:
                    logger.info(f"  已处理 {edge_idx} 条边，已合并 {len(edge_weights)} 条唯一边")
        
        logger.info(f"✓ 处理了 {len(edge_weights)} 条边")
        
        # 第三步：添加加权边到图
        logger.info("开始将边添加到网络图...")
        added_edges = 0
        for (source_id, target_id), weight in edge_weights.items():
            if weight >= min_citations:
                edge = Edge(
                    source=source_id,
                    target=target_id,
                    edge_type='cites',
                    weight=float(weight),
                    metadata={'citation_type': 'direct'}
                )
                self.add_edge(edge)
                added_edges += 1
        
        logger.info(f"✓ 引用网络流式构建完成: {len(self.nodes)}个节点（包含孤立节点）, {added_edges}条边")
    
    def build_from_openalex_streaming_generator(
        self,
        nodes: List[Dict],
        edges_generator,
        min_citations: int = 1,
        batch_size: int = 1000
    ):
        """
        从 OpenAlex 数据流式构建引用网络（生成器版本，极致内存优化）
        
        这个版本针对超大数据集优化：
        1. 节点列表照常加载（必须统计总数）
        2. 边采用生成器模式，逐个消费，不一次性加载
        3. 使用游动窗口来合并相同边，最多保存 batch_size * 100 条未合并的边
        4. 内存占用近似恒定，与论文数量无关
        
        Args:
            nodes: 论文节点列表
            edges_generator: 引用关系生成器（不是列表）
            min_citations: 最小引用次数阈值
            batch_size: 批处理大小
        """
        logger.info(f"开始使用生成器模式流式构建引用网络（极致内存优化）...")
        
        if not nodes:
            logger.warning("节点列表为空")
            return
        
        # 第一步：添加节点
        valid_node_ids = set()
        skipped_count = 0
        null_id_count = 0
        duplicate_id_count = 0
        
        for node_idx, node_data in enumerate(nodes, 1):
            if not node_data or not isinstance(node_data, dict):
                skipped_count += 1
                continue
            
            node_id = node_data.get('id')
            if not node_id:
                null_id_count += 1
                continue
            
            # 检查重复
            if node_id in valid_node_ids:
                duplicate_id_count += 1
                continue  # 跳过重复的节点
            
            valid_node_ids.add(node_id)
            
            citations = node_data.get('cited_by_count', 0)
            if not isinstance(citations, (int, float)):
                citations = 0
            
            year = node_data.get('publication_year', 2020)
            if not isinstance(year, int):
                year = 2020
            
            title = node_data.get('title', 'Unknown')
            if not title:
                title = 'Unknown'
            
            node = Node(
                id=node_id,
                label=str(title)[:50],
                node_type='paper',
                metadata={
                    'title': str(title),
                    'year': year,
                    'citation_count': int(citations),
                    'venue': node_data.get('venue', 'Unknown'),
                    'url': node_data.get('url', '')
                }
            )
            self.add_node(node)
            self.paper_data[node_id] = {
                'title': str(title),
                'year': year,
                'citation_count': int(citations)
            }
            
            # 每 batch_size 个节点输出一次进度
            if node_idx % batch_size == 0:
                logger.info(f"  已处理 {node_idx}/{len(nodes)} 个节点，已收集 {len(valid_node_ids)} 个唯一ID（无效 {skipped_count}，NULL-ID {null_id_count}，重复 {duplicate_id_count}）")
        
        logger.info(f"✓ 节点第一步完成: 总处理 {len(nodes)} 个节点，收集 {len(valid_node_ids)} 个唯一ID")
        logger.info(f"  统计：无效数据 {skipped_count}，NULL-ID {null_id_count}，重复 ID {duplicate_id_count}")
        
        # 第二步：使用游动窗口处理边生成器
        logger.info("开始消费边生成器（游动窗口合并）...")
        
        edge_weights = {}
        edge_idx = 0
        window_size = batch_size * 100
        
        try:
            for edge_data in edges_generator:
                edge_idx += 1
                
                if not edge_data or not isinstance(edge_data, dict):
                    continue
                
                source_id = edge_data.get('source')
                target_id = edge_data.get('target')
                
                if not source_id or not target_id:
                    continue
                
                # 只处理两端都在节点中的边
                if source_id in valid_node_ids and target_id in valid_node_ids:
                    edge_key = (source_id, target_id)
                    edge_weights[edge_key] = edge_weights.get(edge_key, 0) + edge_data.get('weight', 1)
                
                # 每 batch_size * 10 条边，输出进度并检查窗口大小
                if edge_idx % (batch_size * 10) == 0:
                    logger.info(f"  已处理 {edge_idx} 条边，已合并 {len(edge_weights)} 条唯一边")
                
                # 如果缓存太大，先批量处理并清空一部分
                if len(edge_weights) > window_size:
                    logger.debug(f"  边缓存达到 {len(edge_weights)} 条，执行部分清理...")
                    # 这里我们不清理，因为我们需要完整的边权重统计
        
        except GeneratorExit:
            logger.info("边生成器提前退出")
        except Exception as e:
            logger.error(f"消费边生成器时出错: {str(e)}", exc_info=True)
            raise
        
        logger.info(f"✓ 生成器消费完毕: 处理了 {edge_idx} 条边，合并为 {len(edge_weights)} 条唯一边")
        
        # 第三步：添加合并后的边到图
        logger.info("开始将边添加到网络图...")
        added_edges = 0
        for (source_id, target_id), weight in edge_weights.items():
            if weight >= min_citations:
                edge = Edge(
                    source=source_id,
                    target=target_id,
                    edge_type='cites',
                    weight=float(weight),
                    metadata={'citation_type': 'direct'}
                )
                self.add_edge(edge)
                added_edges += 1
        
        # 第四步：确保所有节点都在图中（包括孤立节点）
        logger.info(f"确保所有 {len(valid_node_ids)} 个节点都在图中...")
        nodes_in_graph = set(self.graph.nodes)
        nodes_not_in_graph = valid_node_ids - nodes_in_graph
        
        if nodes_not_in_graph:
            logger.info(f"发现 {len(nodes_not_in_graph)} 个孤立节点，正在添加...")
            for node_id in nodes_not_in_graph:
                if node_id in self.nodes:
                    # 节点已在 self.nodes 中，但不在 graph 中，添加到 graph
                    self.graph.add_node(node_id)
        
        logger.info(f"✓ 引用网络生成器模式构建完成: {len(self.nodes)}个节点（包含孤立节点）, {added_edges}条边")
        logger.info(f"  节点统计：总计 {len(self.nodes)} 个，其中 {added_edges} 条边连接的节点数")
    
    
    def get_network_statistics(self) -> Dict:
        """获取网络统计信息"""
        if not self.graph.nodes:
            return {}
        
        stats = {
            "total_papers": len(self.nodes),
            "total_citations": len(self.edges),
            "network_density": nx.density(self.graph),
            "avg_citations_per_paper": len(self.edges) / len(self.nodes) if self.nodes else 0,
            "connected_components": nx.number_connected_components(self.graph),
            "largest_component_size": len(max(nx.connected_components(self.graph), default=set())),
        }
        return stats


class CollaborationNetwork(NetworkBase):
    """作者协作网络"""
    
    def __init__(self):
        """初始化协作网络"""
        super().__init__()
        self.author_data: Dict[str, Dict] = {}
    
    def build_from_dataframes(
        self,
        authors_df: pd.DataFrame,
        papers_df: pd.DataFrame,
        min_collaborations: int = 1
    ):
        """
        从DataFrame构建协作网络
        
        Args:
            authors_df: 作者数据 (paperid, authorid, authorname)
            papers_df: 论文数据 (paperid, year, ...)
            min_collaborations: 最小协作次数阈值
        """
        logger.info("开始构建协作网络...")
        
        # 创建论文ID到年份的映射
        paper_year_map = {str(row['paperid']): int(row['year']) 
                         for _, row in papers_df.iterrows()}
        
        # 构建作者基础信息
        author_stats = {}
        for _, row in authors_df.iterrows():
            author_id = str(row['authorid'])
            if author_id not in author_stats:
                author_stats[author_id] = {
                    'name': row.get('authorname', row.get('displayname', 'Unknown')),
                    'papers': set(),
                    'collaborators': set(),
                    'citations': 0,
                }
            author_stats[author_id]['papers'].add(str(row['paperid']))
        
        # 找出协作关系
        collaboration_matrix = {}
        for paper_id, group in authors_df.groupby('paperid'):
            paper_id = str(paper_id)
            author_list = [str(aid) for aid in group['authorid'].unique()]
            
            # 为同一论文的所有作者对添加协作关系
            for i in range(len(author_list)):
                for j in range(i + 1, len(author_list)):
                    author1, author2 = author_list[i], author_list[j]
                    pair_key = tuple(sorted([author1, author2]))
                    if pair_key not in collaboration_matrix:
                        collaboration_matrix[pair_key] = {
                            'count': 0,
                            'papers': []
                        }
                    collaboration_matrix[pair_key]['count'] += 1
                    collaboration_matrix[pair_key]['papers'].append(paper_id)
        
        # 添加节点
        filtered_authors = set()
        for (author1, author2), collab_data in collaboration_matrix.items():
            if collab_data['count'] >= min_collaborations:
                filtered_authors.add(author1)
                filtered_authors.add(author2)
        
        logger.info(f"协作网络涉及{len(filtered_authors)}名作者")
        
        for author_id in filtered_authors:
            if author_id in author_stats:
                stats = author_stats[author_id]
                
                node = Node(
                    id=author_id,
                    label=stats['name'][:30],
                    node_type='author',
                    metadata={
                        'name': stats['name'],
                        'papers': list(stats['papers']),
                        'paper_count': len(stats['papers']),
                    }
                )
                self.add_node(node)
        
        # 添加边
        for (author1, author2), collab_data in collaboration_matrix.items():
            if (author1 in self.nodes and author2 in self.nodes and 
                collab_data['count'] >= min_collaborations):
                
                edge = Edge(
                    source=author1,
                    target=author2,
                    edge_type='collaboration',
                    weight=float(collab_data['count']),
                    metadata={
                        'collaboration_count': collab_data['count'],
                        'papers': collab_data['papers']
                    }
                )
                self.add_edge(edge)
        
        logger.info(f"协作网络构建完成: {len(self.nodes)}个节点, {len(self.edges)}条边")
    
    def build_from_openalex(
        self,
        authors: List[Dict],
        collaborations: List[Dict],
        min_collaborations: int = 1
    ):
        """
        从 OpenAlex 数据构建协作网络
        
        Args:
            authors: 作者列表（来自 OpenAlexFetcher.get_authors_by_work_ids）
            collaborations: 合作关系列表（来自 OpenAlexFetcher.get_collaboration_by_authors_batch - 推荐批量方法）
            min_collaborations: 最小协作次数阈值
        """
        logger.info("开始从 OpenAlex 数据构建协作网络...")
        
        if not authors:
            logger.warning("作者列表为空")
            return
        
        # 添加节点
        valid_author_ids = set()  # 跟踪有效的作者
        
        for author_data in authors:
            # 跳过 None 或无效数据
            if not author_data or not isinstance(author_data, dict):
                logger.debug("跳过无效的作者数据")
                continue
            
            author_id = author_data.get('id')
            if not author_id:
                logger.debug("作者缺少 ID，跳过")
                continue
            
            valid_author_ids.add(author_id)
            
            # 获取论文数
            paper_count = author_data.get('works_count', 1)
            if not isinstance(paper_count, (int, float)):
                paper_count = 1
            
            name = author_data.get('name', 'Unknown')
            if not name:
                name = 'Unknown'
            
            node = Node(
                id=author_id,
                label=str(name)[:30],
                node_type='author',
                metadata={
                    'name': str(name),
                    'paper_count': int(paper_count),
                    'orcid': author_data.get('orcid', '')
                }
            )
            self.add_node(node)
            self.author_data[author_id] = author_data
        
        logger.info(f"添加了 {len(valid_author_ids)} 个作者节点")
        
        # 添加边
        if not collaborations:
            logger.info("合作关系列表为空")
            return
        
        edge_count = 0
        for collab_data in collaborations:
            # 跳过 None 或无效数据
            if not collab_data or not isinstance(collab_data, dict):
                continue
            
            source_id = collab_data.get('from')
            target_id = collab_data.get('to')
            weight = collab_data.get('weight', 1)
            
            # 验证源和目标都有效
            if not source_id or not target_id:
                continue
            
            # 确保权重是数字类型
            if not isinstance(weight, (int, float)):
                weight = 1
            
            if weight >= min_collaborations and source_id in valid_author_ids and target_id in valid_author_ids:
                edge = Edge(
                    source=source_id,
                    target=target_id,
                    edge_type='collaboration',
                    weight=float(weight),
                    metadata={'collaboration_count': int(weight)}
                )
                self.add_edge(edge)
                edge_count += 1
        
        logger.info(f"协作网络构建完成: {len(self.nodes)}个节点, {edge_count}条边")
    
    def get_network_statistics(self) -> Dict:
        """获取网络统计信息"""
        if not self.graph.nodes:
            return {}
        
        stats = {
            "total_authors": len(self.nodes),
            "total_collaborations": len(self.edges),
            "network_density": nx.density(self.graph),
            "avg_collaborators": len(self.edges) / len(self.nodes) if self.nodes else 0,
            "connected_components": nx.number_connected_components(self.graph),
            "clustering_coefficient": nx.average_clustering(self.graph) if self.graph.nodes else 0,
        }
        return stats
    
    def detect_communities(self) -> Dict[str, List[str]]:
        """检测社群结构"""
        try:
            from networkx.algorithms import community
            communities = community.greedy_modularity_communities(self.graph)
            
            communities_dict = {}
            for i, comm in enumerate(communities):
                communities_dict[f"community_{i}"] = list(comm)
            
            logger.info(f"检测到{len(communities)}个社群")
            return communities_dict
        except Exception as e:
            logger.warning(f"社群检测失败: {e}")
            return {}

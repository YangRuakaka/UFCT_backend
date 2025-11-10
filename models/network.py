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
    size: float = 1.0
    color: str = "#4ECDC4"
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
    label: str = ""
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
        self.layout: Dict[str, Tuple[float, float]] = {}  # node_id -> (x, y)
    
    def add_node(self, node: Node):
        """添加节点"""
        self.nodes[node.id] = node
        self.graph.add_node(node.id)
    
    def add_edge(self, edge: Edge):
        """添加边"""
        self.edges.append(edge)
        self.graph.add_edge(edge.source, edge.target, weight=edge.weight)
    
    def compute_layout(self, algorithm: str = "spring", iterations: int = 50, k: float = 0.5):
        """
        计算网络布局
        
        Args:
            algorithm: 布局算法 ('spring', 'kamada_kawai', 'circular')
            iterations: 迭代次数
            k: spring layout的参数
        """
        logger.info(f"计算{algorithm}布局: {len(self.graph.nodes)}个节点, {len(self.graph.edges)}条边")
        
        if algorithm == "spring":
            self.layout = nx.spring_layout(
                self.graph, 
                k=k, 
                iterations=iterations,
                seed=42
            )
        elif algorithm == "kamada_kawai":
            self.layout = nx.kamada_kawai_layout(self.graph)
        elif algorithm == "circular":
            self.layout = nx.circular_layout(self.graph)
        else:
            logger.warning(f"未知布局算法: {algorithm}, 使用spring")
            self.layout = nx.spring_layout(self.graph, k=k, iterations=iterations, seed=42)
        
        logger.info("布局计算完成")
    
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
    
    def to_json(self, include_layout: bool = True) -> Dict:
        """
        将网络转换为JSON格式
        
        Args:
            include_layout: 是否包含布局坐标
        
        Returns:
            JSON字典
        """
        nodes_data = []
        for node_id, node in self.nodes.items():
            node_dict = asdict(node)
            if include_layout and node_id in self.layout:
                x, y = self.layout[node_id]
                node_dict["x"] = float(x)
                node_dict["y"] = float(y)
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
                
                # 计算节点大小（基于引用数）
                citations = paper['citation_count']
                size = 10 + min(50, citations / 10)  # 10-60 range
                
                # 根据年份分配颜色
                year = paper['year']
                color = self._get_year_color(year)
                
                node = Node(
                    id=paper_id,
                    label=paper['title'][:50],  # 截断标题
                    node_type='paper',
                    size=size,
                    color=color,
                    metadata={
                        'title': paper['title'],
                        'year': year,
                        'citation_count': citations,
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
                    label=f"引用{int(weight)}次",
                    metadata={'citation_type': 'direct'}
                )
                self.add_edge(edge)
        
        logger.info(f"引用网络构建完成: {len(self.nodes)}个节点, {len(self.edges)}条边")
    
    @staticmethod
    def _get_year_color(year: int) -> str:
        """根据年份返回颜色"""
        year_colors = {
            2020: "#FF6B6B",  # 红色
            2021: "#FFA500",  # 橙色
            2022: "#FFD93D",  # 黄色
            2023: "#6BCF7F",  # 绿色
            2024: "#4D96FF",  # 蓝色
        }
        return year_colors.get(year, "#9B59B6")  # 默认紫色
    
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
                
                # 计算节点大小（基于论文数）
                paper_count = len(stats['papers'])
                size = 10 + min(40, paper_count * 2)
                
                node = Node(
                    id=author_id,
                    label=stats['name'][:30],
                    node_type='author',
                    size=size,
                    color="#4ECDC4",
                    metadata={
                        'name': stats['name'],
                        'papers': list(stats['papers']),
                        'paper_count': paper_count,
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
                    label=f"{collab_data['count']}篇论文",
                    metadata={
                        'collaboration_count': collab_data['count'],
                        'papers': collab_data['papers']
                    }
                )
                self.add_edge(edge)
        
        logger.info(f"协作网络构建完成: {len(self.nodes)}个节点, {len(self.edges)}条边")
    
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

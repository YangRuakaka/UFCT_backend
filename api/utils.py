"""
工具函数和助手模块
"""
import logging
from typing import Dict, List, Optional
import hashlib
import json

logger = logging.getLogger(__name__)


def normalize_paper_id(paper_id) -> str:
    """规范化论文ID"""
    return str(paper_id).strip()


def normalize_author_id(author_id) -> str:
    """规范化作者ID"""
    return str(author_id).strip()


def truncate_text(text: str, max_length: int = 50) -> str:
    """截断文本"""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """生成缓存键"""
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    
    full_key = ":".join(key_parts)
    # 如果太长就使用哈希
    if len(full_key) > 200:
        key_hash = hashlib.md5(full_key.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    return full_key


def safe_json_serialize(obj) -> str:
    """安全的JSON序列化"""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except Exception as e:
        logger.error(f"JSON序列化失败: {e}")
        return "{}"


# ==================== 学科和大学配置 ====================
DISCIPLINE_KEYWORDS = {
    'cs': ['computer science', 'computing', 'algorithms', 'programming', 'software', 'system'],
    'ai': ['artificial intelligence', 'machine learning', 'deep learning', 'neural networks', 'AI', 'learning'],
    'se': ['software engineering', 'software development', 'testing', 'architecture', 'development'],
    'cv': ['computer vision', 'image processing', 'object detection', 'segmentation', 'vision', 'image'],
    'nlp': ['natural language processing', 'NLP', 'text mining', 'machine translation', 'language', 'text'],
    'db': ['database', 'data management', 'data storage', 'query optimization', 'data'],
    'network': ['computer network', 'network', 'communication', 'distributed', 'protocol'],
    'security': ['network security', 'cybersecurity', 'security', 'encryption', 'privacy', 'attack'],
}


def filter_papers_by_discipline(papers: List[Dict], discipline: str) -> List[Dict]:
    """
    按学科关键词过滤论文
    
    Args:
        papers: 论文列表
        discipline: 学科 ID
    
    Returns:
        过滤后的论文列表
    """
    keywords = DISCIPLINE_KEYWORDS.get(discipline, [])
    if not keywords:
        return papers
    
    filtered = []
    for paper in papers:
        if not paper:
            continue
        
        title = (paper.get('title') or '').lower()
        abstract = (paper.get('abstract') or '').lower()
        
        # 检查关键词匹配
        if any(keyword.lower() in title or keyword.lower() in abstract for keyword in keywords):
            filtered.append(paper)
    
    logger.info(f"按学科 {discipline} 过滤: {len(papers)} -> {len(filtered)} 篇论文")
    return filtered


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


def get_all_universities() -> List[Dict]:
    """获取所有大学列表"""
    return [
        {
            "id": "tongji",
            "name": "同济大学",
            "country": "China",
            "ror_id": "https://ror.org/01nrxwf90"
        },
        {
            "id": "tsinghua",
            "name": "清华大学",
            "country": "China",
            "ror_id": "https://ror.org/05rrcem69"
        },
        {
            "id": "fudan",
            "name": "复旦大学",
            "country": "China",
            "ror_id": "https://ror.org/0gw74x445"
        },
    ]


def get_all_disciplines() -> List[Dict]:
    """获取所有学科列表"""
    return [
        {
            "id": "cs",
            "name": "计算机科学",
            "keywords": DISCIPLINE_KEYWORDS['cs']
        },
        {
            "id": "ai",
            "name": "人工智能",
            "keywords": DISCIPLINE_KEYWORDS['ai']
        },
        {
            "id": "se",
            "name": "软件工程",
            "keywords": DISCIPLINE_KEYWORDS['se']
        },
        {
            "id": "cv",
            "name": "计算机视觉",
            "keywords": DISCIPLINE_KEYWORDS['cv']
        },
        {
            "id": "nlp",
            "name": "自然语言处理",
            "keywords": DISCIPLINE_KEYWORDS['nlp']
        },
        {
            "id": "db",
            "name": "数据库",
            "keywords": DISCIPLINE_KEYWORDS['db']
        },
        {
            "id": "network",
            "name": "计算机网络",
            "keywords": DISCIPLINE_KEYWORDS['network']
        },
        {
            "id": "security",
            "name": "网络安全",
            "keywords": DISCIPLINE_KEYWORDS['security']
        },
    ]

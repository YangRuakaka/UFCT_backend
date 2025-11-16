"""
共享的工具函数 - 包括学科和大学配置
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

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

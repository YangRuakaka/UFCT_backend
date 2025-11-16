"""
名称到ID的解析工具 - 将大学名称和学科名称转换为OpenAlex ID
独立模块避免模块缓存问题
"""
import logging
import requests
from typing import Optional, Dict, List
from urllib.parse import quote

logger = logging.getLogger(__name__)

# OpenAlex API基础配置
OPENALEX_BASE_URL = "https://api.openalex.org"
OPENALEX_EMAIL = "yangyyk@tongji.edu.cn"  # 用于polite pool


def _make_openalex_request(endpoint: str, params: Dict = None) -> Dict:
    """
    直接向OpenAlex API发起请求，避免依赖可能有缓存问题的单例
    
    Args:
        endpoint: API端点（如 '/institutions', '/topics'）
        params: 查询参数
    
    Returns:
        API响应JSON
    """
    if params is None:
        params = {}
    
    # 添加邮箱以加入polite pool
    params['mailto'] = OPENALEX_EMAIL
    
    url = f"{OPENALEX_BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenAlex API 请求失败: {endpoint}, 错误: {e}")
        return {}


def resolve_institution_name_to_id(institution_name_or_id: Optional[str]) -> Optional[str]:
    """
    将机构名称转换为OpenAlex ID，如果已是ID则直接返回
    
    Args:
        institution_name_or_id: 机构名称或ID
    
    Returns:
        OpenAlex ID (如 "I136199984") 或 None
    """
    if not institution_name_or_id:
        return None
    
    # 如果已是ID格式（以I开头或包含openalex.org）则直接返回
    if isinstance(institution_name_or_id, str):
        if institution_name_or_id.startswith('I') or 'openalex.org' in institution_name_or_id:
            logger.info(f"机构已是ID或URI格式: {institution_name_or_id}")
            # 如果是完整URI，提取ID部分
            if 'openalex.org' in institution_name_or_id:
                return institution_name_or_id.split('/')[-1]
            return institution_name_or_id
    
    # 否则搜索并返回第一个结果的ID
    try:
        logger.info(f"搜索机构: {institution_name_or_id}")
        
        response = _make_openalex_request('/institutions', params={
            'search': institution_name_or_id,
            'per_page': 1
        })
        
        results = response.get('results', [])
        if results:
            inst_id = results[0].get('id')
            if inst_id:
                # 提取ID部分 (e.g., https://openalex.org/I136199984 -> I136199984)
                extracted_id = inst_id.split('/')[-1] if '/' in inst_id else inst_id
                logger.info(f"✓ 找到机构: {results[0].get('display_name')} -> {extracted_id}")
                return extracted_id
        else:
            logger.warning(f"✗ 未找到机构: {institution_name_or_id}")
    except Exception as e:
        logger.error(f"解析机构名称失败: {institution_name_or_id}, 错误: {e}")
    
    return None


def resolve_discipline_name_to_id(discipline_name_or_id: Optional[str]) -> Optional[str]:
    """
    将学科名称转换为OpenAlex ID，如果已是ID则直接返回
    
    Args:
        discipline_name_or_id: 学科名称或ID
    
    Returns:
        OpenAlex ID (如 "T10001") 或 None
    """
    if not discipline_name_or_id:
        return None
    
    # 如果已是ID格式（以T开头或包含openalex.org）则直接返回
    if isinstance(discipline_name_or_id, str):
        if discipline_name_or_id.startswith('T') or 'openalex.org' in discipline_name_or_id:
            logger.info(f"学科已是ID或URI格式: {discipline_name_or_id}")
            # 如果是完整URI，提取ID部分
            if 'openalex.org' in discipline_name_or_id:
                return discipline_name_or_id.split('/')[-1]
            return discipline_name_or_id
    
    # 否则搜索并返回第一个结果的ID
    try:
        logger.info(f"搜索学科: {discipline_name_or_id}")
        
        response = _make_openalex_request('/topics', params={
            'search': discipline_name_or_id,
            'per_page': 1
        })
        
        results = response.get('results', [])
        if results:
            topic_id = results[0].get('id')
            if topic_id:
                # 提取ID部分 (e.g., https://openalex.org/T12345 -> T12345)
                extracted_id = topic_id.split('/')[-1] if '/' in topic_id else topic_id
                logger.info(f"✓ 找到学科: {results[0].get('display_name')} -> {extracted_id}")
                return extracted_id
        else:
            logger.warning(f"✗ 未找到学科: {discipline_name_or_id}")
    except Exception as e:
        logger.error(f"解析学科名称失败: {discipline_name_or_id}, 错误: {e}")
    
    return None


def search_institutions(query: str, limit: int = 10) -> List[Dict]:
    """
    搜索机构
    
    Args:
        query: 搜索关键词
        limit: 返回结果数量
    
    Returns:
        机构列表
    """
    try:
        logger.info(f"搜索机构: {query}, limit={limit}")
        
        response = _make_openalex_request('/institutions', params={
            'search': query,
            'per_page': min(limit, 50)
        })
        
        results = response.get('results', [])
        
        formatted_results = []
        for inst in results[:limit]:
            formatted_results.append({
                'id': inst.get('id', '').split('/')[-1] if '/' in inst.get('id', '') else inst.get('id'),
                'display_name': inst.get('display_name'),
                'country_code': inst.get('country_code'),
                'type': inst.get('type'),
                'works_count': inst.get('works_count'),
                'cited_by_count': inst.get('cited_by_count'),
            })
        
        logger.info(f"✓ 搜索成功: 找到 {len(formatted_results)} 个机构")
        return formatted_results
    except Exception as e:
        logger.error(f"搜索机构失败: {e}")
        return []


def search_disciplines(query: str, limit: int = 10) -> List[Dict]:
    """
    搜索学科
    
    Args:
        query: 搜索关键词
        limit: 返回结果数量
    
    Returns:
        学科列表
    """
    try:
        logger.info(f"搜索学科: {query}, limit={limit}")
        
        response = _make_openalex_request('/topics', params={
            'search': query,
            'per_page': min(limit, 50)
        })
        
        results = response.get('results', [])
        
        formatted_results = []
        for topic in results[:limit]:
            formatted_results.append({
                'id': topic.get('id', '').split('/')[-1] if '/' in topic.get('id', '') else topic.get('id'),
                'display_name': topic.get('display_name'),
                'description': topic.get('description'),
                'keywords': topic.get('keywords', []),
                'works_count': topic.get('works_count'),
                'cited_by_count': topic.get('cited_by_count'),
            })
        
        logger.info(f"✓ 搜索成功: 找到 {len(formatted_results)} 个学科")
        return formatted_results
    except Exception as e:
        logger.error(f"搜索学科失败: {e}")
        return []

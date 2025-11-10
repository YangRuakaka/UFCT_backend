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

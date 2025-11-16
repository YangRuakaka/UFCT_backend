"""API工具模块"""

# 从当前目录的模块导入
from .name_resolver import (
    resolve_institution_name_to_id,
    resolve_discipline_name_to_id,
    search_institutions,
    search_disciplines
)
from .param_validator import OpenAlexParamValidator
from .common import (
    get_all_universities,
    get_all_disciplines,
    filter_papers_by_discipline,
    DISCIPLINE_KEYWORDS
)

__all__ = [
    # 名称解析函数
    'resolve_institution_name_to_id',
    'resolve_discipline_name_to_id',
    'search_institutions',
    'search_disciplines',
    # 参数验证
    'OpenAlexParamValidator',
    # 通用工具
    'get_all_universities',
    'get_all_disciplines',
    'filter_papers_by_discipline',
    'DISCIPLINE_KEYWORDS'
]

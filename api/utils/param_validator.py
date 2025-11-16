"""
OpenAlex 参数验证和转换工具
用于验证和转换学科 ID、机构 ID 等参数为有效的 OpenAlex API 格式
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OpenAlexParamValidator:
    """OpenAlex 参数验证器"""
    
    # 常见学科 ID 映射（用户输入 -> OpenAlex 格式）
    DISCIPLINE_ALIASES = {
        # 用户输入 -> OpenAlex 有效 ID
        'cs': 'computer_science',
        'computer_science': 'computer_science',
        'biology': 'biology',
        'physics': 'physics',
        'chemistry': 'chemistry',
        'math': 'mathematics',
        'mathematics': 'mathematics',
        'medicine': 'medicine',
        'psychology': 'psychology',
        'economics': 'economics',
        'history': 'history',
        'philosophy': 'philosophy',
        'engineering': 'engineering',
        'ml': 'machine_learning',
        'machine_learning': 'machine_learning',
        'ai': 'artificial_intelligence',
        'artificial_intelligence': 'artificial_intelligence',
    }
    
    # 常见机构 ID 映射
    INSTITUTION_ALIASES = {
        # 用户输入 -> OpenAlex 机构 ID
        'tongji': 'I4210147421',  # 同济大学
        'tongji_university': 'I4210147421',
        'harvard': 'I4210145129',
        'harvard_university': 'I4210145129',
        'mit': 'I4210157984',
        'stanford': 'I4210159054',
        'stanford_university': 'I4210159054',
        'berkeley': 'I4210145729',
        'oxford': 'I4210132671',
        'cambridge': 'I4210132509',
        'tsinghua': 'I4210166340',  # 清华大学
        'peking': 'I4210159234',  # 北京大学
        'fudan': 'I4210163215',  # 复旦大学
    }
    
    @staticmethod
    def validate_and_convert_discipline(discipline: Optional[str]) -> Optional[str]:
        """
        验证并转换学科参数
        
        Args:
            discipline: 用户输入的学科 ID（可以是别名或完整 ID）
        
        Returns:
            有效的 OpenAlex 学科 ID，或 None 如果无效
        
        Raises:
            ValueError: 如果学科 ID 无法识别
        """
        if not discipline:
            return None
        
        # 转小写进行匹配
        discipline_lower = discipline.lower().strip()
        
        # 检查是否在别名映射中
        if discipline_lower in OpenAlexParamValidator.DISCIPLINE_ALIASES:
            valid_id = OpenAlexParamValidator.DISCIPLINE_ALIASES[discipline_lower]
            logger.debug(f"学科参数转换: {discipline} -> {valid_id}")
            return valid_id
        
        # 如果不在映射中，假设用户输入的是正确的 ID，发出警告
        logger.warning(
            f"学科 ID '{discipline}' 不在已知列表中，"
            f"将直接使用该 ID。如果 API 返回 400 错误，请检查拼写。"
        )
        return discipline
    
    @staticmethod
    def validate_and_convert_institution(institution: Optional[str]) -> Optional[str]:
        """
        验证并转换机构参数
        
        Args:
            institution: 用户输入的机构 ID（可以是别名或完整 ID）
        
        Returns:
            有效的 OpenAlex 机构 ID，或 None 如果无效
        
        Raises:
            ValueError: 如果机构 ID 无法识别或格式不正确
        """
        if not institution:
            return None
        
        institution_lower = institution.lower().strip()
        
        # 检查是否在别名映射中
        if institution_lower in OpenAlexParamValidator.INSTITUTION_ALIASES:
            valid_id = OpenAlexParamValidator.INSTITUTION_ALIASES[institution_lower]
            logger.debug(f"机构参数转换: {institution} -> {valid_id}")
            return valid_id
        
        # 如果以 I 开头，假设已经是有效的 OpenAlex ID
        if institution.upper().startswith('I') and institution[1:].isdigit():
            logger.debug(f"机构参数验证通过: {institution}")
            return institution
        
        # 否则发出警告
        logger.warning(
            f"机构 ID '{institution}' 格式可能不正确。"
            f"有效格式应该是 'I' 开头的数字 ID（如 I4210147421）"
            f"或已知别名（如 tongji, harvard 等）。"
        )
        
        return institution
    
    @staticmethod
    def get_available_disciplines():
        """获取已知的学科别名列表"""
        return list(OpenAlexParamValidator.DISCIPLINE_ALIASES.keys())
    
    @staticmethod
    def get_available_institutions():
        """获取已知的机构别名列表"""
        return list(OpenAlexParamValidator.INSTITUTION_ALIASES.keys())


if __name__ == '__main__':
    # 测试参数验证
    print("=" * 70)
    print("OpenAlex 参数验证测试")
    print("=" * 70)
    
    # 测试学科参数
    print("\n学科参数验证：")
    test_disciplines = ['cs', 'computer_science', 'biology', 'unknown_field']
    for disc in test_disciplines:
        result = OpenAlexParamValidator.validate_and_convert_discipline(disc)
        print(f"  {disc:20} -> {result}")
    
    # 测试机构参数
    print("\n机构参数验证：")
    test_institutions = ['tongji', 'harvard', 'I4210147421', 'unknown_org']
    for inst in test_institutions:
        result = OpenAlexParamValidator.validate_and_convert_institution(inst)
        print(f"  {inst:20} -> {result}")
    
    # 显示可用的别名
    print("\n可用的学科别名：")
    print(f"  {', '.join(OpenAlexParamValidator.get_available_disciplines())}")
    
    print("\n可用的机构别名：")
    print(f"  {', '.join(OpenAlexParamValidator.get_available_institutions())}")

"""
OpenAlex 参数验证和转换工具
用于验证和转换学科 ID、机构 ID 等参数为有效的 OpenAlex API 格式
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OpenAlexParamValidator:
    """OpenAlex 参数验证器"""
    
    # 学科 ID 映射（OpenAlex 的完整 topic ID）
    # 从 https://api.openalex.org/topics 获取
    # 注意：这些是 OpenAlex 中的实际主题ID，需要定期验证
    DISCIPLINE_ALIASES = {
        # 用户输入 -> OpenAlex Topic ID
        
        # ========== 计算机科学核心领域 ==========
        # Computer Science (计算机科学)
        'cs': 'T13674',
        'computer_science': 'T13674',
        'computer science': 'T13674',
        'computerscience': 'T13674',
        'engineering': 'T13674',  # Computer Science and Engineering
        
        # Machine Learning (机器学习)
        'ml': 'T10470',
        'machine_learning': 'T10470',
        'machine learning': 'T10470',
        'machinelearning': 'T10470',
        
        # Deep Learning (深度学习)
        'deep_learning': 'T12600',
        'deep learning': 'T12600',
        'deeplearning': 'T12600',
        'dl': 'T12600',
        
        # Artificial Intelligence (人工智能)
        'ai': 'T11202',
        'artificial_intelligence': 'T11202',
        'artificial intelligence': 'T11202',
        'artificialintelligence': 'T11202',
        
        # Natural Language Processing (自然语言处理)
        'nlp': 'T10531',
        'natural_language_processing': 'T10531',
        'natural language processing': 'T10531',
        'naturallanguageprocessing': 'T10531',
        
        # Computer Vision (计算机视觉)
        'cv': 'T10030',
        'computer_vision': 'T10030',
        'computer vision': 'T10030',
        'computervision': 'T10030',
        'vision': 'T10030',
        
        # Data Science (数据科学)
        'data_science': 'T10281',
        'data science': 'T10281',
        'datascience': 'T10281',
        
        # ========== CS相关的系统与工程领域 ==========
        # Software Engineering (软件工程)
        'software_engineering': 'T11034',
        'software engineering': 'T11034',
        'softwareengineering': 'T11034',
        'se': 'T11034',
        
        # Cybersecurity (网络安全)
        'cybersecurity': 'T10349',
        'cyber_security': 'T10349',
        'cyber security': 'T10349',
        'security': 'T10349',
        'information security': 'T10349',
        
        # Distributed Systems (分布式系统)
        'distributed_systems': 'T10667',
        'distributed systems': 'T10667',
        'distributedsystems': 'T10667',
        
        # Database Systems (数据库系统)
        'database_systems': 'T10598',
        'database systems': 'T10598',
        'databases': 'T10598',
        'database': 'T10598',
        
        # Human-Computer Interaction (人机交互)
        'hci': 'T10449',
        'human_computer_interaction': 'T10449',
        'human computer interaction': 'T10449',
        'human-computer interaction': 'T10449',
        
        # Algorithms (算法)
        'algorithms': 'T10047',
        'algorithm': 'T10047',
        
        # ========== 其他领域 ==========
        'biology': 'T12000',
        'physics': 'T12018',
        'chemistry': 'T12029',
        'math': 'T11205',
        'mathematics': 'T11205',
        'medicine': 'T12144',
        'psychology': 'T12332',
        'economics': 'T11452',
        'history': 'T11550',
        'philosophy': 'T11722',
    }
    
    # 机构 ID 映射
    INSTITUTION_ALIASES = {
        # 用户输入 -> OpenAlex 机构 ID (从 institutions 端点查询)
        # 注意：这些ID可能会变化，建议定期验证
        
        # 中国大学
        'tongji': 'I116953780',
        'tongji_university': 'I116953780',
        'tongji university': 'I116953780',
        'tsinghua': 'I4210166340',
        'tsinghua_university': 'I4210166340',
        'tsinghua university': 'I4210166340',
        'peking': 'I4210159234',
        'peking_university': 'I4210159234',
        'peking university': 'I4210159234',
        'fudan': 'I4210163215',
        'fudan_university': 'I4210163215',
        'fudan university': 'I4210163215',
        
        # 美国大学
        'harvard': 'I4210145129',
        'harvard_university': 'I4210145129',
        'harvard university': 'I4210145129',
        'mit': 'I4210157984',
        'mit university': 'I4210157984',
        'stanford': 'I4210159054',
        'stanford_university': 'I4210159054',
        'stanford university': 'I4210159054',
        'berkeley': 'I4210145729',
        'berkeley_university': 'I4210145729',
        'berkeley university': 'I4210145729',
        
        # 英国大学
        'oxford': 'I4210132671',
        'oxford_university': 'I4210132671',
        'oxford university': 'I4210132671',
        'cambridge': 'I4210132509',
        'cambridge_university': 'I4210132509',
        'cambridge university': 'I4210132509',
    }
    
    @staticmethod
    def validate_and_convert_discipline(discipline: Optional[str]) -> Optional[str]:
        """
        验证并转换学科参数为有效的 OpenAlex Topic ID
        
        Args:
            discipline: 用户输入的学科 ID（可以是别名或完整 ID）
                       支持格式：
                       - 别名：'cs', 'machine learning', 'Computer Science' 等
                       - Topic ID：'T13674' 或 'https://openalex.org/T13674'
        
        Returns:
            有效的 OpenAlex Topic ID（格式：T开头的数字，如 T11900）
        """
        if not discipline:
            return None
        
        # 规范化：转换为小写，移除前后空格
        discipline_normalized = discipline.lower().strip()
        
        # 检查是否在别名映射中
        if discipline_normalized in OpenAlexParamValidator.DISCIPLINE_ALIASES:
            valid_id = OpenAlexParamValidator.DISCIPLINE_ALIASES[discipline_normalized]
            logger.debug(f"学科参数转换: '{discipline}' -> {valid_id}")
            return valid_id
        
        # 如果以 T 开头且后跟数字，假设已经是有效的 Topic ID
        if discipline.startswith('T') and discipline[1:].isdigit():
            logger.debug(f"学科参数验证通过: {discipline}")
            return discipline
        
        # 如果是完整的 URI 格式
        if discipline.startswith('https://openalex.org/T'):
            topic_id = discipline.split('/')[-1]
            logger.debug(f"学科参数从 URI 提取: {discipline} -> {topic_id}")
            return topic_id
        
        logger.warning(
            f"学科 ID '{discipline}' 不被识别。"
            f"支持的别名: {', '.join(list(OpenAlexParamValidator.DISCIPLINE_ALIASES.keys())[:10])}..."
        )
        return None
    
    @staticmethod
    def validate_and_convert_disciplines(disciplines: Optional[str]) -> list:
        """
        验证并转换多个学科参数为有效的 OpenAlex Topic ID 列表
        
        支持逗号分隔的多个学科（用于 OR 查询）
        
        Args:
            disciplines: 逗号分隔的学科列表（例："Computer Science,Machine Learning"）
                        可以混合别名和 Topic ID
        
        Returns:
            有效 Topic ID 列表（去重）
        """
        if not disciplines:
            return []
        
        # 分割逗号分隔的学科列表
        discipline_list = [d.strip() for d in disciplines.split(',')]
        
        valid_ids = []
        seen = set()
        
        for discipline in discipline_list:
            valid_id = OpenAlexParamValidator.validate_and_convert_discipline(discipline)
            if valid_id and valid_id not in seen:
                valid_ids.append(valid_id)
                seen.add(valid_id)
        
        if valid_ids:
            logger.debug(f"多学科参数转换成功: {len(valid_ids)} 个有效 Topic ID")
        else:
            logger.warning(f"未能转换任何学科参数：{disciplines}")
        
        return valid_ids
    
    @staticmethod
    def validate_and_convert_institution(institution: Optional[str]) -> Optional[str]:
        """
        验证并转换机构参数为有效的 OpenAlex Institution ID
        
        Args:
            institution: 用户输入的机构 ID（可以是别名或完整 ID）
                        支持格式：
                        - 别名：'tongji', 'Tongji University', 'harvard' 等
                        - Institution ID：'I116953780' 或 'https://openalex.org/I116953780'
                        - ROR ID：'https://ror.org/0...'
        
        Returns:
            有效的 OpenAlex Institution ID（格式：I开头的数字）
        """
        if not institution:
            return None
        
        # 规范化：转换为小写，移除前后空格
        institution_normalized = institution.lower().strip()
        
        # 检查是否在别名映射中
        if institution_normalized in OpenAlexParamValidator.INSTITUTION_ALIASES:
            valid_id = OpenAlexParamValidator.INSTITUTION_ALIASES[institution_normalized]
            logger.debug(f"机构参数转换: '{institution}' -> {valid_id}")
            return valid_id
        
        # 如果以 I 开头且后跟数字，假设已经是有效的 Institution ID
        if institution.startswith('I') and institution[1:].isdigit():
            logger.debug(f"机构参数验证通过: {institution}")
            return institution
        
        # 如果是完整的 URI 格式
        if institution.startswith('https://openalex.org/I'):
            inst_id = institution.split('/')[-1]
            logger.debug(f"机构参数从 URI 提取: {institution} -> {inst_id}")
            return inst_id
        
        # ROR 格式的机构 ID
        if institution.startswith('https://ror.org/'):
            logger.debug(f"机构参数为 ROR ID: {institution}")
            return institution
        
        logger.warning(
            f"机构 ID '{institution}' 格式不正确。"
            f"应为别名（如 tongji）或 I 开头的 ID（如 I116953780）"
        )
        return None
    
    @staticmethod
    def get_available_disciplines():
        """获取已知的学科别名列表"""
        return list(OpenAlexParamValidator.DISCIPLINE_ALIASES.keys())
    
    @staticmethod
    def get_available_cs_topics():
        """
        获取所有支持的计算机科学相关topics
        
        Returns:
            dict: 按分类组织的CS topics，格式为:
            {
                '计算机科学核心领域': {
                    'machine_learning': 'T10470',
                    'deep_learning': 'T12600',
                    ...
                },
                'CS相关的系统与工程领域': {
                    'software_engineering': 'T11034',
                    ...
                }
            }
        """
        cs_topics = {}
        
        # 提取CS相关的topics（按注释分组）
        core_topics = {}
        system_topics = {}
        
        for alias, topic_id in OpenAlexParamValidator.DISCIPLINE_ALIASES.items():
            # 映射到OpenAlex ID
            topic_display = {
                'T13674': 'Computer Science',
                'T10470': 'Machine Learning',
                'T12600': 'Deep Learning',
                'T11202': 'Artificial Intelligence',
                'T10531': 'Natural Language Processing',
                'T10030': 'Computer Vision',
                'T10281': 'Data Science',
                'T11034': 'Software Engineering',
                'T10349': 'Cybersecurity',
                'T10667': 'Distributed Systems',
                'T10598': 'Database Systems',
                'T10449': 'Human-Computer Interaction',
                'T10047': 'Algorithms',
            }
            
            if topic_id in topic_display:
                # 去重：只保留最常用的别名
                if topic_display[topic_id] not in core_topics and topic_display[topic_id] not in system_topics:
                    if topic_id in ['T13674', 'T10470', 'T12600', 'T11202', 'T10531', 'T10030', 'T10281']:
                        core_topics[alias] = topic_id
                    else:
                        system_topics[alias] = topic_id
        
        return {
            '计算机科学核心领域': core_topics,
            'CS相关的系统与工程领域': system_topics
        }
    
    @staticmethod
    def get_available_institutions():
        """获取已知的机构别名列表"""
        return list(OpenAlexParamValidator.INSTITUTION_ALIASES.keys())

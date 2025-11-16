"""
作者模型 - 定义作者数据结构
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from models.base import BaseModel


@dataclass
class Author(BaseModel):
    """作者模型"""
    
    id: str                              # OpenAlex ID
    display_name: str
    works_count: int = 0
    cited_by_count: int = 0
    h_index: Optional[int] = None
    last_known_institution: Optional[Dict] = None
    affiliations: List[Dict] = field(default_factory=list)
    topics: List[Dict] = field(default_factory=list)
    works: List[str] = field(default_factory=list)        # 论文ID列表
    collaborators: List[str] = field(default_factory=list)  # 协作者ID列表
    orcid: Optional[str] = None
    url: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__()
    
    @property
    def is_prolific(self) -> bool:
        """判断是否为多产作者（>50篇论文）"""
        return self.works_count > 50
    
    @property
    def is_highly_cited(self) -> bool:
        """判断是否为高被引作者（>1000次）"""
        return self.cited_by_count > 1000
    
    @property
    def average_citations(self) -> float:
        """计算平均引用数"""
        if self.works_count == 0:
            return 0.0
        return self.cited_by_count / self.works_count
    
    @property
    def current_institution(self) -> Optional[str]:
        """获取当前所在机构"""
        if self.last_known_institution:
            return self.last_known_institution.get('display_name')
        return None
    
    @property
    def specialties(self) -> List[str]:
        """获取专业领域列表"""
        return [t.get('display_name') for t in self.topics if t.get('display_name')]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'display_name': self.display_name,
            'works_count': self.works_count,
            'cited_by_count': self.cited_by_count,
            'h_index': self.h_index,
            'last_known_institution': self.last_known_institution,
            'affiliations': self.affiliations,
            'topics': self.topics,
            'works': self.works,
            'collaborators': self.collaborators,
            'orcid': self.orcid,
            'url': self.url,
            'metadata': self.metadata,
        }

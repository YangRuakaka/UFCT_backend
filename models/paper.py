"""
论文模型 - 定义论文数据结构
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from models.base import BaseModel


@dataclass
class Paper(BaseModel):
    """论文模型"""
    
    id: str                          # OpenAlex ID 或 DOI
    title: str
    year: int
    cited_by_count: int = 0
    publication_date: Optional[str] = None
    doi: Optional[str] = None
    authors: List[Dict] = field(default_factory=list)
    concepts: List[Dict] = field(default_factory=list)
    cited_by: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    source: Optional[str] = None     # 出版物来源
    url: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__()
    
    @property
    def is_highly_cited(self) -> bool:
        """判断是否为高被引论文（>10次）"""
        return self.cited_by_count > 10
    
    @property
    def disciplines(self) -> List[str]:
        """获取学科列表"""
        return [c.get('display_name') for c in self.concepts if c.get('display_name')]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'cited_by_count': self.cited_by_count,
            'publication_date': self.publication_date,
            'doi': self.doi,
            'authors': self.authors,
            'concepts': self.concepts,
            'cited_by': self.cited_by,
            'references': self.references,
            'source': self.source,
            'url': self.url,
            'metadata': self.metadata,
        }

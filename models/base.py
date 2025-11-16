"""
模型基类 - 所有数据模型的父类
"""
from datetime import datetime
from typing import Dict, Any


class BaseModel:
    """基础模型类"""
    
    def __init__(self):
        """初始化基础模型"""
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_')
        }
    
    def to_json(self) -> Dict[str, Any]:
        """转换为 JSON 序列化的字典"""
        data = self.to_dict()
        # 处理 datetime 对象
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_dict()})"

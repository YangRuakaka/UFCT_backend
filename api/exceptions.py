"""
异常定义 - 统一的异常处理
"""


class BaseAPIException(Exception):
    """基础 API 异常"""
    
    def __init__(self, message: str, status_code: int = 500):
        """
        初始化异常
        
        Args:
            message: 异常消息
            status_code: HTTP 状态码
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "status": "error",
            "message": self.message
        }


class DataNotFoundException(BaseAPIException):
    """数据未找到异常"""
    
    def __init__(self, message: str = "数据未找到"):
        super().__init__(message, status_code=404)


class ValidationException(BaseAPIException):
    """验证异常"""
    
    def __init__(self, message: str = "参数验证失败"):
        super().__init__(message, status_code=400)


class BadRequestException(BaseAPIException):
    """请求错误异常"""
    
    def __init__(self, message: str = "请求错误"):
        super().__init__(message, status_code=400)


class InternalServerException(BaseAPIException):
    """服务器内部错误异常"""
    
    def __init__(self, message: str = "服务器内部错误"):
        super().__init__(message, status_code=500)


class DataFetchException(BaseAPIException):
    """数据获取异常"""
    
    def __init__(self, message: str = "数据获取失败"):
        super().__init__(message, status_code=503)


class CacheException(BaseAPIException):
    """缓存异常"""
    
    def __init__(self, message: str = "缓存操作失败"):
        super().__init__(message, status_code=500)


class NetworkAnalysisException(BaseAPIException):
    """网络分析异常"""
    
    def __init__(self, message: str = "网络分析失败"):
        super().__init__(message, status_code=500)

"""
配置文件 - 管理环境变量和系统配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基础配置"""
    # Flask配置
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # Hugging Face 数据集配置
    HF_DATASET_LOCAL_DIR = os.getenv("HF_DATASET_LOCAL_DIR", "./data/sciscinet-v2")
    
    # 数据处理配置
    DEFAULT_YEAR_MIN = 2020
    DEFAULT_YEAR_MAX = 2024
    DEFAULT_LIMIT = 500  # 单次查询最大节点数
    MAX_NODES = 5000     # 支持最大节点数
    MIN_DEGREE = 2       # 最小节点度数（用于过滤孤立节点）
    
    # 缓存配置
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    CACHE_TIMEOUT = 86400  # 24小时缓存
    
    # 网络分析配置
    FORCE_DIRECTED_ITERATIONS = 50  # 力引导布局迭代次数
    FORCE_DIRECTED_K = 0.5           # 弹簧常数
    MIN_EDGE_WEIGHT = 0.1            # 最小边权重阈值
    
    # API配置
    MAX_REQUEST_TIMEOUT = 30
    BATCH_SIZE = 1000  # 批查询大小
    
    # 向后兼容（废弃的 BigQuery 配置）
    BIGQUERY_PROJECT = os.getenv("BIGQUERY_PROJECT", "")
    BIGQUERY_DATASET_V2 = ""
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    CACHE_TIMEOUT = 300  # 5分钟缓存


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    CACHE_TIMEOUT = 0


# 获取配置
def get_config(env=None):
    """根据环境变量返回对应配置"""
    if env is None:
        env = os.getenv("FLASK_ENV", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)

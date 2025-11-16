"""
API 蓝图模块
"""
from .health import health_bp
from .config import config_bp
from .networks import networks_bp
from .papers_authors import papers_authors_bp
from .statistics import statistics_bp

__all__ = ['health_bp', 'config_bp', 'networks_bp', 'papers_authors_bp', 'statistics_bp']

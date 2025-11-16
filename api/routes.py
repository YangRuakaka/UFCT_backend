import logging

from flask import Blueprint

from api.blueprints import health_bp, config_bp, networks_bp, papers_authors_bp, statistics_bp


logger = logging.getLogger(__name__)


def init_api_blueprint() -> Blueprint:
    """初始化API主蓝图，注册所有子蓝图"""
    api_bp = Blueprint('api', __name__)

    # 注册所有子蓝图
    api_bp.register_blueprint(health_bp)
    api_bp.register_blueprint(config_bp)
    api_bp.register_blueprint(networks_bp)
    api_bp.register_blueprint(papers_authors_bp)
    api_bp.register_blueprint(statistics_bp)

    logger.info("✓ API 初始化完成 - 所有蓝图已注册")
    logger.info("  ├─ health_bp (健康检查)")
    logger.info("  ├─ config_bp (配置信息)")
    logger.info("  ├─ networks_bp (网络相关)")
    logger.info("  ├─ papers_authors_bp (论文/作者详情)")
    logger.info("  └─ statistics_bp (统计数据)")

    return api_bp
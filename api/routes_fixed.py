"""
API路由 - 定义所有REST API端点
"""
import logging
from flask import Blueprint, request, jsonify, current_app
from typing import Tuple, Dict

from data import BigQueryFetcher
from data.data_fetcher import DataCache
from models import CitationNetwork, CollaborationNetwork
from config import Config

logger = logging.getLogger(__name__)

# 创建Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 全局对象
fetcher: BigQueryFetcher = None
cache: DataCache = None


def init_api(app):
    """初始化API（延迟加载，不在启动时连接 BigQuery）"""
    global cache
    
    cache = DataCache(use_redis=False)  # 改为True以启用Redis
    app.register_blueprint(api_bp)
    logger.info("✓ API 初始化完成")


def get_fetcher():
    """获取或创建 BigQueryFetcher 实例"""
    global fetcher
    if fetcher is None:
        try:
            logger.info("初始化 BigQuery Fetcher...")
            fetcher = BigQueryFetcher()
            logger.info("✓ BigQuery Fetcher 初始化成功")
        except Exception as e:
            logger.error(f"✗ BigQuery Fetcher 初始化失败: {e}")
            logger.warning("请设置 GOOGLE_APPLICATION_CREDENTIALS 环境变量指向 GCP 认证 JSON 文件")
            raise
    return fetcher


# ==================== 健康检查 ====================
@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "message": "UFCT Backend is running"
    }), 200


# ==================== 论文引用网络 ====================
@api_bp.route('/networks/citation', methods=['GET'])
def get_citation_network():
    """
    获取论文引用网络
    
    查询参数：
    - year_min: 起始年份 (默认2020)
    - year_max: 结束年份 (默认2024)
    - limit: 节点数限制 (默认500, 最大5000)
    - layout: 布局算法 (spring/kamada_kawai/circular)
    
    返回格式：
    {
        "status": "success",
        "data": {
            "network": {
                "nodes": [...],
                "edges": [...],
                "metadata": {...}
            },
            "statistics": {...}
        }
    }
    """
    try:
        # 获取查询参数
        year_min = request.args.get('year_min', Config.DEFAULT_YEAR_MIN, type=int)
        year_max = request.args.get('year_max', Config.DEFAULT_YEAR_MAX, type=int)
        limit = request.args.get('limit', Config.DEFAULT_LIMIT, type=int)
        layout_algo = request.args.get('layout', 'spring', type=str)
        
        # 参数验证
        limit = min(limit, Config.MAX_NODES)
        
        # 检查缓存
        cache_key = f"citation_network:{year_min}:{year_max}:{limit}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"缓存命中: {cache_key}")
            return jsonify({
                "status": "success",
                "data": cached_data,
                "cached": True
            }), 200
        
        logger.info(f"获取引用网络: {year_min}-{year_max}, limit={limit}")
        
        # 获取论文数据
        fetcher_instance = get_fetcher()
        papers_df = fetcher_instance.get_papers_by_year_range(year_min, year_max, limit)
        if papers_df.empty:
            return jsonify({
                "status": "error",
                "message": "没有找到符合条件的论文"
            }), 404
        
        # 获取引用关系
        paper_ids = papers_df['paperid'].tolist()
        references_df = fetcher_instance.get_paper_references(paper_ids, year_min, year_max)
        
        # 构建网络
        citation_net = CitationNetwork()
        citation_net.build_from_dataframes(papers_df, references_df)
        
        # 计算布局
        citation_net.compute_layout(algorithm=layout_algo, iterations=50, k=0.5)
        
        # 获取统计信息
        stats = citation_net.get_network_statistics()
        
        # 构建响应
        response_data = {
            "network": citation_net.to_json(include_layout=True),
            "statistics": stats,
            "query_params": {
                "year_min": year_min,
                "year_max": year_max,
                "limit": limit,
                "layout": layout_algo
            }
        }
        
        # 缓存结果
        cache.set(cache_key, response_data)
        
        return jsonify({
            "status": "success",
            "data": response_data,
            "cached": False
        }), 200
        
    except Exception as e:
        logger.error(f"获取引用网络失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==================== 作者协作网络 ====================
@api_bp.route('/networks/collaboration', methods=['GET'])
def get_collaboration_network():
    """
    获取作者协作网络
    
    查询参数：
    - year_min: 起始年份 (默认2020)
    - year_max: 结束年份 (默认2024)
    - limit: 节点数限制 (默认500, 最大5000)
    - min_collaborations: 最小协作次数 (默认1)
    - layout: 布局算法 (spring/kamada_kawai/circular)
    
    返回格式：
    {
        "status": "success",
        "data": {
            "network": {
                "nodes": [...],
                "edges": [...],
                "metadata": {...}
            },
            "statistics": {...},
            "communities": {...}
        }
    }
    """
    try:
        # 获取查询参数
        year_min = request.args.get('year_min', Config.DEFAULT_YEAR_MIN, type=int)
        year_max = request.args.get('year_max', Config.DEFAULT_YEAR_MAX, type=int)
        limit = request.args.get('limit', Config.DEFAULT_LIMIT, type=int)
        min_collab = request.args.get('min_collaborations', 1, type=int)
        layout_algo = request.args.get('layout', 'spring', type=str)
        
        # 参数验证
        limit = min(limit, Config.MAX_NODES)
        
        # 检查缓存
        cache_key = f"collaboration_network:{year_min}:{year_max}:{limit}:{min_collab}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"缓存命中: {cache_key}")
            return jsonify({
                "status": "success",
                "data": cached_data,
                "cached": True
            }), 200
        
        logger.info(f"获取协作网络: {year_min}-{year_max}, limit={limit}")
        
        # 获取论文数据
        fetcher_instance = get_fetcher()
        papers_df = fetcher_instance.get_papers_by_year_range(year_min, year_max, limit)
        if papers_df.empty:
            return jsonify({
                "status": "error",
                "message": "没有找到符合条件的论文"
            }), 404
        
        # 获取作者数据
        paper_ids = papers_df['paperid'].tolist()
        authors_df = fetcher_instance.get_authors_by_paperids(paper_ids)
        
        # 构建网络
        collab_net = CollaborationNetwork()
        collab_net.build_from_dataframes(authors_df, papers_df, min_collaborations=min_collab)
        
        # 计算布局
        collab_net.compute_layout(algorithm=layout_algo, iterations=50, k=0.5)
        
        # 获取统计信息
        stats = collab_net.get_network_statistics()
        
        # 检测社群
        communities = collab_net.detect_communities()
        
        # 构建响应
        response_data = {
            "network": collab_net.to_json(include_layout=True),
            "statistics": stats,
            "communities": communities,
            "query_params": {
                "year_min": year_min,
                "year_max": year_max,
                "limit": limit,
                "min_collaborations": min_collab,
                "layout": layout_algo
            }
        }
        
        # 缓存结果
        cache.set(cache_key, response_data)
        
        return jsonify({
            "status": "success",
            "data": response_data,
            "cached": False
        }), 200
        
    except Exception as e:
        logger.error(f"获取协作网络失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==================== 论文详情 ====================
@api_bp.route('/papers/<paper_id>', methods=['GET'])
def get_paper_details(paper_id: str):
    """
    获取论文详情
    
    参数：
    - paper_id: 论文ID
    
    返回格式：
    {
        "status": "success",
        "data": {
            "paper": {...},
            "citations": [...],
            "authors": [...]
        }
    }
    """
    try:
        cache_key = f"paper:{paper_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return jsonify({
                "status": "success",
                "data": cached_data,
                "cached": True
            }), 200
        
        # 这里可以实现具体的论文详情获取逻辑
        return jsonify({
            "status": "error",
            "message": "功能开发中"
        }), 501
        
    except Exception as e:
        logger.error(f"获取论文详情失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==================== 作者详情 ====================
@api_bp.route('/authors/<author_id>', methods=['GET'])
def get_author_details(author_id: str):
    """
    获取作者详情
    
    参数：
    - author_id: 作者ID
    
    返回格式：
    {
        "status": "success",
        "data": {
            "author": {...},
            "papers": [...],
            "collaborators": [...]
        }
    }
    """
    try:
        cache_key = f"author:{author_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return jsonify({
                "status": "success",
                "data": cached_data,
                "cached": True
            }), 200
        
        # 这里可以实现具体的作者详情获取逻辑
        return jsonify({
            "status": "error",
            "message": "功能开发中"
        }), 501
        
    except Exception as e:
        logger.error(f"获取作者详情失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==================== 错误处理 ====================
@api_bp.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return jsonify({
        "status": "error",
        "message": "请求的资源不存在"
    }), 404


@api_bp.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    return jsonify({
        "status": "error",
        "message": "服务器内部错误"
    }), 500


def create_api_blueprint():
    """创建API Blueprint"""
    return api_bp

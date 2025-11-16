"""
网络相关端点（引用网络和协作网络）
支持多维度过滤，包括大学、学科、年份范围、引用次数等
"""
import logging
from flask import Blueprint, request, jsonify
from api.services import NetworkService

logger = logging.getLogger(__name__)

networks_bp = Blueprint('networks', __name__)

# 初始化网络服务
network_service = NetworkService(use_redis=False)


# ==================== 论文引用网络 ====================
@networks_bp.route('/networks/citation', methods=['GET'])
def get_citation_network():
    """
    获取论文引用网络（支持多维度过滤）
    ---
    tags:
      - Networks
    parameters:
      - name: year_min
        in: query
        type: integer
        required: false
        default: 2020
        description: 起始年份
      - name: year_max
        in: query
        type: integer
        required: false
        default: 2024
        description: 结束年份
      - name: limit
        in: query
        type: integer
        required: false
        default: 500
        description: 节点数限制 (最大5000)
      - name: university
        in: query
        type: string
        required: false
        description: 大学名称或ID（如"MIT"、"Stanford"或"I136199984"）
      - name: discipline
        in: query
        type: string
        required: false
        description: 学科名称或ID（如"Machine Learning"、"Artificial Intelligence"或"T10001"）
      - name: min_citations
        in: query
        type: integer
        required: false
        default: 0
        description: 最少引用次数 (可选)
    responses:
      200:
        description: 成功获取引用网络
        schema:
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
            query_params:
              type: object
              description: 返回查询参数及其ID转换结果
            cached:
              type: boolean
      404:
        description: 没有找到符合条件的论文
      500:
        description: 服务器错误
    """
    try:
        # 获取查询参数
        year_min = request.args.get('year_min', 2020, type=int)
        year_max = request.args.get('year_max', 2024, type=int)
        limit = request.args.get('limit', 500, type=int)
        university = request.args.get('university', None, type=str)
        discipline = request.args.get('discipline', None, type=str)
        min_citations = request.args.get('min_citations', 0, type=int)
        
        # 根据论文数量自动选择处理方式
        # 论文数 > 5000 时使用流式模式（内存优化）
        use_streaming = limit > 5000
        
        logger.info(f"获取引用网络: limit={limit}, use_streaming={use_streaming}")
        
        if use_streaming:
            # 使用流式处理模式（内存优化，推荐用于大规模数据）
            logger.info("使用流式处理模式获取大规模引用网络...")
            result = network_service.get_citation_network_streaming(
                year_min=year_min,
                year_max=year_max,
                limit=limit,
                university=university,
                discipline=discipline,
                min_citations=min_citations,
                batch_size=1000
            )
        else:
            # 使用标准处理模式（适合中小规模数据）
            result = network_service.get_citation_network(
                year_min=year_min,
                year_max=year_max,
                limit=limit,
                university=university,
                discipline=discipline,
                min_citations=min_citations
            )
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.warning(f"参数错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        logger.error(f"获取引用网络失败: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==================== 作者协作网络 ====================
@networks_bp.route('/networks/collaboration', methods=['GET'])
def get_collaboration_network():
    """
    获取作者协作网络（支持多维度过滤）
    ---
    tags:
      - Networks
    parameters:
      - name: year_min
        in: query
        type: integer
        required: false
        default: 2020
        description: 起始年份
      - name: year_max
        in: query
        type: integer
        required: false
        default: 2024
        description: 结束年份
      - name: limit
        in: query
        type: integer
        required: false
        default: 500
        description: 论文数限制
      - name: min_collaborations
        in: query
        type: integer
        required: false
        default: 1
        description: 最少协作次数
      - name: university
        in: query
        type: string
        required: false
        description: 大学名称或ID（如"MIT"、"Stanford"或"I136199984"）
      - name: discipline
        in: query
        type: string
        required: false
        description: 学科名称或ID（如"Machine Learning"、"Artificial Intelligence"或"T10001"）
    responses:
      200:
        description: 成功获取协作网络
        schema:
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                network:
                  type: object
                  description: 网络拓扑数据
                statistics:
                  type: object
                  description: 网络统计信息
                communities:
                  type: array
                  description: 社区检测结果
                query_params:
                  type: object
                  description: 查询参数及其ID转换结果
            cached:
              type: boolean
      404:
        description: 未获取到数据
      500:
        description: 服务器错误
    """
    try:
        # 获取查询参数
        year_min = request.args.get('year_min', 2020, type=int)
        year_max = request.args.get('year_max', 2024, type=int)
        limit = request.args.get('limit', 500, type=int)
        min_collaborations = request.args.get('min_collaborations', 1, type=int)
        university = request.args.get('university', None, type=str)
        discipline = request.args.get('discipline', None, type=str)
        
        # 调用服务
        result = network_service.get_collaboration_network(
            year_min=year_min,
            year_max=year_max,
            limit=limit,
            min_collaborations=min_collaborations,
            university=university,
            discipline=discipline
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.warning(f"参数错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        logger.error(f"获取协作网络失败: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

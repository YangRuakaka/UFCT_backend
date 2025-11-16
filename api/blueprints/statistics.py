"""
统计相关端点 - 提供时间序列和分布统计数据
"""
import logging
from flask import Blueprint, request, jsonify
from api.services import StatisticsService
from api.exceptions import DataNotFoundException, DataFetchException

logger = logging.getLogger(__name__)

statistics_bp = Blueprint('statistics', __name__)

# 初始化服务
statistics_service = StatisticsService(use_redis=False)


@statistics_bp.route('/papers/statistics', methods=['GET'])
def get_papers_statistics():
    """
    获取论文统计数据 - 时间序列和专利引用分布
    
    用于前端创建两个协调的D3.js仪表板：
    1. 时间序列图表：显示过去10年CS相关论文数量
    2. 直方图：显示专利引用分布
    交互：点击时间序列上的数据点，直方图更新显示该年份的分布
    
    ---
    tags:
      - Statistics
    parameters:
      - name: university
        in: query
        type: string
        required: false
        description: 大学名称或ID（例："MIT"、"Stanford"或"I136199984"）
      - name: discipline
        in: query
        type: string
        required: false
        description: 学科名称或ID（例："Computer Science"或"T10001"，可选）
      - name: topics
        in: query
        type: string
        required: false
        description: 逗号分隔的多个学科列表（例："Computer Science,Machine Learning,Deep Learning"）
      - name: year_min
        in: query
        type: integer
        required: false
        default: 2015
        description: 起始年份
      - name: year_max
        in: query
        type: integer
        required: false
        default: 2024
        description: 结束年份
    responses:
      200:
        description: 成功获取统计数据
        schema:
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                timeline:
                  type: array
                  description: 按年份的论文数量统计
                  items:
                    type: object
                    properties:
                      year:
                        type: integer
                      paperCount:
                        type: integer
                      growth_rate:
                        type: number
                        description: 同比增长率（可能为null）
                
                global_histogram:
                  type: array
                  description: 所有论文的专利引用分布
                  items:
                    type: object
                    properties:
                      bin_range:
                        type: string
                        example: "0-10"
                      bin_start:
                        type: integer
                      bin_end:
                        type: integer
                      count:
                        type: integer
                      percentage:
                        type: number
                
                histogram_by_year:
                  type: object
                  description: 按年份的详细直方图数据（用于交互更新）
                  additionalProperties:
                    type: array
                    items:
                      type: object
                
                metadata:
                  type: object
                  description: 统计元数据
                  properties:
                    total_papers:
                      type: integer
                    total_patents:
                      type: integer
                    avg_patent_count_per_paper:
                      type: number
                    max_patent_count:
                      type: integer
                    min_patent_count:
                      type: integer
                    patent_count_std_dev:
                      type: number
                    year_range:
                      type: object
                      properties:
                        min:
                          type: integer
                        max:
                          type: integer
            cached:
              type: boolean
              description: 是否从缓存获取
      400:
        description: 请求参数错误
      404:
        description: 未找到符合条件的论文数据
      500:
        description: 服务器错误
    """
    try:
        # 获取查询参数
        university = request.args.get('university', None, type=str)
        discipline = request.args.get('discipline', None, type=str)
        topics = request.args.get('topics', None, type=str)
        year_min = request.args.get('year_min', 2015, type=int)
        year_max = request.args.get('year_max', 2024, type=int)
        
        # 处理 topics 参数（逗号分隔的多个学科）
        # 优先级：topics > discipline
        if topics:
            discipline = topics
        
        # 验证年份范围
        if year_min > year_max:
            return jsonify({
                "status": "error",
                "message": "year_min 必须小于或等于 year_max"
            }), 400
        
        if year_max - year_min > 100:
            return jsonify({
                "status": "error",
                "message": "年份范围过大（最多100年）"
            }), 400
        
        logger.info(
            f"获取统计数据: university={university}, "
            f"discipline={discipline}, {year_min}-{year_max}"
        )
        
        # 调用服务获取统计数据
        result = statistics_service.get_papers_statistics(
            university=university,
            discipline=discipline,
            year_min=year_min,
            year_max=year_max
        )
        
        return jsonify(result), 200
    
    except DataNotFoundException as e:
        logger.warning(f"数据不存在: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    
    except DataFetchException as e:
        logger.error(f"数据获取失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "数据获取失败，请稍后重试"
        }), 500
    
    except ValueError as e:
        logger.warning(f"参数验证失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"参数错误: {str(e)}"
        }), 400
    
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "服务器内部错误"
        }), 500

"""
论文和作者详情端点
"""
import logging
from flask import Blueprint, request, jsonify
from api.services import PaperService, AuthorService

logger = logging.getLogger(__name__)

papers_authors_bp = Blueprint('papers_authors', __name__)

# 初始化服务
paper_service = PaperService(use_redis=False)
author_service = AuthorService(use_redis=False)


# ==================== 论文详情 ====================
@papers_authors_bp.route('/papers/<string:paper_id>', methods=['GET'])
def get_paper_details(paper_id: str):
    """
    获取论文详情
    ---
    tags:
      - Papers
    parameters:
      - name: paper_id
        in: path
        type: string
        required: true
        description: 论文ID (OpenAlex ID 或 DOI)
    responses:
      200:
        description: 成功获取论文详情
        schema:
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                id:
                  type: string
                title:
                  type: string
                year:
                  type: integer
                cited_by_count:
                  type: integer
            cached:
              type: boolean
      404:
        description: 论文不存在
      500:
        description: 服务器错误
    """
    try:
        result = paper_service.get_paper_details(paper_id)
        return jsonify(result), 200
        
    except ValueError as e:
        logger.warning(f"论文不存在: {paper_id}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        logger.error(f"获取论文详情失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==================== 作者详情 ====================
@papers_authors_bp.route('/authors/<string:author_id>', methods=['GET'])
def get_author_details(author_id: str):
    """
    获取作者详情
    ---
    tags:
      - Authors
    parameters:
      - name: author_id
        in: path
        type: string
        required: true
        description: 作者ID
    responses:
      200:
        description: 成功获取作者详情
        schema:
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                author_id:
                  type: string
                name:
                  type: string
                publication_count:
                  type: integer
            cached:
              type: boolean
      404:
        description: 作者不存在
      500:
        description: 服务器错误
    """
    try:
        result = author_service.get_author_details(author_id)
        return jsonify(result), 200
        
    except ValueError as e:
        logger.warning(f"作者不存在: {author_id}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        logger.error(f"获取作者详情失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

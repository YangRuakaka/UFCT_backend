"""
健康检查端点
"""
import logging
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health():
    """
    健康检查端点
    ---
    tags:
      - Health
    responses:
      200:
        description: 服务正常运行
        schema:
          properties:
            status:
              type: string
              example: "ok"
            version:
              type: string
              example: "1.0.0"
            message:
              type: string
              example: "UFCT Backend is running"
    """
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "message": "UFCT Backend is running"
    }), 200

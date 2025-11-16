"""
配置信息端点
"""
import logging
from flask import Blueprint, jsonify, request
from api.services import ConfigService

logger = logging.getLogger(__name__)

config_bp = Blueprint('config', __name__)

# 初始化配置服务
config_service = ConfigService()




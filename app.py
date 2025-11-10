"""
主应用程序 - UFCT Backend
"""
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Flasgger
from config import get_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name: str = None):
    """
    创建Flask应用
    
    Args:
        config_name: 配置名称 ('development', 'production', 'testing')
    
    Returns:
        Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    config = get_config(config_name)
    app.config.from_object(config)
    
    # 启用CORS
    CORS(app)
    
    # 初始化 Swagger/Flasgger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }
    
    Flasgger(app, config=swagger_config)
    
    logger.info(f"Flask应用初始化: {config_name or 'development'}")
    
    # 注册API蓝图
    from api import init_api_blueprint
    blueprint = init_api_blueprint()
    app.register_blueprint(blueprint, url_prefix='/api')
    
    # 添加健康检查路由
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            "status": "ok",
            "service": "UFCT Backend",
            "version": "1.0.0"
        })
    
    logger.info("应用初始化完成")
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)

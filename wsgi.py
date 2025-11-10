"""
WSGI 应用程序入口 - 用于生产部署（Gunicorn/uWSGI）
"""
import os
from app import create_app

# 根据环境变量选择配置
env = os.getenv('FLASK_ENV', 'production')
app = create_app(env)

if __name__ == "__main__":
    app.run()

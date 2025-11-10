#!/bin/bash
# UFCT Backend 快速启动脚本（Linux/Mac）

echo "==========================================="
echo "UFCT Backend 项目初始化"
echo "==========================================="

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python 版本: $python_version"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo "✓ 虚拟环境创建完成"
else
    echo "✓ 虚拟环境已存在"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt
echo "✓ 依赖安装完成"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ 已创建 .env（请手动配置 GOOGLE_APPLICATION_CREDENTIALS）"
    fi
else
    echo "✓ .env 文件已存在"
fi

echo ""
echo "==========================================="
echo "初始化完成！"
echo "==========================================="
echo ""
echo "启动应用："
echo "  开发环境: python app.py"
echo "  生产环境: gunicorn wsgi:app"
echo ""
echo "访问地址: http://localhost:5000"
echo "API 文档: http://localhost:5000/api (需前端支持)"

@echo off
REM UFCT Backend 快速启动脚本（Windows）

echo =========================================
echo UFCT Backend 项目初始化
echo =========================================

REM 检查 Python 版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✓ Python 版本: %python_version%

REM 创建虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    echo ✓ 虚拟环境创建完成
) else (
    echo ✓ 虚拟环境已存在
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt
echo ✓ 依赖安装完成

REM 检查 .env 文件
if not exist ".env" (
    echo ⚠️  .env 文件不存在
    if exist ".env.example" (
        copy .env.example .env
        echo ✓ 已创建 .env（请手动配置 GOOGLE_APPLICATION_CREDENTIALS）
    )
) else (
    echo ✓ .env 文件已存在
)

echo.
echo =========================================
echo 初始化完成！
echo =========================================
echo.
echo 启动应用：
echo   开发环境: python app.py
echo   生产环境: gunicorn wsgi:app
echo.
echo 访问地址: http://localhost:5000
echo API 文档: 详见 API_DOCUMENTATION.md
echo.
pause

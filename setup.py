"""
快速开始脚本 - 一键部署
"""
import os
import sys
import subprocess

def setup_environment():
    """设置环境"""
    print("=" * 60)
    print("UFCT Backend 快速启动")
    print("=" * 60)
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print("❌ Python 版本过低，需要 3.8+")
        sys.exit(1)
    
    print("✓ Python 版本:", sys.version.split()[0])
    
    # 检查虚拟环境
    venv_path = "venv"
    if not os.path.exists(venv_path):
        print("\n创建虚拟环境...")
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print("✓ 虚拟环境创建完成")
    else:
        print("✓ 虚拟环境已存在")
    
    # 激活虚拟环境并安装依赖
    pip_executable = os.path.join(venv_path, "Scripts", "pip") if os.name == 'nt' else os.path.join(venv_path, "bin", "pip")
    
    print("\n安装依赖...")
    subprocess.run([pip_executable, "install", "-r", "requirements.txt"], check=True)
    print("✓ 依赖安装完成")
    
    # 检查 .env 文件
    if not os.path.exists(".env"):
        print("\n⚠️  .env 文件不存在")
        print("请复制 .env.example 为 .env 并配置 GOOGLE_APPLICATION_CREDENTIALS")
        
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✓ 已创建 .env（请手动配置）")
    else:
        print("✓ .env 文件已存在")
    
    print("\n" + "=" * 60)
    print("设置完成！")
    print("=" * 60)
    print("\n启动应用:")
    print("  - 开发环境: python app.py")
    print("  - 生产环境: gunicorn wsgi:app")
    print("\n访问地址: http://localhost:5000")
    print("API 文档: 详见 README.md")


if __name__ == "__main__":
    setup_environment()

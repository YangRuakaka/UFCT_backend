# UFCT Backend - 学术合作网络分析系统

一个基于 Flask 的学术合作网络分析服务，使用 OpenAlex API 获取论文、作者和引用数据，支持复杂的网络分析和统计功能。

## 📋 目录
- [项目概述](#项目概述)
- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [配置指南](#配置指南)
- [运行服务](#运行服务)
- [API 文档](#api-文档)
- [项目结构](#项目结构)
- [常见问题](#常见问题)

---

## 项目概述

UFCT Backend 是一个强大的学术网络分析平台，提供以下核心功能：

✨ **主要功能**
- 📚 论文检索和管理（基于 OpenAlex）
- 👥 作者信息查询和合作关系分析
- 🔗 学术引用网络构建
- 📊 合作统计和网络分析
- 💾 缓存机制支持（内存/Redis）
- ⚡ 批量优化查询（OR 语法，性能提升 20-95 倍）

---

## 系统要求

### 硬件要求
- **CPU**: 双核或更高
- **内存**: 4GB 或更高
- **磁盘**: 至少 500MB 空闲空间

### 软件要求
- **Python**: 3.8 或更高版本
- **pip**: Python 包管理器
- **Git**: 版本控制（可选）

### 可选依赖
- **Redis**: 用于分布式缓存（可选）
- **PostgreSQL/MySQL**: 用于生产环境数据库（可选）

---

## 安装步骤

### 1️⃣ 克隆项目

```bash
# 使用 HTTPS
git clone https://github.com/YangRuakaka/UFCT_backend.git
cd UFCT_backend

# 或使用 SSH
git clone git@github.com:YangRuakaka/UFCT_backend.git
cd UFCT_backend
```

### 2️⃣ 创建虚拟环境（推荐）

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ 安装依赖

```bash
# 安装所有项目依赖
pip install -r requirements.txt

# 如果需要更新 pip
pip install --upgrade pip
```

### 4️⃣ 验证安装

```bash
# 检查 Python 版本
python --version

# 列出已安装的包
pip list
```

---

## 配置指南

### 1️⃣ 配置文件设置

编辑 `config.py` 文件，根据需要调整配置：

```python
# 基础配置
DEBUG = True                    # 开发模式
SECRET_KEY = 'your-secret-key' # Flask 密钥

# OpenAlex API 配置
OPENALEX_EMAIL = 'your-email@example.com'  # 加入 Polite Pool
MAX_RPS = 10                                 # 最大请求速率

# 缓存配置
CACHE_TYPE = 'simple'           # 缓存类型: simple, redis
CACHE_REDIS_URL = 'redis://localhost:6379/0'  # Redis 连接

# 数据库配置（可选）
SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 日志配置
LOG_LEVEL = 'INFO'
```

### 2️⃣ 环境变量配置（可选）

创建 `.env` 文件（如果应用支持）：

```env
FLASK_ENV=development
FLASK_DEBUG=True
OPENALEX_EMAIL=your-email@example.com
REDIS_URL=redis://localhost:6379/0
```

### 3️⃣ OpenAlex API 邮箱设置

获取更好的 API 响应性能，需要提供邮箱：

```python
# config.py
OPENALEX_EMAIL = 'your-email@example.com'  # ⭐ 重要：加入 Polite Pool
```

---

## 运行服务

### 📍 方式一：使用 Flask 开发服务器（推荐开发环境）

```bash
# 激活虚拟环境（如果还没激活）
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 运行应用
python app.py
```

**预期输出:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

访问地址：http://localhost:5000

### 📍 方式二：使用 Gunicorn（推荐生产环境）

```bash
# 安装 Gunicorn（如果未安装）
pip install gunicorn

# 运行应用（4 个 worker 进程）
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

# 指定日志级别
gunicorn -w 4 -b 0.0.0.0:5000 --log-level info wsgi:app
```

### 📍 方式三：使用 WSGI 直接运行

```bash
# Python 直接导入运行
python -c "from wsgi import app; app.run(debug=True)"
```

### 📍 方式四：Docker 容器运行（如果有 Dockerfile）

```bash
# 构建镜像
docker build -t ufct-backend .

# 运行容器
docker run -p 5000:5000 ufct-backend
```

---

## 🧪 测试连接

服务启动后，验证是否正常运行：

### 1. 检查健康状态
```bash
curl http://localhost:5000/health
# 或
curl http://127.0.0.1:5000/api/health
```

**预期响应:**
```json
{
  "status": "healthy",
  "message": "Service is running"
}
```

### 2. 查询论文
```bash
curl "http://localhost:5000/api/papers?title=machine%20learning"
```

### 3. 查询作者信息
```bash
curl "http://localhost:5000/api/authors?name=Albert%20Einstein"
```

### 4. 获取统计信息
```bash
curl "http://localhost:5000/api/statistics"
```

---

## 📚 API 文档

### 主要端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/papers` | GET | 查询论文 |
| `/api/authors` | GET | 查询作者信息 |
| `/api/networks` | GET | 获取合作网络 |
| `/api/statistics` | GET | 获取统计数据 |

详细 API 文档请参考 `NETWORKS_API_FOR_LLM.md`

---

## 📁 项目结构

```
UFCT_backend/
├── app.py                      # Flask 应用入口
├── config.py                   # 配置文件
├── wsgi.py                     # WSGI 入口（生产环境）
├── requirements.txt            # Python 依赖列表
├── README.md                   # 本文件
├── NETWORKS_API_FOR_LLM.md     # 详细 API 文档
│
├── api/                        # API 模块
│   ├── __init__.py
│   ├── routes.py              # 路由定义
│   ├── exceptions.py          # 自定义异常
│   ├── utils.py               # API 工具函数
│   ├── blueprints/            # API 蓝图
│   │   ├── health.py          # 健康检查端点
│   │   ├── papers.py          # 论文相关端点
│   │   ├── authors.py         # 作者相关端点
│   │   ├── networks.py        # 网络相关端点
│   │   └── statistics.py      # 统计相关端点
│   ├── services/              # 业务逻辑层
│   │   ├── paper_service.py
│   │   ├── author_service.py
│   │   ├── network_service.py
│   │   └── statistics_service.py
│   ├── repositories/          # 数据访问层
│   │   ├── paper_repository.py
│   │   ├── author_repository.py
│   │   ├── network_repository.py
│   │   └── statistics_repository.py
│   └── utils/                 # 工具函数
│       ├── param_validator.py # 参数验证
│       ├── name_resolver.py   # 名称解析
│       └── common.py          # 通用函数
│
├── data/                      # 数据获取模块
│   ├── openalex_fetcher.py   # OpenAlex API 封装
│   └── param_validator.py    # 数据验证
│
├── models/                    # 数据模型
│   ├── base.py               # 基础模型
│   ├── paper.py              # 论文模型
│   ├── author.py             # 作者模型
│   └── network.py            # 网络模型
│
└── cache/                     # 缓存目录
```

---

## 🔧 常见问题

### Q1: 运行时报错 `ModuleNotFoundError: No module named 'flask'`

**解决方案:**
```bash
# 确保虚拟环境已激活
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt

# 验证安装
python -c "import flask; print(flask.__version__)"
```

### Q2: 端口 5000 已被占用

**解决方案:**
```bash
# 方案一：更换端口
python app.py --port 8000

# 方案二：杀死占用端口的进程
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

### Q3: OpenAlex API 响应缓慢或 429 错误

**解决方案:**
```python
# config.py 中配置
OPENALEX_EMAIL = 'your-email@example.com'  # 加入 Polite Pool
MAX_RPS = 8                                  # 降低请求速率
BATCH_SIZE = 50                              # 批量查询大小
```

### Q4: 如何使用 Redis 缓存

```python
# config.py 中配置
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'

# 启动 Redis 服务（需提前安装）
# Windows: redis-server
# macOS: brew services start redis
# Linux: sudo service redis-server start
```

### Q5: 如何看日志/调试

```bash
# 启用调试模式
set FLASK_ENV=development  # Windows
export FLASK_ENV=development  # macOS/Linux

# 查看详细日志
python app.py --debug
```

---

## 📈 性能优化说明

项目使用了多项技术优化查询性能：

- ⚡ **OR 语法批量查询**: 性能提升 20-95 倍
- 🔄 **令牌桶限流**: 精确控制 API 请求速率
- 📦 **批处理**: 智能批量大小自适应
- 💾 **缓存机制**: 支持内存和 Redis 缓存
- 🔁 **指数退避重试**: 自动处理限流情况

详见 `NETWORKS_API_FOR_LLM.md` 中的性能优化章节。

---

## 📝 许可证

MIT License

---

## 👤 作者

[YangRuakaka](https://github.com/YangRuakaka)

---

## 💡 常用命令速查表

```bash
# 激活虚拟环境
venv\Scripts\activate              # Windows
source venv/bin/activate           # macOS/Linux

# 安装/更新依赖
pip install -r requirements.txt
pip install --upgrade -r requirements.txt

# 运行开发服务器
python app.py

# 运行生产服务器
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

# 测试 API
curl http://localhost:5000/health

# 停止服务
Ctrl + C  # 在终端中按此组合键

# 退出虚拟环境
deactivate
```

---

**最后更新**: 2025年11月16日

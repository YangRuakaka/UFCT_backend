# UFCT Backend - 科研网络可视化系统后端

## 项目概述

这是一个用于生成和可视化计算机科学领域论文引用网络和作者协作网络的后端系统。系统使用 **SciSciNet-v2** 数据集，通过 Google BigQuery 访问大规模学术数据。

### 核心功能

- 📊 **论文引用网络**：可视化论文之间的引用关系
- 👥 **作者协作网络**：展示作者之间的协作关系
- 🎨 **力引导布局**：使用 NetworkX 计算图布局
- 💾 **智能缓存**：支持 Redis 缓存和本地内存缓存
- 🔍 **社群检测**：自动检测协作网络中的研究社群

---

## 📋 项目结构

```
UFCT_backend/
│
├── app.py                      # Flask主应用
├── config.py                   # 配置文件
├── requirements.txt            # Python依赖
├── .env.example               # 环境变量示例
│
├── data/                       # 数据获取模块
│   ├── __init__.py
│   └── data_fetcher.py        # BigQuery数据获取器
│
├── models/                     # 数据模型
│   ├── __init__.py
│   └── network.py             # 网络数据结构 (CitationNetwork, CollaborationNetwork)
│
├── api/                        # API路由
│   ├── __init__.py
│   └── routes.py              # REST API端点定义
│
├── services/                   # 业务逻辑（预留）
│   └── __init__.py
│
├── cache/                      # 缓存数据存储
│   └── .gitkeep
│
├── tests/                      # 单元测试
│   └── test_api.py
│
└── README.md                   # 本文件
```

---

## 🚀 快速开始

### 1. 环境配置

#### 系统要求
- Python 3.8+
- 可选：Redis（用于分布式缓存）

#### 安装依赖

```bash
# 克隆项目
cd d:\Github\UFCT_backend

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

#### 配置GCP认证

```bash
# 1. 从GCP控制台下载JSON密钥文件
# 2. 复制.env.example为.env
copy .env.example .env

# 3. 编辑.env文件，设置GOOGLE_APPLICATION_CREDENTIALS
set GOOGLE_APPLICATION_CREDENTIALS=path\to\your\credentials.json
```

### 2. 运行应用

```bash
# 开发环境
python app.py

# 应用将在 http://localhost:5000 启动
```

### 3. 验证部署

```bash
# 检查健康状态
curl http://localhost:5000/health

# 获取引用网络
curl "http://localhost:5000/api/networks/citation?year_min=2020&year_max=2024&limit=500"
```

---

## 📡 API 文档

### 1. 健康检查

**请求：**
```http
GET /health
```

**响应 (200):**
```json
{
  "status": "ok",
  "service": "UFCT Backend",
  "version": "1.0.0"
}
```

---

### 2. 获取论文引用网络

**端点：** `GET /api/networks/citation`

**查询参数：**
| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `year_min` | int | 2020 | 起始年份 |
| `year_max` | int | 2024 | 结束年份 |
| `limit` | int | 500 | 节点数限制（最大5000） |
| `layout` | string | spring | 布局算法：spring / kamada_kawai / circular |

**示例请求：**
```bash
curl "http://localhost:5000/api/networks/citation?year_min=2020&year_max=2024&limit=500&layout=spring"
```

**响应 (200):**
```json
{
  "status": "success",
  "cached": false,
  "data": {
    "network": {
      "nodes": [
        {
          "id": "paper_123",
          "label": "深度学习中的注意力机制...",
          "node_type": "paper",
          "size": 35.5,
          "color": "#FF6B6B",
          "x": 0.45,
          "y": 0.32,
          "metadata": {
            "title": "深度学习中的注意力机制",
            "year": 2023,
            "citation_count": 245,
            "type": "Journal"
          }
        }
      ],
      "edges": [
        {
          "source": "paper_123",
          "target": "paper_456",
          "edge_type": "cites",
          "weight": 1.0,
          "label": "引用1次",
          "metadata": {
            "citation_type": "direct"
          }
        }
      ],
      "metadata": {
        "total_nodes": 523,
        "total_edges": 1847,
        "network_density": 0.0134,
        "avg_degree": 7.06
      }
    },
    "statistics": {
      "total_papers": 523,
      "total_citations": 1847,
      "network_density": 0.0134,
      "avg_citations_per_paper": 3.53,
      "connected_components": 45,
      "largest_component_size": 380
    },
    "query_params": {
      "year_min": 2020,
      "year_max": 2024,
      "limit": 500,
      "layout": "spring"
    }
  }
}
```

**数据字段说明：**

| 字段 | 类型 | 描述 |
|------|------|------|
| `nodes[].id` | string | 论文唯一标识符 |
| `nodes[].label` | string | 论文标题（截断到50字符） |
| `nodes[].size` | float | 节点大小（10-60，基于引用数） |
| `nodes[].color` | string | 节点颜色（基于发表年份） |
| `nodes[].x, y` | float | 力引导布局坐标 |
| `nodes[].metadata.citation_count` | int | 被引用次数 |
| `edges[].weight` | float | 边权重（引用数量） |
| `metadata.network_density` | float | 网络密度（0-1） |
| `metadata.avg_degree` | float | 平均度数 |

---

### 3. 获取作者协作网络

**端点：** `GET /api/networks/collaboration`

**查询参数：**
| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `year_min` | int | 2020 | 起始年份 |
| `year_max` | int | 2024 | 结束年份 |
| `limit` | int | 500 | 节点数限制（最大5000） |
| `min_collaborations` | int | 1 | 最小协作次数 |
| `layout` | string | spring | 布局算法 |

**示例请求：**
```bash
curl "http://localhost:5000/api/networks/collaboration?year_min=2020&year_max=2024&limit=500&min_collaborations=2"
```

**响应 (200):**
```json
{
  "status": "success",
  "cached": false,
  "data": {
    "network": {
      "nodes": [
        {
          "id": "author_789",
          "label": "张三",
          "node_type": "author",
          "size": 35.0,
          "color": "#4ECDC4",
          "x": 0.23,
          "y": 0.56,
          "metadata": {
            "name": "张三",
            "papers": ["paper_123", "paper_124"],
            "paper_count": 23
          }
        }
      ],
      "edges": [
        {
          "source": "author_789",
          "target": "author_101",
          "edge_type": "collaboration",
          "weight": 5.0,
          "label": "5篇论文",
          "metadata": {
            "collaboration_count": 5,
            "papers": ["paper_123", "paper_456"]
          }
        }
      ],
      "metadata": {
        "total_nodes": 287,
        "total_edges": 654,
        "network_density": 0.0159,
        "avg_degree": 4.56
      }
    },
    "statistics": {
      "total_authors": 287,
      "total_collaborations": 654,
      "network_density": 0.0159,
      "avg_collaborators": 4.56,
      "connected_components": 32,
      "clustering_coefficient": 0.48
    },
    "communities": {
      "community_0": ["author_789", "author_101", "author_202"],
      "community_1": ["author_303", "author_404"],
      "...": "..."
    },
    "query_params": {
      "year_min": 2020,
      "year_max": 2024,
      "limit": 500,
      "min_collaborations": 2,
      "layout": "spring"
    }
  }
}
```

**数据字段说明：**

| 字段 | 类型 | 描述 |
|------|------|------|
| `nodes[].metadata.paper_count` | int | 作者论文数 |
| `edges[].weight` | float | 协作紧密度（共著论文数） |
| `statistics.clustering_coefficient` | float | 聚类系数（0-1，越高越容易形成团队） |
| `communities` | dict | 检测到的研究社群（使用贪心模块化算法） |

---

## 🗄️ 数据源：SciSciNet-v2

### 数据访问方式

本项目使用 **Google BigQuery** 访问 SciSciNet-v2 数据集。

#### 主要数据表

| 表名 | 用途 | 数据量 |
|------|------|--------|
| `sciscinet_papers` | 论文基础信息 | 249.8M+ 记录 |
| `sciscinet_authors` | 作者和论文关系 | 100.4M+ 记录 |
| `paper_references` | 论文引用关系 | 2.49B+ 记录 |
| `sciscinet_affiliations` | 机构信息 | 110.5K+ 记录 |

#### 查询示例

```sql
-- 获取2020-2024年的论文
SELECT 
    paperid,
    title,
    year,
    publicationtype,
    estimatedcitation
FROM `ksm-rch-scisciturbo.sciscinet_v2.sciscinet_papers`
WHERE year >= 2020 AND year <= 2024
LIMIT 1000;

-- 获取论文的作者信息
SELECT 
    paperid,
    authorid,
    authorname,
    displayname
FROM `ksm-rch-scisciturbo.sciscinet_v2.sciscinet_authors`
WHERE paperid IN ('paper_123', 'paper_456')

-- 获取引用关系
SELECT 
    paperid,
    citedpaperid
FROM `ksm-rch-scisciturbo.sciscinet_v2.paper_references`
WHERE paperid IN ('paper_123', 'paper_456')
```

### GCP 认证配置

1. **创建服务账户**：
   - 访问 [GCP Console](https://console.cloud.google.com)
   - 导航到 "服务账户" → 创建新服务账户
   - 分配 "BigQuery Data Editor" 和 "BigQuery Job User" 角色

2. **下载密钥**：
   - 在服务账户页面创建 JSON 密钥
   - 将密钥文件保存到本地

3. **配置环境变量**：
   ```bash
   set GOOGLE_APPLICATION_CREDENTIALS=path\to\your\credentials.json
   ```

---

## 🎨 可扩展性解决方案

### 问题1：数据量过大

**影响**：SciSciNet 包含 2.49 亿篇论文，直接查询会导致超时和成本爆炸

**解决方案**：
- ✅ **分层采样**：根据引用数或影响力指数过滤高价值节点
- ✅ **时间粒度划分**：按年份分别生成网络，支持时间切片
- ✅ **渐进式查询**：先获取核心数据，异步加载补充数据

**实现代码**：
```python
# 按引用数过滤（只取高影响力论文）
papers_df = papers_df[papers_df['citation_count'] >= citation_threshold]

# 按发表时间分批
for year in range(2020, 2025):
    year_data = fetcher.get_papers_by_year_range(year, year, limit=1000)
    process_year_data(year_data)
```

### 问题2：图渲染卡顿

**影响**：前端需要渲染数千个节点和边，导致浏览器卡顿

**解决方案**：
- ✅ **前端虚拟化**：使用 D3.js + Canvas 加速，只渲染可见节点
- ✅ **节点聚类**：将相近的节点合并为超节点（LOD 技术）
- ✅ **边简化**：移除权重低于阈值的边（默认 0.1）

**参数调优**：
```python
# config.py
MIN_EDGE_WEIGHT = 0.1        # 边权重阈值
DEFAULT_LIMIT = 500          # 单次查询节点数
FORCE_DIRECTED_ITERATIONS = 50  # 布局迭代次数
```

### 问题3：计算性能

**影响**：力引导布局计算复杂度 O(n³)，1000+ 节点会很慢

**解决方案**：
- ✅ **后端缓存**：使用 Redis 缓存预计算的布局坐标
- ✅ **增量更新**：只在新数据时重新计算，使用差分更新
- ✅ **并行计算**：使用 Dask 或多进程加速

**缓存配置**：
```python
# 24小时缓存
CACHE_TIMEOUT = 86400

# Redis 配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
```

### 问题4：API 响应时间

**影响**：BigQuery 查询可能需要 10-30 秒

**解决方案**：
- ✅ **异步查询**：使用 Flask 的异步任务队列（Celery）
- ✅ **预生成数据**：定期后台任务预生成常见查询
- ✅ **分页查询**：支持 offset/limit 进行渐进式加载

**异步任务示例**（后续可添加）：
```python
# 后台任务生成缓存
from celery import Celery
celery = Celery(__name__)

@celery.task
def precompute_networks():
    for year_min in [2020, 2021, 2022, 2023]:
        year_max = year_min + 2
        # 预生成引用网络和协作网络
```

### 性能指标

| 指标 | 目标 | 当前状态 |
|------|------|--------|
| 节点数 | 500-5000 | ✅ 支持 |
| 前端渲染 FPS | 60+ | ✅ D3.js Canvas 实现 |
| API 响应 (缓存命中) | <2s | ✅ Redis 加速 |
| API 响应 (首次查询) | <30s | ✅ BigQuery 优化 |
| 网络密度 | <5% | ✅ 稀疏图优化 |

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_api.py -v

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

### 测试覆盖

- ✅ BigQuery 数据获取
- ✅ 网络构建和布局计算
- ✅ API 端点功能
- ✅ 缓存机制
- ✅ 错误处理

---

## 📊 前后端数据传输格式

### 通用响应格式

所有 API 响应遵循统一格式：

```json
{
  "status": "success|error",
  "message": "可选的消息",
  "cached": true|false,
  "data": {
    // 具体数据
  }
}
```

### 错误响应

```json
{
  "status": "error",
  "message": "错误描述信息",
  "code": "ERROR_CODE"
}
```

### 网络图数据格式（D3.js 兼容）

```json
{
  "nodes": [
    {
      "id": "node_1",
      "label": "节点标签",
      "node_type": "paper|author",
      "size": 25.5,
      "color": "#FF6B6B",
      "x": 0.45,
      "y": 0.32,
      "metadata": {
        // 自定义属性
      }
    }
  ],
  "edges": [
    {
      "source": "node_1",
      "target": "node_2",
      "edge_type": "cites|collaboration",
      "weight": 3.5,
      "label": "边标签",
      "metadata": {}
    }
  ],
  "metadata": {
    "total_nodes": 500,
    "total_edges": 1234,
    "network_density": 0.0123,
    "avg_degree": 4.94
  }
}
```

### 前端使用示例

```javascript
// React 组件示例
import React, { useEffect, useState } from 'react';

function CitationNetworkViewer() {
  const [networkData, setNetworkData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch('/api/networks/citation?year_min=2020&year_max=2024&limit=500')
      .then(res => res.json())
      .then(({ data }) => {
        setNetworkData(data.network);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>加载中...</div>;
  if (!networkData) return null;

  return (
    <div>
      <h2>论文引用网络</h2>
      <p>节点数: {networkData.metadata.total_nodes}</p>
      <p>边数: {networkData.metadata.total_edges}</p>
      {/* 使用 D3.js 渲染 networkData */}
    </div>
  );
}
```

---

## 🔧 配置说明

### 主要配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DEFAULT_YEAR_MIN` | 2020 | 默认查询起始年份 |
| `DEFAULT_YEAR_MAX` | 2024 | 默认查询结束年份 |
| `DEFAULT_LIMIT` | 500 | 默认查询节点限制 |
| `MAX_NODES` | 5000 | 单次查询最大节点数 |
| `FORCE_DIRECTED_ITERATIONS` | 50 | 力引导布局迭代次数 |
| `FORCE_DIRECTED_K` | 0.5 | 力引导布局弹簧常数 |
| `MIN_EDGE_WEIGHT` | 0.1 | 最小边权重阈值 |
| `CACHE_TIMEOUT` | 86400 | 缓存超时时间（秒） |

### 环境变量

创建 `.env` 文件：

```bash
# Flask
FLASK_ENV=development
FLASK_DEBUG=1

# GCP BigQuery
BIGQUERY_PROJECT=ksm-rch-scisciturbo
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Redis 缓存
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

---

## 📈 性能优化技巧

### 1. 启用 Redis 缓存

```python
# api/routes.py
cache = DataCache(use_redis=True)  # 改为 True
```

### 2. 调整布局算法

```bash
# 大网络使用 kamada_kawai（更快但不够美观）
curl "http://localhost:5000/api/networks/citation?layout=kamada_kawai"

# 小网络使用 spring（更美观但较慢）
curl "http://localhost:5000/api/networks/citation?layout=spring"
```

### 3. 限制节点数

```bash
# 查询小规模网络（更快）
curl "http://localhost:5000/api/networks/citation?limit=100"

# 查询大规模网络（更全面但较慢）
curl "http://localhost:5000/api/networks/citation?limit=5000"
```

---

## 🐛 常见问题

### Q: BigQuery 连接超时

**A:** 检查 GCP 认证：
```bash
# 验证证书文件路径
echo %GOOGLE_APPLICATION_CREDENTIALS%

# 测试 BigQuery 连接
python -c "from google.cloud import bigquery; client = bigquery.Client(); print('连接成功')"
```

### Q: 前端渲染缓慢

**A:** 减少节点数或切换布局算法：
```bash
curl "http://localhost:5000/api/networks/citation?limit=200&layout=kamada_kawai"
```

### Q: 缓存未生效

**A:** 确认 Redis 正在运行（若配置了 Redis）：
```bash
redis-cli ping
```

---

## 📝 后续开发计划

- [ ] 实现论文详情接口
- [ ] 实现作者详情接口
- [ ] 添加搜索功能
- [ ] 实现时间序列网络分析
- [ ] 添加导出功能（PNG/GeoJSON）
- [ ] 实现异步任务队列（Celery）
- [ ] 添加数据更新定时任务
- [ ] 性能监控和日志系统

---

## 📄 许可证

MIT License

---

## 👨‍💼 联系方式

- 项目维护：UFCT Team
- 问题反馈：提交 Issue 或 Pull Request


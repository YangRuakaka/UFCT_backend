# API 详细文档

## 📋 目录

1. [基本信息](#基本信息)
2. [健康检查](#健康检查)
3. [论文引用网络](#论文引用网络)
4. [作者协作网络](#作者协作网络)
5. [错误处理](#错误处理)
6. [数据格式规范](#数据格式规范)

---

## 基本信息

### 服务地址
- **基础 URL**: `http://localhost:5000` (开发环境)
- **API 前缀**: `/api`
- **API 版本**: v1.0

### 请求格式
- **Content-Type**: `application/json`
- **字符编码**: UTF-8

### 通用响应格式

所有 API 响应都遵循以下格式：

```json
{
  "status": "success|error",
  "message": "可选的详细信息",
  "cached": true|false,
  "data": {
    // 具体返回数据
  }
}
```

**字段说明**:
- `status`: 请求状态，`success` 成功，`error` 失败
- `message`: 错误或成功消息（可选）
- `cached`: 是否从缓存返回（true=缓存命中，false=实时查询）
- `data`: 返回的具体数据

---

## 健康检查

### 端点

```http
GET /health
```

### 说明
检查服务是否正常运行

### 响应示例

**状态码**: 200 OK

```json
{
  "status": "ok",
  "service": "UFCT Backend",
  "version": "1.0.0"
}
```

### cURL 示例

```bash
curl http://localhost:5000/health
```

---

## 论文引用网络

### 端点

```http
GET /api/networks/citation
```

### 说明
获取指定时间范围内的论文引用网络。返回节点（论文）和边（引用关系）的网络数据，可直接用于 D3.js 等前端可视化库。

### 查询参数

| 参数 | 类型 | 默认值 | 必需 | 范围 | 说明 |
|------|------|--------|------|------|------|
| `year_min` | integer | 2020 | 否 | 1970-2024 | 起始年份（闭包） |
| `year_max` | integer | 2024 | 否 | 1970-2024 | 结束年份（闭包） |
| `limit` | integer | 500 | 否 | 10-5000 | 返回的最大节点数 |
| `layout` | string | spring | 否 | spring,kamada_kawai,circular | 图布局算法 |

### 布局算法说明

| 算法 | 计算速度 | 美观度 | 适用场景 |
|------|--------|--------|---------|
| `spring` | 中等 | ⭐⭐⭐ | 通用，推荐 |
| `kamada_kawai` | 快 | ⭐⭐ | 大规模网络（>1000 节点） |
| `circular` | 很快 | ⭐ | 特殊场景 |

### 请求示例

#### 基础请求
```bash
curl "http://localhost:5000/api/networks/citation"
```

#### 自定义参数
```bash
curl "http://localhost:5000/api/networks/citation?year_min=2022&year_max=2024&limit=200&layout=spring"
```

#### Python 请求示例
```python
import requests

params = {
    'year_min': 2022,
    'year_max': 2024,
    'limit': 500,
    'layout': 'spring'
}

response = requests.get('http://localhost:5000/api/networks/citation', params=params)
data = response.json()

if data['status'] == 'success':
    network = data['data']['network']
    stats = data['data']['statistics']
    print(f"论文数: {len(network['nodes'])}")
    print(f"引用数: {len(network['edges'])}")
```

### 响应示例

**状态码**: 200 OK

```json
{
  "status": "success",
  "cached": false,
  "data": {
    "network": {
      "nodes": [
        {
          "id": "paper_2023_001",
          "label": "深度学习中的注意力机制在自然语言处理中的应用",
          "node_type": "paper",
          "size": 45.5,
          "color": "#6BCF7F",
          "x": 0.432,
          "y": 0.521,
          "metadata": {
            "title": "深度学习中的注意力机制在自然语言处理中的应用",
            "year": 2023,
            "citation_count": 127,
            "type": "Journal"
          }
        },
        {
          "id": "paper_2022_045",
          "label": "Transformer 模型的效率优化研究",
          "node_type": "paper",
          "size": 32.1,
          "color": "#4D96FF",
          "x": 0.621,
          "y": 0.334,
          "metadata": {
            "title": "Transformer 模型的效率优化研究",
            "year": 2022,
            "citation_count": 89,
            "type": "Conference"
          }
        }
      ],
      "edges": [
        {
          "source": "paper_2023_001",
          "target": "paper_2022_045",
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
        "network_density": 0.01344,
        "avg_degree": 7.06
      }
    },
    "statistics": {
      "total_papers": 523,
      "total_citations": 1847,
      "network_density": 0.01344,
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

### 响应字段说明

#### nodes 数组

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 论文唯一标识符 |
| `label` | string | 论文标题（截断到50字符用于显示） |
| `node_type` | string | 节点类型，固定为 "paper" |
| `size` | float | 节点大小（10-60），基于引用数量 |
| `color` | string | 节点颜色，根据年份分配（HEX格式） |
| `x, y` | float | 力引导布局坐标，范围 [0, 1] |
| `metadata.title` | string | 完整论文标题 |
| `metadata.year` | int | 发表年份 |
| `metadata.citation_count` | int | 被引用次数 |
| `metadata.type` | string | 出版类型（Journal/Conference/...） |

#### edges 数组

| 字段 | 类型 | 说明 |
|------|------|------|
| `source` | string | 源论文 ID（引用者） |
| `target` | string | 目标论文 ID（被引用者） |
| `edge_type` | string | 边类型，固定为 "cites" |
| `weight` | float | 边权重（两篇论文之间的引用数） |
| `label` | string | 边标签，用于 Tooltip |
| `metadata.citation_type` | string | 引用类型 |

#### 网络统计

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_papers` | int | 网络中论文总数 |
| `total_citations` | int | 引用关系总数 |
| `network_density` | float | 网络密度（0-1），表示图的连通程度 |
| `avg_citations_per_paper` | float | 平均每篇论文的引用数 |
| `connected_components` | int | 连通分量数（孤立的论文组数） |
| `largest_component_size` | int | 最大连通分量的节点数 |

### 错误响应

**当查询无结果时** (404)
```json
{
  "status": "error",
  "message": "没有找到符合条件的论文"
}
```

**当 BigQuery 连接失败时** (500)
```json
{
  "status": "error",
  "message": "Failed to authenticate with BigQuery: ..."
}
```

---

## 作者协作网络

### 端点

```http
GET /api/networks/collaboration
```

### 说明
获取指定时间范围内的作者协作网络。返回节点（作者）和边（协作关系）的网络数据。

### 查询参数

| 参数 | 类型 | 默认值 | 必需 | 范围 | 说明 |
|------|------|--------|------|------|------|
| `year_min` | integer | 2020 | 否 | 1970-2024 | 起始年份 |
| `year_max` | integer | 2024 | 否 | 1970-2024 | 结束年份 |
| `limit` | integer | 500 | 否 | 10-5000 | 返回的最大节点数 |
| `min_collaborations` | integer | 1 | 否 | 1-100 | 最小协作次数过滤 |
| `layout` | string | spring | 否 | spring,kamada_kawai,circular | 布局算法 |

### 请求示例

#### 基础请求
```bash
curl "http://localhost:5000/api/networks/collaboration"
```

#### 自定义参数（只显示协作 2 次以上的作者）
```bash
curl "http://localhost:5000/api/networks/collaboration?year_min=2022&year_max=2024&limit=300&min_collaborations=2"
```

#### Python 请求示例
```python
import requests

params = {
    'year_min': 2022,
    'year_max': 2024,
    'limit': 500,
    'min_collaborations': 2,
    'layout': 'spring'
}

response = requests.get('http://localhost:5000/api/networks/collaboration', params=params)
data = response.json()

if data['status'] == 'success':
    network = data['data']['network']
    communities = data['data']['communities']
    print(f"作者数: {len(network['nodes'])}")
    print(f"协作数: {len(network['edges'])}")
    print(f"社群数: {len(communities)}")
```

### 响应示例

**状态码**: 200 OK

```json
{
  "status": "success",
  "cached": false,
  "data": {
    "network": {
      "nodes": [
        {
          "id": "author_a123",
          "label": "张三",
          "node_type": "author",
          "size": 38.0,
          "color": "#4ECDC4",
          "x": 0.521,
          "y": 0.437,
          "metadata": {
            "name": "张三",
            "papers": ["paper_001", "paper_002", "paper_003"],
            "paper_count": 23
          }
        },
        {
          "id": "author_b456",
          "label": "李四",
          "node_type": "author",
          "size": 32.0,
          "color": "#4ECDC4",
          "x": 0.612,
          "y": 0.521,
          "metadata": {
            "name": "李四",
            "papers": ["paper_002", "paper_004", "paper_005"],
            "paper_count": 18
          }
        }
      ],
      "edges": [
        {
          "source": "author_a123",
          "target": "author_b456",
          "edge_type": "collaboration",
          "weight": 2.0,
          "label": "2篇论文",
          "metadata": {
            "collaboration_count": 2,
            "papers": ["paper_002", "paper_003"]
          }
        }
      ],
      "metadata": {
        "total_nodes": 287,
        "total_edges": 654,
        "network_density": 0.01593,
        "avg_degree": 4.56
      }
    },
    "statistics": {
      "total_authors": 287,
      "total_collaborations": 654,
      "network_density": 0.01593,
      "avg_collaborators": 4.56,
      "connected_components": 32,
      "clustering_coefficient": 0.482
    },
    "communities": {
      "community_0": ["author_a123", "author_b456", "author_c789"],
      "community_1": ["author_d012", "author_e345"],
      "community_2": ["author_f678", "author_g901", "author_h234"]
    },
    "query_params": {
      "year_min": 2020,
      "year_max": 2024,
      "limit": 500,
      "min_collaborations": 1,
      "layout": "spring"
    }
  }
}
```

### 响应字段说明

#### nodes 数组

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 作者唯一标识符 |
| `label` | string | 作者名称 |
| `node_type` | string | 节点类型，固定为 "author" |
| `size` | float | 节点大小（10-50），基于论文数量 |
| `color` | string | 节点颜色，固定为 "#4ECDC4" |
| `x, y` | float | 力引导布局坐标 |
| `metadata.name` | string | 完整作者名称 |
| `metadata.papers` | array | 该作者发表的论文 ID 列表 |
| `metadata.paper_count` | int | 论文总数 |

#### edges 数组

| 字段 | 类型 | 说明 |
|------|------|------|
| `source` | string | 作者1 的 ID |
| `target` | string | 作者2 的 ID |
| `edge_type` | string | 边类型，固定为 "collaboration" |
| `weight` | float | 协作紧密度（共著论文数） |
| `label` | string | 边标签 |
| `metadata.collaboration_count` | int | 共著论文数 |
| `metadata.papers` | array | 共著论文 ID 列表 |

#### 网络统计

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_authors` | int | 网络中作者总数 |
| `total_collaborations` | int | 协作关系总数 |
| `network_density` | float | 网络密度 |
| `avg_collaborators` | float | 平均合作者数 |
| `connected_components` | int | 连通分量数 |
| `clustering_coefficient` | float | 聚类系数（0-1），表示三角形聚类程度 |

#### 社群检测

`communities` 字段包含自动检测的研究社群：
- 键为社群标识符（如 `community_0`）
- 值为该社群中的作者 ID 列表
- 使用贪心模块化算法检测

---

## 错误处理

### HTTP 状态码

| 状态码 | 说明 | 常见原因 |
|--------|------|---------|
| 200 | 成功 | 请求正常处理 |
| 404 | 未找到 | 没有符合条件的数据 |
| 500 | 服务器错误 | BigQuery 连接失败、数据处理错误 |

### 错误响应格式

```json
{
  "status": "error",
  "message": "具体错误信息"
}
```

### 常见错误和解决方案

#### 1. BigQuery 认证失败

**错误信息**:
```
"message": "Failed to authenticate with BigQuery: Could not automatically determine credentials"
```

**解决方案**:
1. 确认 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量已设置
2. 验证 JSON 密钥文件路径正确
3. 检查密钥文件是否有读权限

```bash
# Windows
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\credentials.json

# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# 验证
python -c "from google.cloud import bigquery; print(bigquery.Client())"
```

#### 2. 没有找到符合条件的论文

**错误信息**:
```
"message": "没有找到符合条件的论文"
```

**原因**: 指定的年份范围或其他条件过于严格

**解决方案**:
- 扩大年份范围
- 增加 `limit` 参数值
- 尝试不同的参数组合

#### 3. 超时错误

**原因**: BigQuery 查询时间过长

**解决方案**:
- 减少 `limit` 参数
- 缩小年份范围
- 使用 `kamada_kawai` 布局算法

---

## 数据格式规范

### 颜色代码（16进制）

论文引用网络按年份分配颜色：

| 年份 | 颜色 | 十六进制 |
|------|------|---------|
| 2020 | 🔴 红色 | #FF6B6B |
| 2021 | 🟠 橙色 | #FFA500 |
| 2022 | 🟡 黄色 | #FFD93D |
| 2023 | 🟢 绿色 | #6BCF7F |
| 2024 | 🔵 蓝色 | #4D96FF |
| 其他 | 🟣 紫色 | #9B59B6 |

### 布局坐标

- **范围**: [0, 1]
- **原点**: 左上角
- **缩放**: 乘以画布尺寸即可得到像素坐标

```javascript
// D3.js 中的使用示例
const x = node.x * width;
const y = node.y * height;
```

### 节点大小计算公式

**论文引用网络**:
```
size = 10 + min(50, citation_count / 10)
范围: [10, 60]
```

**作者协作网络**:
```
size = 10 + min(40, paper_count * 2)
范围: [10, 50]
```

### 网络密度公式

```
network_density = (2 * edge_count) / (node_count * (node_count - 1))
范围: [0, 1]
```

---

## 缓存说明

### 缓存策略

- **命中条件**: 相同的查询参数（year_min, year_max, limit）
- **缓存时间**: 24 小时（生产环境）/ 5 分钟（开发环境）
- **存储方式**: Redis（若启用）或内存

### 识别缓存

在响应中检查 `cached` 字段：
```json
{
  "cached": true,      // 从缓存返回
  "data": {...}
}
```

### 清除缓存

当前版本需要重启应用以清除内存缓存。如使用 Redis，可直接操作：

```bash
redis-cli FLUSHDB
```


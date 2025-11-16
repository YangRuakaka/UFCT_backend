# Networks API 规范文档 (LLM版)

## API总览

本系统提供两个核心网络分析API：
1. **论文引用网络API** - 分析论文间的引用关系
2. **作者协作网络API** - 分析作者间的协作关系

两个API都采用RESTful风格，支持GET请求，返回JSON格式数据。

---

## API 1: 论文引用网络

### 端点定义
```
GET /api/networks/citation
```

### 功能描述
获取论文引用网络的拓扑数据。通过分析论文间的引用关系，构建有向网络图，返回节点（论文）、边（引用关系）和网络统计指标。

### 请求参数规范

| 参数 | 类型 | 必需 | 默认 | 范围 | 含义 |
|------|------|------|------|------|------|
| year_min | int | N | 2020 | [1800, 2024] | 论文发表起始年份（含） |
| year_max | int | N | 2024 | [1800, 2024] | 论文发表终止年份（含） |
| limit | int | N | 500 | [1, 5000] | 返回的最大节点数 |
| university | str | N | null | - | 大学过滤：名称(如"MIT")或ID(如"I136199984") |
| discipline | str | N | null | - | 学科过滤：名称(如"Machine Learning")或ID(如"T10001") |
| min_citations | int | N | 0 | [0, ∞) | 论文最少被引用次数 |

### 请求示例
```
/api/networks/citation?year_min=2020&year_max=2023&limit=300&university=MIT&discipline=Machine%20Learning&min_citations=5
```

### 响应规范

#### 成功响应 (HTTP 200)
```json
{
  "status": "success",
  "data": {
    "network": {
      "nodes": [
        {
          "id": "W123456789",
          "label": "string(论文标题)",
          "node_type": "paper",
          "size": 20,
          "color": "#4ECDC4",
          "metadata": {
            "title": "论文完整标题",
            "year": 2023,
            "citation_count": 15,
            "venue": "NeurIPS 2023",
            "url": "https://openalex.org/W123456789"
          }
        }
      ],
      "edges": [
        {
          "source": "W123456789",
          "target": "W987654321",
          "edge_type": "cites",
          "weight": 1,
          "label": "引用关系",
          "metadata": {}
        }
      ],
      "metadata": {
        "total_nodes": 450,
        "total_edges": 1250,
        "network_density": 0.012,
        "avg_degree": 5.56
      }
    },
    "statistics": {
      "total_nodes": 450,
      "total_edges": 1250,
      "average_degree": 5.56,
      "density": 0.012,
      "diameter": 8,
      "average_clustering_coefficient": 0.45
    },
    "query_params": {
      "year_min": 2020,
      "year_max": 2024,
      "limit": 500,
      "university": "MIT",
      "university_id": "I136199984",
      "discipline": "Machine Learning",
      "discipline_id": "T10001",
      "min_citations": 0
    }
  },
  "cached": false,
  "timestamp": "2024-11-13T10:30:00Z"
}
```

#### 数据字段说明

**nodes数组**:
- id: OpenAlex论文ID (string)
- label: 论文标题 (string)
- node_type: 节点类型 (string, 为"paper")
- size: 可视化节点大小，基于被引用次数 (number)
- color: 节点颜色，基于发表年份 (string)
- metadata: 包含论文详细信息的对象

**edges数组**:
- source: 源论文ID (string)
- target: 被引用论文ID (string)
- weight: 边权重，通常为1 (number)

**statistics对象**:
- total_nodes: 网络节点总数 (int)
- total_edges: 网络边总数 (int)
- average_degree: 平均度数 (number)
- density: 网络密度，范围[0,1] (number)
- diameter: 网络直径，两点最大距离 (int)
- average_clustering_coefficient: 平均聚类系数 (number)

**query_params对象**:
- 返回用户输入的所有参数
- 若输入了名称，返回对应的OpenAlex ID

#### 错误响应

**404 - 未找到数据**
```json
{
  "status": "error",
  "message": "没有找到符合条件的论文"
}
```

**500 - 服务器错误**
```json
{
  "status": "error",
  "message": "error description"
}
```

---

## API 2: 作者协作网络

### 端点定义
```
GET /api/networks/collaboration
```

### 功能描述
获取作者协作网络的拓扑数据。通过分析作者间的共同发表论文关系，构建无向网络图，返回作者节点、协作关系、社区划分和网络统计指标。

### 请求参数规范

| 参数 | 类型 | 必需 | 默认 | 范围 | 含义 |
|------|------|------|------|------|------|
| year_min | int | N | 2020 | [1800, 2024] | 论文发表起始年份（含） |
| year_max | int | N | 2024 | [1800, 2024] | 论文发表终止年份（含） |
| limit | int | N | 500 | [1, 5000] | 返回的最大论文数限制 |
| min_collaborations | int | N | 1 | [1, ∞) | 作者最少出现在多少篇论文中 |
| university | str | N | null | - | 大学过滤：名称或ID |
| discipline | str | N | null | - | 学科过滤：名称或ID |

### 请求示例
```
/api/networks/collaboration?year_min=2020&year_max=2024&university=Stanford&min_collaborations=2&limit=500
```

### 响应规范

#### 成功响应 (HTTP 200)
```json
{
  "status": "success",
  "data": {
    "network": {
      "nodes": [
        {
          "id": "A123456789",
          "label": "Author Name",
          "collaborations": 25,
          "papers": 15,
          "h_index": 8,
          "size": 25,
          "community": 0
        }
      ],
      "edges": [
        {
          "source": "A123456789",
          "target": "A987654321",
          "weight": 5,
          "papers": ["W111", "W222", "W333", "W444", "W555"]
        }
      ]
    },
    "statistics": {
      "total_authors": 380,
      "total_collaborations": 920,
      "average_collaborators": 4.85,
      "density": 0.008,
      "communities_count": 12,
      "modularity": 0.52,
      "giant_component_size": 245
    },
    "communities": [
      {
        "id": 0,
        "size": 45,
        "main_authors": ["Author1", "Author2", "Author3"],
        "research_topics": ["Machine Learning", "Data Mining"]
      }
    ],
    "query_params": {
      "year_min": 2020,
      "year_max": 2024,
      "limit": 500,
      "min_collaborations": 1,
      "university": "Stanford",
      "university_id": "I182444752",
      "discipline": "Artificial Intelligence",
      "discipline_id": "T10002"
    }
  },
  "cached": false,
  "timestamp": "2024-11-13T10:30:00Z"
}
```

#### 数据字段说明

**nodes数组**:
- id: OpenAlex作者ID (string)
- label: 作者名称 (string)
- collaborations: 总协作次数 (int)
- papers: 论文发表数 (int)
- h_index: h-index指数 (int)
- size: 可视化节点大小 (number)
- community: 所属社区编号 (int)

**edges数组**:
- source: 作者A的ID (string)
- target: 作者B的ID (string)
- weight: 协作强度，即共同论文数 (int)
- papers: 共同发表的论文ID列表 (array<string>)

**statistics对象**:
- total_authors: 网络中的作者总数 (int)
- total_collaborations: 协作关系总数 (int)
- average_collaborators: 平均每位作者的协作者数 (number)
- density: 网络密度，范围[0,1] (number)
- communities_count: 检测到的社区数 (int)
- modularity: 模块度，社区划分质量指标，范围[-0.5, 1] (number)
- giant_component_size: 最大连通分量中的作者数 (int)

**communities数组**:
- id: 社区唯一编号 (int)
- size: 社区中的作者数 (int)
- main_authors: 该社区最重要的3位作者 (array<string>)
- research_topics: 该社区的主要研究方向 (array<string>)

#### 错误响应

**404 - 未找到数据**
```json
{
  "status": "error",
  "message": "未找到符合条件的作者数据"
}
```

**500 - 服务器错误**
```json
{
  "status": "error",
  "message": "error description"
}
```

---

## 通用规范

### HTTP状态码
| 代码 | 含义 | 触发条件 |
|------|------|---------|
| 200 | 成功 | 正常请求并获得数据 |
| 404 | 未找到 | 没有符合条件的数据 |
| 500 | 服务器错误 | 内部处理异常 |

### 参数解析规则

#### 大学/学科参数处理
- 输入可以是名称字符串或OpenAlex ID
- 系统会尝试自动识别和转换
- 若为名称，需进行URL编码（空格变%20）
- 响应中会返回解析结果和对应ID

### 缓存机制
- 相同查询参数的请求会使用缓存
- 响应的`cached`字段表示是否使用了缓存
- `timestamp`字段表示数据生成时间

### 数据特性说明

**网络特性指标**:
- **度数(Degree)**: 节点连接的边数
- **密度(Density)**: 实际边数/可能的最大边数，越高越密集
- **直径(Diameter)**: 网络中任意两点的最大最短路径长度
- **聚类系数(Clustering Coefficient)**: 节点邻居间的连接程度
- **模块度(Modularity)**: 社区划分的质量指标，>0.3表示有明显社区结构

**作者指标**:
- **H-index**: 作者有h篇论文被引用至少h次
- **Collaborations**: 与该作者合作过的不同作者数或合作论文数
- **Community**: 使用Louvain等社区检测算法的结果

---

## 集成指南

### Python调用示例
```python
import requests
import json

# 论文引用网络
citation_url = "http://api.example.com/api/networks/citation"
params = {
    'year_min': 2020,
    'year_max': 2024,
    'discipline': 'Machine Learning',
    'limit': 300
}
response = requests.get(citation_url, params=params)
data = response.json()

# 检查状态
if data['status'] == 'success':
    nodes = data['data']['network']['nodes']
    edges = data['data']['network']['edges']
    stats = data['data']['statistics']
else:
    print(f"Error: {data['message']}")

# 作者协作网络
collab_url = "http://api.example.com/api/networks/collaboration"
params = {
    'year_min': 2020,
    'year_max': 2024,
    'university': 'MIT',
    'min_collaborations': 2
}
response = requests.get(collab_url, params=params)
data = response.json()

if data['status'] == 'success':
    communities = data['data']['communities']
    for comm in communities:
        print(f"Community {comm['id']}: {len(comm['main_authors'])} main authors")
```

### JavaScript调用示例
```javascript
// 论文引用网络
const citationParams = new URLSearchParams({
  year_min: 2020,
  year_max: 2024,
  discipline: 'Machine Learning',
  limit: 300
});

fetch(`/api/networks/citation?${citationParams}`)
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      const { nodes, edges } = data.data.network;
      const stats = data.data.statistics;
      console.log(`Network has ${stats.total_nodes} nodes and ${stats.total_edges} edges`);
    }
  });

// 作者协作网络
const collabParams = new URLSearchParams({
  year_min: 2020,
  year_max: 2024,
  university: 'Stanford',
  min_collaborations: 1
});

fetch(`/api/networks/collaboration?${collabParams}`)
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      const communities = data.data.communities;
      console.log(`Found ${communities.length} communities`);
    }
  });
```

---

## 常见使用场景

### 场景1: 获取某学科高被引论文的引用网络
```
/api/networks/citation?discipline=Artificial%20Intelligence&min_citations=50&year_min=2020&year_max=2024&limit=200
```
**返回**: AI领域被引用至少50次的论文构成的引用网络

### 场景2: 分析某大学的科研协作生态
```
/api/networks/collaboration?university=MIT&year_min=2020&year_max=2024&limit=500
```
**返回**: MIT过去5年的作者协作网络及社区结构

### 场景3: 对比不同学科的引用模式
```
/api/networks/citation?discipline=Machine%20Learning&year_min=2023&year_max=2023&limit=300
```
然后对比另一个学科的数据

### 场景4: 识别关键作者和研究社区
```
/api/networks/collaboration?discipline=Natural%20Language%20Processing&min_collaborations=5&limit=300
```
**返回**: NLP领域高度活跃的作者及其社区组织

---

## 版本信息

- **API版本**: 1.0
- **发布日期**: 2024-11-13
- **最后更新**: 2024-11-13
- **维护者**: Backend Team

---

## 限制和约束

1. **时间范围**: 支持1800-2024年的数据
2. **节点限制**: citation API最多5000个论文节点，collaboration API基于论文数限制
3. **查询超时**: 单次请求可能需要数秒到数十秒
4. **缓存TTL**: 相同查询结果缓存保留时间为1小时
5. **并发限制**: 建议不超过10个并发请求

---

## 错误处理建议

1. 检查HTTP状态码，优先处理4xx和5xx错误
2. 检查JSON响应中的status字段
3. 对于404错误，考虑调整过滤条件
4. 对于500错误，可进行重试或上报
5. 记录所有错误响应的message字段便于调试

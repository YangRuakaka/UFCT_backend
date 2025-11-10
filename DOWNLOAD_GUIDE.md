# 使用 Hugging Face API 下载数据

## 方案 1: 使用新的 API 下载脚本（推荐）

### 步骤 1: 设置 HF_TOKEN 环境变量

#### Windows (cmd):
```batch
set HF_TOKEN=your_huggingface_token_here
python download_dataset_api.py
```

#### Windows (PowerShell):
```powershell
$env:HF_TOKEN="your_huggingface_token_here"
python download_dataset_api.py
```

#### Linux/Mac:
```bash
export HF_TOKEN=your_huggingface_token_here
python download_dataset_api.py
```

### 步骤 2: 获取 HF_TOKEN

1. 访问 https://huggingface.co/settings/tokens
2. 创建新的访问令牌（Token）
3. 复制令牌值

### 步骤 3: 查看下载进度

脚本会显示：
- ✓ 可用的数据 splits
- ✓ Parquet 文件列表
- 📊 逐个下载进度条
- ✓ 最后的完成统计

## 方案 2: 使用 curl 命令直接下载

### 查看可用的 splits:
```bash
curl -X GET \
  -H "Authorization: Bearer $HF_TOKEN" \
  "https://datasets-server.huggingface.co/splits?dataset=Northwestern-CSSI%2Fsciscinet-v2"
```

### 获取 Parquet 文件列表:
```bash
curl -X GET \
  -H "Authorization: Bearer $HF_TOKEN" \
  "https://huggingface.co/api/datasets/Northwestern-CSSI/sciscinet-v2/parquet/default"
```

### 获取特定行数据:
```bash
curl -X GET \
  -H "Authorization: Bearer $HF_TOKEN" \
  "https://datasets-server.huggingface.co/rows?dataset=Northwestern-CSSI%2Fsciscinet-v2&config=default&split=train&offset=0&length=100"
```

## 数据文件说明

SciSciNet-v2 包含以下主要 Parquet 文件：

- `hit_papers_level0.parquet` - 论文基础信息（级别0）
- `hit_papers_level1.parquet` - 论文详细信息（级别1）
- `normalized_citations_level0.parquet` - 引用关系（级别0）
- `normalized_citations_level1.parquet` - 引用关系（级别1）
- `sciscinet_authors.parquet` - 作者信息
- `sciscinet_author_details.parquet` - 作者详细信息
- `sciscinet_affiliations.parquet` - 机构信息
- `sciscinet_affl_assoc_affl.parquet` - 机构关联信息
- `sciscinet_fields.parquet` - 研究领域信息

## 转换 Parquet 为 CSV

下载完成后，可以将 Parquet 文件转换为 CSV：

```python
from download_dataset_api import HFDatasetAPIFetcher
from config import Config

fetcher = HFDatasetAPIFetcher(local_dir=Config.HF_DATASET_LOCAL_DIR)
fetcher.convert_parquets_to_csv(sample_size=None)  # None = 全部转换
```

或只转换样本数据：
```python
fetcher.convert_parquets_to_csv(sample_size=1000)  # 只转换前 1000 行
```

## 故障排除

### 错误: 401 Unauthorized
- ✗ 问题: HF_TOKEN 无效或未设置
- ✓ 解决: 确认 token 有效且已设置环境变量

### 错误: 网络超时
- ✓ 解决: 重新运行脚本（支持断点续传）

### 数据不完整
- ✓ 查看日志确认所有文件是否下载完成
- ✓ 重新运行脚本会从上次中断处继续

## 注意事项

1. **数据量很大**：SciSciNet-v2 总大小可能超过 100GB
2. **需要网络连接**：必须保持网络连接直到下载完成
3. **磁盘空间**：确保有足够的磁盘空间存储数据
4. **时间**：根据网络速度，下载可能需要数小时

## 更新数据获取模块

下载完成后，更新 `data_fetcher.py` 以使用本地的 Parquet 文件：

```python
def load_parquet(self, filename: str) -> pd.DataFrame:
    """加载 Parquet 文件"""
    filepath = Path(self.local_dir) / filename
    if filepath.exists():
        return pd.read_parquet(filepath)
    return pd.DataFrame()
```

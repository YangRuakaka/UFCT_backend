#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用 Hugging Face Datasets API 下载 SciSciNet-v2 数据集
直接从 API 下载，无需本地认证
"""
import os
import sys
import logging
import requests
import pandas as pd
from pathlib import Path
from typing import Optional
from config import Config
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HFDatasetAPIFetcher:
    """使用 Hugging Face API 获取数据"""
    
    BASE_URL = "https://datasets-server.huggingface.co"
    PARQUET_URL = "https://huggingface.co/api/datasets"
    
    def __init__(self, 
                 repo_id: str = "Northwestern-CSSI/sciscinet-v2",
                 local_dir: str = None,
                 hf_token: Optional[str] = None):
        """
        初始化 API 获取器
        
        Args:
            repo_id: Hugging Face 数据集仓库 ID
            local_dir: 本地保存目录
            hf_token: Hugging Face API token（从环境变量或参数获取）
        """
        self.repo_id = repo_id
        self.local_dir = local_dir or Config.HF_DATASET_LOCAL_DIR
        self.hf_token = hf_token or os.getenv("HF_TOKEN", "")
        
        # 创建本地目录
        Path(self.local_dir).mkdir(parents=True, exist_ok=True)
        
        self.headers = {}
        if self.hf_token:
            self.headers["Authorization"] = f"Bearer {self.hf_token}"
    
    def get_splits(self) -> list:
        """获取数据集的 split 列表"""
        url = f"{self.BASE_URL}/splits?dataset={self.repo_id}"
        
        logger.info(f"获取数据集 splits...")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            splits = [s["split"] for s in data.get("splits", [])]
            
            logger.info(f"✓ 可用的 splits: {splits}")
            return splits
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ 获取 splits 失败: {e}")
            if response.status_code == 401:
                logger.error("  → 需要有效的 HF_TOKEN 环境变量")
            return []
    
    def get_parquet_files(self, config: str = "default") -> dict:
        """获取 Parquet 文件列表"""
        url = f"{self.PARQUET_URL}/{self.repo_id}/parquet/{config}"
        
        logger.info(f"获取 Parquet 文件列表...")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✓ 获取到 {len(data)} 个文件")
            
            return data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ 获取 Parquet 文件失败: {e}")
            if response.status_code == 401:
                logger.error("  → 需要有效的 HF_TOKEN 环境变量")
            return {}
    
    def download_parquet(self, url: str, filename: str, chunk_size: int = 8192) -> bool:
        """下载单个 Parquet 文件"""
        filepath = Path(self.local_dir) / filename
        
        logger.info(f"下载: {filename}")
        
        try:
            response = requests.get(url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            logger.info(f"✓ 下载成功: {filename} ({total_size / 1024 / 1024:.2f} MB)")
            return True
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ 下载失败 {filename}: {e}")
            if response.status_code == 401:
                logger.error("  → 需要有效的 HF_TOKEN 环境变量")
            if filepath.exists():
                filepath.unlink()
            return False
    
    def download_all_parquets(self, config: str = "default"):
        """下载所有 Parquet 文件"""
        parquet_files = self.get_parquet_files(config)
        
        if not parquet_files:
            logger.error("没有找到 Parquet 文件")
            return False
        
        logger.info(f"将下载 {len(parquet_files)} 个文件到: {self.local_dir}")
        logger.info("=" * 60)
        
        success_count = 0
        for idx, file_info in enumerate(parquet_files, 1):
            filename = file_info.get("filename", "")
            url = file_info.get("url", "")
            
            if not filename or not url:
                continue
            
            logger.info(f"[{idx}/{len(parquet_files)}] {filename}")
            
            if self.download_parquet(url, filename):
                success_count += 1
            
            logger.info("")
        
        logger.info("=" * 60)
        logger.info(f"✓ 下载完成: {success_count}/{len(parquet_files)} 个文件")
        
        return success_count == len(parquet_files)
    
    def convert_parquets_to_csv(self, sample_size: Optional[int] = None):
        """将 Parquet 文件转换为 CSV（可选）"""
        logger.info("转换 Parquet 为 CSV...")
        
        parquet_files = list(Path(self.local_dir).glob("*.parquet"))
        
        if not parquet_files:
            logger.warning("没有找到 Parquet 文件")
            return
        
        for pq_file in parquet_files:
            csv_file = pq_file.with_suffix(".csv")
            
            try:
                logger.info(f"转换: {pq_file.name} → {csv_file.name}")
                
                df = pd.read_parquet(pq_file)
                
                if sample_size:
                    df = df.head(sample_size)
                    logger.info(f"  (采样 {len(df)} 行)")
                
                df.to_csv(csv_file, index=False)
                logger.info(f"✓ 转换成功: {csv_file.name}")
                
            except Exception as e:
                logger.error(f"✗ 转换失败: {e}")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("SciSciNet-v2 数据集下载 (使用 API)")
    logger.info("=" * 60)
    
    # 检查 HF_TOKEN
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        logger.warning("⚠ 未设置 HF_TOKEN 环境变量")
        logger.warning("  需要运行: set HF_TOKEN=your_token_here")
        logger.warning("")
    
    # 创建获取器
    fetcher = HFDatasetAPIFetcher(
        local_dir=Config.HF_DATASET_LOCAL_DIR,
        hf_token=hf_token
    )
    
    # 获取 splits
    fetcher.get_splits()
    
    logger.info("")
    logger.info("开始下载数据...")
    logger.info("=" * 60)
    
    # 下载所有 Parquet 文件
    success = fetcher.download_all_parquets()
    
    if success:
        logger.info("✓ 所有文件下载成功！")
        
        # 询问是否转换为 CSV
        logger.info("")
        logger.info("提示: 你也可以选择转换 Parquet 为 CSV 格式")
        logger.info("调用: fetcher.convert_parquets_to_csv()")
    else:
        logger.error("✗ 部分文件下载失败")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

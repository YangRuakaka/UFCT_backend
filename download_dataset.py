#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hugging Face SciSciNet-v2 数据集下载脚本
自动下载并初始化本地数据集
"""
import os
import sys
import logging
from pathlib import Path
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """下载数据集"""
    logger.info("=" * 60)
    logger.info("SciSciNet-v2 数据集下载")
    logger.info("=" * 60)
    
    # 初始化 fetcher（会自动下载数据集）
    try:
        from data.data_fetcher import HFDatasetFetcher
        
        logger.info(f"目标目录: {Config.HF_DATASET_LOCAL_DIR}")
        
        fetcher = HFDatasetFetcher(local_dir=Config.HF_DATASET_LOCAL_DIR)
        
        # 触发下载
        logger.info("正在下载数据集...")
        fetcher._ensure_downloaded()
        
        logger.info("✓ 数据集下载成功！")
        logger.info(f"✓ 数据存储于: {Config.HF_DATASET_LOCAL_DIR}")
        
        # 列出下载的文件
        data_dir = Path(Config.HF_DATASET_LOCAL_DIR)
        if data_dir.exists():
            files = list(data_dir.glob("*.csv"))
            logger.info(f"✓ 数据文件数量: {len(files)}")
            for f in files:
                logger.info(f"  - {f.name}")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ 下载失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

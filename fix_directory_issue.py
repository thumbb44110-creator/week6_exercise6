#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復目錄建立問題的快速解決方案
"""

import os
import shutil
from pathlib import Path

def fix_directory_issue():
    """修復 data 目錄問題"""
    print("🔧 修復目錄建立問題")
    print("=" * 50)
    
    # 檢查 data 目錄狀況
    data_path = Path("data")
    
    print(f"檢查 {data_path} 狀況:")
    
    if data_path.exists():
        if data_path.is_file():
            print(f"⚠️ 發現同名檔案，正在刪除...")
            data_path.unlink()
            print(f"✅ 已刪除檔案: {data_path}")
        elif data_path.is_dir():
            print(f"✅ 目錄已存在: {data_path}")
            # 列出目錄內容
            try:
                contents = list(data_path.iterdir())
                print(f"   內容: {len(contents)} 個項目")
                for item in contents[:5]:  # 只顯示前5個
                    print(f"     - {item.name}")
                if len(contents) > 5:
                    print(f"     ... 還有 {len(contents)-5} 個項目")
            except Exception as e:
                print(f"   無法讀取目錄內容: {e}")
        else:
            print(f"❌ 未知檔案類型")
    else:
        print(f"✅ 目錄不存在，將建立...")
        data_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 已建立目錄: {data_path}")
    
    print()
    print("🚀 現在可以重新執行 Cell 11")
    print("請重新執行 cell11_with_auto_download.py 中的 main_cell11_auto_download() 函數")
    
    return True

if __name__ == "__main__":
    fix_directory_issue()

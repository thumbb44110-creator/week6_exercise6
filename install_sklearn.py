#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安裝 scikit-learn for Jupyter Notebook
"""

import sys
import subprocess

def install_sklearn():
    """安裝 scikit-learn"""
    try:
        import sklearn
        print("scikit-learn 已安裝")
        print(f"版本: {sklearn.__version__}")
        return True
    except ImportError:
        print("正在安裝 scikit-learn...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn"])
            print("scikit-learn 安裝成功")
            return True
        except Exception as e:
            print(f"安裝失敗: {e}")
            return False

if __name__ == "__main__":
    success = install_sklearn()
    if success:
        print("現在可以在 Jupyter Notebook 中使用 sklearn 了")
    else:
        print("安裝失敗，請手動安裝")

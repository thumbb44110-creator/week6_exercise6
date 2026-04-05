# 在 Jupyter Notebook 中安裝 pykrige
import sys
import subprocess

def install_package(package):
    """在當前 Python 環境中安裝套件"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 安裝 pykrige
install_package('pykrige')
print("pykrige 安裝完成！")

# 測試安裝
try:
    from pykrige.ok import OrdinaryKriging
    print("✅ pykrige 導入成功！")
    print(f"pykrige 版本: {OrdinaryKriging.__module__}")
except ImportError as e:
    print(f"❌ 導入失敗: {e}")

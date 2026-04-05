# 檢查實際檔案路徑

import os
from pathlib import Path

print("檢查檔案路徑...")
print("=" * 50)

# 檢查當前工作目錄
current_dir = os.getcwd()
print(f"當前工作目錄: {current_dir}")

# 檢查基礎目錄
base_dir = Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6")
print(f"基礎目錄: {base_dir}")
print(f"基礎目錄存在: {base_dir.exists()}")

# 檢查 data 目錄
data_dir = base_dir / "data"
print(f"data 目錄: {data_dir}")
print(f"data 目錄存在: {data_dir.exists()}")

if data_dir.exists():
    print(f"data 目錄內容:")
    try:
        for item in data_dir.iterdir():
            print(f"  {item.name} ({item.stat().st_size} bytes)")
    except Exception as e:
        print(f"  無法列出內容: {e}")

# 檢查柵格檔案
print(f"\n柵格檔案檢查:")
raster_files = ['kriging_rainfall.tif', 'kriging_variance.tif', 'rf_rainfall.tif']
for filename in raster_files:
    filepath = base_dir / filename
    print(f"  {filename}: {filepath.exists()} ({filepath.stat().st_size if filepath.exists() else 0} bytes)")

# 檢查 Shapefile 檔案
print(f"\nShapefile 檔案檢查:")
shp_files = ['TOWN_MOI.shp', 'TOWN_MOI.shx', 'TOWN_MOI.dbf', 'TOWN_MOI.prj']
for filename in shp_files:
    filepath = data_dir / filename
    print(f"  {filename}: {filepath.exists()} ({filepath.stat().st_size if filepath.exists() else 0} bytes)")

# 嘗試不同的可能路徑
print(f"\n嘗試其他可能路徑:")
possible_paths = [
    Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6\data\TOWN_MOI.shp"),
    Path(r"D:\114學年\遙測\windsurf_project\week6\data\TOWN_MOI.shp"),
    Path(r"D:\114學年\遙測\windsurf_project\data\TOWN_MOI.shp"),
    Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6\TOWN_MOI.shp"),
]

for path in possible_paths:
    print(f"  {path}: {path.exists()}")

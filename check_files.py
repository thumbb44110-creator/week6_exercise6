from pathlib import Path

# 檢查 data 目錄
data_dir = Path("data")
print(f"檢查目錄: {data_dir}")
print(f"目錄存在: {data_dir.exists()}")

if data_dir.exists():
    files = list(data_dir.glob("*"))
    print(f"目錄內容: {len(files)} 個檔案")
    
    for file_path in files:
        size = file_path.stat().st_size
        print(f"  {file_path.name}: {size:,} bytes")
else:
    print("目錄不存在")

# 檢查當前目錄
current_dir = Path(".")
print(f"\n當前目錄: {current_dir.absolute()}")
current_files = [f for f in current_dir.glob("TOWN_MOI.*")]
print(f"當前目錄中的 TOWN_MOI 檔案: {len(current_files)} 個")

for file_path in current_files:
    size = file_path.stat().st_size
    print(f"  {file_path.name}: {size:,} bytes")

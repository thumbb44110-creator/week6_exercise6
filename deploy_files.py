import os
import zipfile
import shutil
from pathlib import Path

# 檢查下載檔案
zip_path = Path(r"C:\Users\User\Downloads\OFiles_9e222fea-bafb-4436-9b17-10921abc6ef2.zip")
print(f"檢查下載檔案: {zip_path}")

if zip_path.exists():
    size = zip_path.stat().st_size
    print(f"檔案大小: {size:,} bytes ({size/1024/1024:.1f} MB)")
    
    # 建立臨時目錄
    temp_dir = Path("temp_extract")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # 解壓縮檔案
    print("解壓縮檔案...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        print(f"ZIP 包含 {len(file_list)} 個檔案")
        
        # 解壓縮所有檔案
        zip_ref.extractall(temp_dir)
    
    # 尋找 Shapefile 檔案
    print("尋找 Shapefile 檔案...")
    shapefile_files = {}
    
    for file_path in temp_dir.rglob("*"):
        if file_path.is_file():
            filename = file_path.name.upper()
            
            if filename.startswith("TOWN") and filename.endswith((".SHP", ".SHX", ".DBF", ".PRJ")):
                shapefile_files[file_path.suffix.upper()] = file_path
                print(f"  找到: {file_path.name}")
    
    # 建立 data 目錄
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # 複製檔案
    print("部署檔案到 data 目錄...")
    deployed_count = 0
    
    for ext, file_path in shapefile_files.items():
        target_filename = f"TOWN_MOI{ext}"
        target_path = data_dir / target_filename
        
        shutil.copy2(file_path, target_path)
        size = target_path.stat().st_size
        print(f"  部署: {target_filename} ({size:,} bytes)")
        deployed_count += 1
    
    # 清理臨時檔案
    shutil.rmtree(temp_dir)
    print(f"清理臨時目錄: {temp_dir}")
    
    print(f"\n部署完成: {deployed_count} 個檔案")
    
    # 驗證檔案
    print("\n驗證部署的檔案...")
    required_files = ["TOWN_MOI.shp", "TOWN_MOI.shx", "TOWN_MOI.dbf", "TOWN_MOI.prj"]
    
    for filename in required_files:
        file_path = data_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  OK {filename}: {size:,} bytes")
        else:
            print(f"  FAIL {filename}: 檔案不存在")
    
    print("\n部署完成！現在可以執行 Cell 11。")
    
else:
    print("下載檔案不存在！")

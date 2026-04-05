# 複製鄉鎮邊界檔案

import shutil
from pathlib import Path

def copy_township_files():
    """複製鄉鎮邊界檔案到 data 目錄"""
    
    # 來源和目標目錄
    source_dir = Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6")
    target_dir = source_dir / "data"
    
    # 確保目標目錄存在
    target_dir.mkdir(exist_ok=True)
    
    # 檔案清單
    files_to_copy = [
        "TOWN_MOI.shp",
        "TOWN_MOI.shx", 
        "TOWN_MOI.dbf",
        "TOWN_MOI.prj"
    ]
    
    print("複製鄉鎮邊界檔案...")
    print(f"來源: {source_dir}")
    print(f"目標: {target_dir}")
    
    copied_count = 0
    
    for filename in files_to_copy:
        source_file = source_dir / filename
        target_file = target_dir / filename
        
        if source_file.exists():
            try:
                shutil.copy2(source_file, target_file)
                print(f"OK {filename} ({source_file.stat().st_size} bytes)")
                copied_count += 1
            except Exception as e:
                print(f"ERROR {filename} - {e}")
        else:
            print(f"MISSING {filename} - 來源檔案不存在")
    
    print(f"\n複製完成: {copied_count}/{len(files_to_copy)} 個檔案")
    
    # 驗證結果
    print(f"\n驗證目標目錄:")
    for filename in files_to_copy:
        target_file = target_dir / filename
        status = "存在" if target_file.exists() else "不存在"
        size = target_file.stat().st_size if target_file.exists() else 0
        print(f"  {filename}: {status} ({size} bytes)")

if __name__ == "__main__":
    copy_township_files()

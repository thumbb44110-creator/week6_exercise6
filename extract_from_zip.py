# 直接從 ZIP 檔案提取鄉鎮邊界

import zipfile
import shutil
from pathlib import Path

def extract_from_zip():
    """從下載的 ZIP 檔案提取鄉鎮邊界"""
    
    # ZIP 檔案路徑
    zip_path = Path(r"C:\Users\User\Downloads\OFiles_9e222fea-bafb-4436-9b17-10921abc6ef2.zip")
    target_dir = Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6\data")
    
    print("從 ZIP 檔案提取鄉鎮邊界...")
    print(f"ZIP 檔案: {zip_path}")
    print(f"目標目錄: {target_dir}")
    
    if not zip_path.exists():
        print(f"ERROR: ZIP 檔案不存在: {zip_path}")
        return False
    
    # 確保目標目錄存在
    target_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 列出 ZIP 內容
            print(f"\nZIP 檔案內容:")
            file_list = zip_ref.namelist()
            for file in file_list:
                print(f"  {file}")
            
            # 尋找並提取 TOWN_MOI 檔案
            town_files = [f for f in file_list if 'TOWN_MOI' in f and f.endswith(('.shp', '.shx', '.dbf', '.prj'))]
            
            print(f"\n找到的鄉鎮檔案: {len(town_files)}")
            
            extracted_count = 0
            for file_info in town_files:
                try:
                    # 提取檔案
                    with zip_ref.open(file_info) as source:
                        # 獲取檔案名稱（去掉路徑）
                        filename = Path(file_info).name
                        target_path = target_dir / filename
                        
                        # 寫入目標檔案
                        with open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                        
                        print(f"EXTRACTED {filename} ({target_path.stat().st_size} bytes)")
                        extracted_count += 1
                        
                except Exception as e:
                    print(f"ERROR extracting {file_info}: {e}")
            
            print(f"\n提取完成: {extracted_count} 個檔案")
            
            # 驗證提取結果
            print(f"\n驗證提取結果:")
            shp_files = ['TOWN_MOI.shp', 'TOWN_MOI.shx', 'TOWN_MOI.dbf', 'TOWN_MOI.prj']
            
            for filename in shp_files:
                target_path = target_dir / filename
                if target_path.exists():
                    size = target_path.stat().st_size
                    print(f"  {filename}: OK ({size} bytes)")
                else:
                    print(f"  {filename}: MISSING")
            
            return extracted_count > 0
            
    except Exception as e:
        print(f"ERROR: 無法處理 ZIP 檔案: {e}")
        return False

if __name__ == "__main__":
    success = extract_from_zip()
    if success:
        print("\n鄉鎮邊界檔案提取成功！")
    else:
        print("\n鄉鎮邊界檔案提取失敗！")

# 測試 NLSC 鄉鎮邊界下載功能

import numpy as np
import warnings
import pandas as pd
import os
import requests
import zipfile
import io
import time
from pathlib import Path
warnings.filterwarnings('ignore')

def safe_mkdir(path):
    """安全建立目錄，處理檔案/目錄衝突"""
    path = Path(path)
    
    if path.exists():
        if path.is_file():
            print(f"⚠️ 發現同名檔案 {path}，正在刪除...")
            path.unlink()
            path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"✅ 目錄已存在: {path}")
    else:
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 建立目錄: {path}")
    
    return path

def test_nlsc_download():
    """測試 NLSC 下載功能"""
    print("🧪 測試 NLSC 鄉鎮邊界下載功能")
    print("=" * 50)
    
    # 安全建立目標目錄
    target_path = safe_mkdir("test_download")
    
    # 檢查是否已存在檔案
    township_files = [
        target_path / "TOWN_MOI.shp",
        target_path / "TOWN_MOI.shx", 
        target_path / "TOWN_MOI.dbf",
        target_path / "TOWN_MOI.prj"
    ]
    
    existing_files = [f for f in township_files if f.exists()]
    all_files_exist = len(existing_files) == len(township_files)
    
    if all_files_exist:
        print(f"✅ 所有鄉鎮邊界檔案已存在:")
        for f in existing_files:
            print(f"    {f.name}")
            print(f"    大小: {f.stat().st_size} bytes")
        print(f"  跳過下載，驗證現有檔案...")
        return validate_downloaded_files(target_path)
    
    print(f"❌ 未發現完整檔案，開始下載測試...")
    print(f"  現有檔案: {len(existing_files)} 個")
    for f in existing_files:
        print(f"    {f.name}")
    
    # NLSC 下載 URL 模式測試
    print("\n🔍 開始 NLSC 下載端點測試...")
    
    download_candidates = [
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1437",
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1436", 
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1435",
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1434",
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1433",
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1428",
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1427",
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1426",
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1425",
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1400",
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1401",
        "https://whgis-nlsc.moi.gov.tw/DownlaodFiles.ashx?oid=1402",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    successful_download = None
    
    for i, url in enumerate(download_candidates, 1):
        print(f"\n測試 {i}/{len(download_candidates)}: {url}")
        
        try:
            print(f"  📡 發送請求...")
            response = session.get(url, timeout=30, stream=True)
            
            print(f"  📊 回應狀態: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = response.headers.get('content-length', '0')
                
                print(f"  📄 內容類型: {content_type}")
                print(f"  📏 內容長度: {int(content_length)/1024:.1f} KB")
                
                if int(content_length) > 1024:
                    print(f"  📥 開始下載...")
                    
                    file_content = b''
                    downloaded_size = 0
                    start_time = time.time()
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file_content += chunk
                            downloaded_size += len(chunk)
                            # 顯示進度
                            if downloaded_size % (100*1024) == 0:
                                elapsed = time.time() - start_time
                                speed = downloaded_size / elapsed / 1024
                                print(f"      已下載: {downloaded_size/1024:.1f} KB (速度: {speed:.1f} KB/s)")
                    
                    download_time = time.time() - start_time
                    print(f"  ✅ 下載完成: {downloaded_size/1024:.1f} KB")
                    print(f"  ⏱️ 下載時間: {download_time:.1f} 秒")
                    print(f"  🚀 平均速度: {downloaded_size/download_time/1024:.1f} KB/s")
                    
                    # 測試 ZIP 解壓縮
                    print(f"  📦 測試 ZIP 解壓縮...")
                    try:
                        with zipfile.ZipFile(io.BytesIO(file_content)) as zip_file:
                            file_list = zip_file.namelist()
                            print(f"    壓縮檔包含: {len(file_list)} 個檔案")
                            
                            # 檢查是否包含鄉鎮邊界檔案
                            shp_files = [f for f in file_list if f.upper().endswith('.SHP')]
                            dbf_files = [f for f in file_list if f.upper().endswith('.DBF')]
                            shx_files = [f for f in file_list if f.upper().endswith('.SHX')]
                            prj_files = [f for f in file_list if f.upper().endswith('.PRJ')]
                            
                            print(f"    SHP 檔案: {len(shp_files)} 個")
                            print(f"    DBF 檔案: {len(dbf_files)} 個")
                            print(f"    SHX 檔案: {len(shx_files)} 個")
                            print(f"    PRJ 檔案: {len(prj_files)} 個")
                            
                            has_township_files = any(
                                'TOWN' in filename.upper() or 'TOWN' in filename.upper()
                                for filename in file_list
                            )
                            
                            if has_township_files and len(shp_files) > 0:
                                print(f"    🎯 找到鄉鎮邊界檔案!")
                                
                                # 解壓縮檔案
                                extracted_files = []
                                for filename in file_list:
                                    if any(ext in filename.upper() for ext in ['.SHP', '.SHX', '.DBF', '.PRJ']):
                                        try:
                                            zip_file.extract(filename, target_path)
                                            extracted_files.append(filename)
                                            print(f"      ✅ 解壓縮: {filename}")
                                        except Exception as e:
                                            print(f"      ❌ 解壓縮失敗 {filename}: {e}")
                                
                                successful_download = url
                                print(f"    🎉 成功下載並解壓縮!")
                                print(f"    📁 解壓縮檔案: {len(extracted_files)} 個")
                                break
                            else:
                                print(f"    ⚠️ 不是鄉鎮邊界檔案")
                                print(f"    📋 檔案列表: {file_list[:5]}...")  # 顯示前5個檔案
                    
                    except zipfile.BadZipFile:
                        print(f"    ❌ 不是有效的 ZIP 檔案")
                    
                    except Exception as e:
                        print(f"    ❌ 解壓縮失敗: {e}")
                
                else:
                    print(f"    ⚠️ 檔案太小，可能不是目標檔案")
            
            else:
                print(f"    ❌ HTTP 錯誤: {response.status_code}")
                if response.status_code == 404:
                    print(f"      檔案不存在")
                elif response.status_code == 403:
                    print(f"      存取被拒絕")
                elif response.status_code == 500:
                    print(f"      伺服器錯誤")
        
        except requests.exceptions.Timeout:
            print(f"    ⏰ 請求逾時")
        
        except requests.exceptions.ConnectionError:
            print(f"    🌐 連線錯誤")
        
        except requests.exceptions.RequestException as e:
            print(f"    ❌ 請求錯誤: {e}")
        
        except Exception as e:
            print(f"    ❌ 其他錯誤: {e}")
        
        # 短暫延遲避免被阻擋
        time.sleep(0.5)
        
        if successful_download:
            break
    
    # 測試結果
    if successful_download:
        print(f"\n🎉 下載測試成功!")
        print(f"   成功 URL: {successful_download}")
        print(f"   目錄: {target_path.absolute()}")
        
        return validate_downloaded_files(target_path)
    else:
        print(f"\n❌ 下載測試失敗")
        print(f"   所有 URL 都無法下載鄉鎮邊界檔案")
        return False

def validate_downloaded_files(target_path):
    """驗證下載的檔案"""
    print("\n🔍 驗證下載的檔案")
    print("=" * 30)
    
    township_files = {
        'TOWN_MOI.shp': '主檔案',
        'TOWN_MOI.shx': '索引檔案',
        'TOWN_MOI.dbf': '屬性檔案',
        'TOWN_MOI.prj': '座標系統檔案'
    }
    
    all_valid = True
    
    for filename, description in township_files.items():
        file_path = target_path / filename
        
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {filename}: {size} bytes ({description})")
            
            # 檢查檔案大小是否合理
            if size < 100:
                print(f"  ⚠️ 檔案大小異常小")
                all_valid = False
            elif filename.endswith('.shp') and size > 100000000:  # 100MB
                print(f"  ⚠️ 檔案大小異常大")
                all_valid = False
        else:
            print(f"❌ {filename}: 檔案不存在 ({description})")
            all_valid = False
    
    # 嘗試載入 Shapefile
    if all_valid:
        try:
            import geopandas as gpd
            shp_path = target_path / "TOWN_MOI.shp"
            gdf = gpd.read_file(shp_path)
            
            print(f"\n📊 Shapefile 驗證:")
            print(f"  總圖層數: {len(gdf)}")
            print(f"  座標系統: {gdf.crs}")
            print(f"  欄位數量: {len(gdf.columns)}")
            print(f"  主要欄位: {list(gdf.columns)[:5]}")
            
            # 檢查是否包含花蓮縣和宜蘭縣
            if 'COUNTYNAME' in gdf.columns:
                counties = gdf['COUNTYNAME'].unique()
                has_hualien = '花蓮縣' in counties
                has_yilan = '宜蘭縣' in counties
                
                print(f"\n🎯 目標縣市檢查:")
                print(f"  花蓮縣: {'✅' if has_hualien else '❌'}")
                print(f"  宜蘭縣: {'✅' if has_yilan else '❌'}")
                
                if has_hualien and has_yilan:
                    target_towns = gdf[gdf['COUNTYNAME'].isin(['花蓮縣', '宜蘭縣'])]
                    print(f"  目標鄉鎮數: {len(target_towns)}")
                    print(f"  花蓮縣鄉鎮: {len(gdf[gdf['COUNTYNAME'] == '花蓮縣'])}")
                    print(f"  宜蘭縣鄉鎮: {len(gdf[gdf['COUNTYNAME'] == '宜蘭縣'])}")
                    
                    print(f"\n🎉 完整驗證通過!")
                    return True
                else:
                    print(f"  ⚠️ 缺少目標縣市")
                    all_valid = False
            else:
                print(f"  ⚠️ 沒有 COUNTYNAME 欄位")
                all_valid = False
        
        except ImportError:
            print(f"\n⚠️ 無法驗證 Shapefile (缺少 geopandas)")
        except Exception as e:
            print(f"\n❌ Shapefile 驗證失敗: {e}")
            all_valid = False
    
    if all_valid:
        print(f"\n✅ 檔案驗證通過!")
    else:
        print(f"\n❌ 檔案驗證失敗!")
    
    return all_valid

def cleanup_test_files():
    """清理測試檔案"""
    print("\n🧹 清理測試檔案")
    print("=" * 20)
    
    test_dir = Path("test_download")
    if test_dir.exists():
        try:
            import shutil
            shutil.rmtree(test_dir)
            print(f"✅ 已刪除測試目錄: {test_dir}")
        except Exception as e:
            print(f"❌ 清理失敗: {e}")
    else:
        print(f"✅ 測試目錄不存在")

# 執行測試
if __name__ == "__main__":
    print("🧪 NLSC 鄉鎮邊界下載功能測試")
    print("=" * 60)
    
    try:
        success = test_nlsc_download()
        
        if success:
            print("\n🎉 測試完成 - 下載功能正常!")
        else:
            print("\n❌ 測試失敗 - 下載功能有問題!")
        
        # 詢問是否清理檔案
        print("\n❓ 是否要清理測試檔案? (y/n)")
        # cleanup_test_files()  # 取消註解來清理檔案
        
    except Exception as e:
        print(f"\n💥 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

else:
    print("🧪 下載測試模組已載入")
    print("使用 test_nlsc_download() 執行測試")

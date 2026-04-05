# Lab 2 Cell 11: Zonal Statistics — Township Decision Table (無模擬版)
# 整合 NLSC 網站自動下載鄉鎮邊界檔案功能，僅使用真實資料

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

# 檢查必要函式庫
try:
    from rasterstats import zonal_stats
    import geopandas as gpd
    import rasterio
    from shapely.geometry import Point, Polygon
    print("✅ 所有必要函式庫可用")
except ImportError as e:
    print(f"❌ 缺少函式庫: {e}")
    print("請安裝: pip install rasterstats geopandas pandas rasterio requests")
    raise

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

def download_township_boundaries_nlsc(target_dir="data", force_download=False):
    """從 NLSC 網站自動下載鄉鎮邊界檔案"""
    print("\n" + "=" * 60)
    print("🌐 從 NLSC 網站下載鄉鎮邊界檔案")
    print("=" * 60)
    
    # 安全建立目標目錄
    target_path = safe_mkdir(target_dir)
    
    # 檢查是否已存在檔案
    township_files = [
        target_path / "TOWN_MOI.shp",
        target_path / "TOWN_MOI.shx", 
        target_path / "TOWN_MOI.dbf",
        target_path / "TOWN_MOI.prj"
    ]
    
    existing_files = [f for f in township_files if f.exists()]
    
    # 檢查是否所有必要檔案都存在
    all_files_exist = len(existing_files) == len(township_files)
    
    if all_files_exist and not force_download:
        print(f"✅ 所有鄉鎮邊界檔案已存在:")
        for f in existing_files:
            print(f"    {f.name}")
        print(f"  跳過下載，直接使用現有檔案進行後續作業")
        return True
    
    elif existing_files and not force_download:
        print(f"⚠️ 部分鄉鎮邊界檔案存在:")
        for f in existing_files:
            print(f"    {f.name}")
        missing_files = [f for f in township_files if not f.exists()]
        print(f"  缺失檔案: {[f.name for f in missing_files]}")
        print(f"  將嘗試下載缺失檔案...")
    else:
        print(f"❌ 未發現鄉鎮邊界檔案")
        print(f"  將嘗試完整下載...")
    
    # NLSC 下載 URL 模式測試
    print("🔍 測試 NLSC 下載端點...")
    
    # 基於網站分析的潛在下載 URL
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
        print(f"  測試 {i}/{len(download_candidates)}: {url}")
        
        try:
            response = session.get(url, timeout=30, stream=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = response.headers.get('content-length', '0')
                
                print(f"    ✅ 狀態: {response.status_code}")
                print(f"    📄 類型: {content_type}")
                print(f"    📏 大小: {int(content_length)/1024:.1f} KB")
                
                if int(content_length) > 1024:
                    print(f"    📥 開始下載...")
                    
                    file_content = b''
                    downloaded_size = 0
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file_content += chunk
                            downloaded_size += len(chunk)
                            if downloaded_size % (100*1024) == 0:
                                print(f"      已下載: {downloaded_size/1024:.1f} KB")
                    
                    print(f"    ✅ 下載完成: {downloaded_size/1024:.1f} KB")
                    
                    try:
                        with zipfile.ZipFile(io.BytesIO(file_content)) as zip_file:
                            file_list = zip_file.namelist()
                            print(f"    📦 壓縮檔包含: {len(file_list)} 個檔案")
                            
                            has_township_files = any(
                                'TOWN' in filename.upper() and 
                                ('.SHP' in filename.upper() or '.DBF' in filename.upper())
                                for filename in file_list
                            )
                            
                            if has_township_files:
                                print(f"    🎯 找到鄉鎮邊界檔案!")
                                
                                for filename in file_list:
                                    if any(ext in filename.upper() for ext in ['.SHP', '.SHX', '.DBF', '.PRJ']):
                                        zip_file.extract(filename, target_path)
                                        print(f"      解壓縮: {filename}")
                                
                                successful_download = url
                                print(f"    ✅ 成功下載並解壓縮!")
                                break
                            else:
                                print(f"    ⚠️ 不是鄉鎮邊界檔案，繼續測試...")
                    
                    except zipfile.BadZipFile:
                        print(f"    ⚠️ 不是有效的 ZIP 檔案，繼續測試...")
                    
                    except Exception as e:
                        print(f"    ⚠️ 解壓縮失敗: {e}")
                
                else:
                    print(f"    ⚠️ 檔案太小，可能不是目標檔案")
            
            else:
                print(f"    ❌ 狀態: {response.status_code}")
        
        except requests.exceptions.Timeout:
            print(f"    ⏰ 逾時，繼續下一個...")
        
        except requests.exceptions.RequestException as e:
            print(f"    ❌ 網路錯誤: {e}")
        
        except Exception as e:
            print(f"    ❌ 其他錯誤: {e}")
        
        time.sleep(0.5)
        
        if successful_download:
            break
    
    if successful_download:
        print(f"\n🎉 成功從 NLSC 下載鄉鎮邊界檔案!")
        print(f"   來源: {successful_download}")
        print(f"   目錄: {target_path.absolute()}")
        
        downloaded_files = [f for f in township_files if f.exists()]
        print(f"   檔案: {len(downloaded_files)}/{len(township_files)} 個")
        
        if len(downloaded_files) == len(township_files):
            print(f"   ✅ 所有必要檔案已下載完成!")
            return True
        else:
            print(f"   ⚠️ 部分檔案缺失，可能需要手動補充")
            return False
    else:
        print(f"\n❌ 無法從 NLSC 下載鄉鎮邊界檔案")
        return False

def show_download_guide():
    """顯示手動下載指南"""
    print("\n" + "=" * 60)
    print("📋 鄉鎮邊界檔案獲取指南")
    print("=" * 60)
    
    print("🌐 NLSC 國土測繪圖資e商城")
    print("網址: https://whgis-nlsc.moi.gov.tw/Opendata/Files.aspx")
    print()
    print("📥 下載步驟:")
    print("  1. 瀏覽器開啟上述網址")
    print("  2. 點選「實體檔案 (Physical Files)」")
    print("  3. 尋找鄉鎮市區界線相關檔案")
    print("  4. 點擊下載按鈕")
    print("  5. 下載 ZIP 檔案並解壓縮")
    print("  6. 將檔案放置在 data/ 目錄中")
    print()
    print("📁 必要檔案:")
    print("  • TOWN_MOI.shp (主檔案)")
    print("  • TOWN_MOI.shx (索引檔案)")
    print("  • TOWN_MOI.dbf (屬性檔案)")
    print("  • TOWN_MOI.prj (座標系統檔案)")

def load_township_boundaries_with_auto_download():
    """載入鄉鎮邊界 (包含自動下載功能)"""
    print("\n" + "=" * 50)
    print("🗺️ 載入鄉鎮邊界")
    print("=" * 50)
    
    # 檢查可能的檔案位置
    possible_paths = [
        'TOWN_MOI.shp',
        'data/TOWN_MOI.shp',
        '../data/TOWN_MOI.shp'
    ]
    
    existing_path = None
    for path in possible_paths:
        if os.path.exists(path):
            existing_path = path
            break
    
    if existing_path:
        print(f"✅ 發現現有檔案: {existing_path}")
        
        try:
            towns_gdf = gpd.read_file(existing_path)
            print(f"  總鄉鎮數: {len(towns_gdf)}")
            print(f"  座標系統: {towns_gdf.crs}")
            
            target_counties = ['花蓮縣', '宜蘭縣']
            study_towns = towns_gdf[towns_gdf['COUNTYNAME'].isin(target_counties)].copy()
            
            if len(study_towns) > 0:
                print(f"  目標縣市鄉鎮: {len(study_towns)}")
                
                if study_towns.crs.to_epsg() != 3826:
                    study_towns = study_towns.to_crs(epsg=3826)
                    print("  座標系統已轉換為 EPSG:3826")
                
                return study_towns
            else:
                print("  ❌ 找不到目標縣市 (花蓮縣、宜蘭縣)")
                return None
                
        except Exception as e:
            print(f"  ❌ 載入失敗: {e}")
            return None
    
    else:
        print("❌ 未發現鄉鎮邊界檔案")
        
        print("\n🤖 嘗試自動下載...")
        download_success = download_township_boundaries_nlsc()
        
        if download_success:
            for path in possible_paths:
                if os.path.exists(path):
                    try:
                        towns_gdf = gpd.read_file(path)
                        target_counties = ['花蓮縣', '宜蘭縣']
                        study_towns = towns_gdf[towns_gdf['COUNTYNAME'].isin(target_counties)].copy()
                        
                        if len(study_towns) > 0:
                            if study_towns.crs.to_epsg() != 3826:
                                study_towns = study_towns.to_crs(epsg=3826)
                            return study_towns
                    except Exception as e:
                        print(f"  ❌ 下載後載入失敗: {e}")
        
        show_download_guide()
        return None

def compute_zonal_statistics(towns_gdf):
    """計算真實的區域統計量"""
    print("\n" + "=" * 50)
    print("📊 計算區域統計量")
    print("=" * 50)
    
    # 檢查柵格檔案
    required_files = ['kriging_rainfall.tif', 'kriging_variance.tif', 'rf_rainfall.tif']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 缺少柵格檔案: {missing_files}")
        print("請確保已執行 Cell 10 (GeoTIFF 匯出)")
        return None
    
    print("✅ 所有柵格檔案存在")
    
    try:
        from rasterstats import zonal_stats
        
        results = {}
        
        # 計算各柵格的區域統計量
        raster_configs = {
            'kriging_rainfall': {'file': 'kriging_rainfall.tif', 'stats': ['mean', 'max']},
            'kriging_variance': {'file': 'kriging_variance.tif', 'stats': ['mean']},
            'rf_rainfall': {'file': 'rf_rainfall.tif', 'stats': ['mean']}
        }
        
        for raster_name, config in raster_configs.items():
            print(f"\n計算 {raster_name} 統計量:")
            
            stats = zonal_stats(
                towns_gdf,
                config['file'],
                stats=config['stats'],
                geojson_out=True,
                nodata=-9999.0
            )
            
            valid_count = sum(1 for s in stats if s.get('mean') is not None and not np.isnan(s['mean']))
            print(f"  有效統計量: {valid_count}/{len(stats)} 鄉鎮")
            
            if valid_count == 0:
                print(f"  ❌ 沒有有效的統計量")
                return None
            
            results[raster_name] = stats
            print(f"  ✅ {raster_name} 統計量計算完成")
        
        return results
        
    except Exception as e:
        print(f"⚠️ 統計計算失敗: {e}")
        return None

def create_decision_table(towns_gdf, zonal_results):
    """建立決策表格"""
    print("\n" + "=" * 50)
    print("📋 建立決策表格")
    print("=" * 50)
    
    town_names = []
    county_names = []
    kriging_means = []
    kriging_maxs = []
    rf_means = []
    variance_means = []
    
    for i, town in towns_gdf.iterrows():
        town_names.append(town['TOWNNAME'])
        county_names.append(town['COUNTYNAME'])
        
        kriging_stats = zonal_results['kriging_rainfall'][i]
        kriging_means.append(kriging_stats['mean'])
        kriging_maxs.append(kriging_stats['max'])
        
        rf_stats = zonal_results['rf_rainfall'][i]
        rf_means.append(rf_stats['mean'])
        
        var_stats = zonal_results['kriging_variance'][i]
        variance_means.append(var_stats['mean'])
    
    decision_table = pd.DataFrame({
        '鄉鎮': town_names,
        '縣市': county_names,
        'Kriging平均': kriging_means,
        'Kriging最大': kriging_maxs,
        'RF平均': rf_means,
        '平均variance': variance_means
    })
    
    print(f"✅ 決策表格建立完成")
    print(f"  總鄉鎮數: {len(decision_table)}")
    print(f"  花蓮縣: {len(decision_table[decision_table['縣市'] == '花蓮縣'])}")
    print(f"  宜蘭縣: {len(decision_table[decision_table['縣市'] == '宜蘭縣'])}")
    
    return decision_table

def calculate_confidence_levels(decision_table):
    """計算可信度等級"""
    print("\n" + "=" * 50)
    print("🎯 計算可信度等級")
    print("=" * 50)
    
    variance_values = decision_table['平均variance'].values
    p33 = np.percentile(variance_values, 33)
    p66 = np.percentile(variance_values, 66)
    
    print(f"變異數分佈:")
    print(f"  33rd 百分位數: {p33:.4f}")
    print(f"  66th 百分位數: {p66:.4f}")
    print(f"  變異數範圍: {variance_values.min():.4f} - {variance_values.max():.4f}")
    
    def classify_confidence(variance):
        if variance < p33:
            return 'HIGH'
        elif variance < p66:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    decision_table['可信度'] = decision_table['平均variance'].apply(classify_confidence)
    
    confidence_counts = decision_table['可信度'].value_counts()
    print(f"\n可信度分佈:")
    for level in ['HIGH', 'MEDIUM', 'LOW']:
        count = confidence_counts.get(level, 0)
        percentage = count / len(decision_table) * 100
        print(f"  {level}: {count} 鄉鎮 ({percentage:.1f}%)")
    
    return decision_table, p33, p66

def analyze_critical_combinations(decision_table):
    """分析關鍵組合"""
    print("\n" + "=" * 50)
    print("⚠️ 分析關鍵組合")
    print("=" * 50)
    
    rainfall_threshold = np.percentile(decision_table['Kriging平均'], 75)
    print(f"高雨量門檻: {rainfall_threshold:.1f} mm/hr (75th 百分位數)")
    
    high_rainfall = decision_table['Kriging平均'] >= rainfall_threshold
    low_confidence = decision_table['可信度'] == 'LOW'
    
    critical_towns = decision_table[high_rainfall & low_confidence]
    confirmed_risk = decision_table[high_rainfall & (decision_table['可信度'] == 'HIGH')]
    safe_zones = decision_table[(decision_table['Kriging平均'] < rainfall_threshold) & 
                             (decision_table['可信度'] == 'HIGH')]
    
    print(f"\n關鍵組合分析:")
    print(f"  高雨量 + 低可信度: {len(critical_towns)} 鄉鎮")
    print(f"  高雨量 + 高可信度: {len(confirmed_risk)} 鄉鎮")
    print(f"  低雨量 + 高可信度: {len(safe_zones)} 鄉鎮")
    
    if len(critical_towns) > 0:
        print(f"\n⚠️ 需要立即關注的鄉鎮 (高雨量 + 低可信度):")
        critical_cols = ['鄉鎮', '縣市', 'Kriging平均', 'RF平均', '平均variance']
        print(critical_towns[critical_cols].to_string(index=False))
    
    if len(confirmed_risk) > 0:
        print(f"\n🔴 確認風險鄉鎮 (高雨量 + 高可信度):")
        print(confirmed_risk[critical_cols].to_string(index=False))
    
    return {
        'critical_towns': critical_towns,
        'confirmed_risk': confirmed_risk,
        'safe_zones': safe_zones,
        'rainfall_threshold': rainfall_threshold
    }

def compare_methods(decision_table):
    """比較不同方法"""
    print("\n" + "=" * 50)
    print("🔍 比較不同方法")
    print("=" * 50)
    
    decision_table['方法差異'] = decision_table['Kriging平均'] - decision_table['RF平均']
    decision_table['相對差異%'] = (decision_table['方法差異'] / 
                                  decision_table['Kriging平均'] * 100)
    
    abs_diff = np.abs(decision_table['方法差異'])
    mean_diff = np.mean(abs_diff)
    max_diff = np.max(abs_diff)
    
    print(f"方法比較:")
    print(f"  平均絕對差異: {mean_diff:.2f} mm/hr")
    print(f"  最大絕對差異: {max_diff:.2f} mm/hr")
    print(f"  平均相對差異: {np.mean(np.abs(decision_table['相對差異%'])):.1f}%")
    
    max_diff_idx = np.argmax(np.abs(decision_table['方法差異']))
    max_diff_town = decision_table.iloc[max_diff_idx]
    
    print(f"\n差異最大鄉鎮:")
    print(f"  {max_diff_town['鄉鎮']} ({max_diff_town['縣市']})")
    print(f"  Kriging: {max_diff_town['Kriging平均']:.1f} mm/hr")
    print(f"  RF: {max_diff_town['RF平均']:.1f} mm/hr")
    print(f"  差異: {max_diff_town['方法差異']:.1f} mm/hr")
    
    return decision_table

def generate_final_report(decision_table, analysis_results):
    """產生最終報告"""
    print("\n" + "=" * 60)
    print("📊 最終決策支援報告")
    print("=" * 60)
    
    summary_stats = {
        '總鄉鎮數': len(decision_table),
        '花蓮縣鄉鎮': len(decision_table[decision_table['縣市'] == '花蓮縣']),
        '宜蘭縣鄉鎮': len(decision_table[decision_table['縣市'] == '宜蘭縣']),
        '平均Kriging雨量': decision_table['Kriging平均'].mean(),
        '平均RF雨量': decision_table['RF平均'].mean(),
        '平均變異數': decision_table['平均variance'].mean(),
        'HIGH可信度': len(decision_table[decision_table['可信度'] == 'HIGH']),
        'MEDIUM可信度': len(decision_table[decision_table['可信度'] == 'MEDIUM']),
        'LOW可信度': len(decision_table[decision_table['可信度'] == 'LOW']),
    }
    
    print("摘要統計:")
    for key, value in summary_stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    try:
        decision_table.to_csv('township_decision_table.csv', index=False, encoding='utf-8-sig')
        print("\n✅ 決策表格已儲存: township_decision_table.csv")
    except Exception as e:
        print(f"\n⚠️ 表格儲存失敗: {e}")
    
    print("\n" + "=" * 50)
    print("🏛️ 鄉鎮決策表格 (按風險排序)")
    print("=" * 50)
    
    display_table = decision_table.sort_values(['可信度', 'Kriging平均'], ascending=[False, False])
    
    display_cols = ['鄉鎮', '縣市', 'Kriging平均', 'Kriging最大', 'RF平均', '平均variance', '可信度']
    print(display_table[display_cols].to_string(index=False))
    
    print("\n" + "=" * 50)
    print("🎯 指揮官決策建議")
    print("=" * 50)
    
    critical_towns = analysis_results['critical_towns']
    confirmed_risk = analysis_results['confirmed_risk']
    safe_zones = analysis_results['safe_zones']
    
    if len(critical_towns) > 0:
        print("⚠️ 立即行動 (高雨量 + 低可信度):")
        for _, town in critical_towns.iterrows():
            print(f"  • {town['鄉鎮']} ({town['縣市']}): 部署額外感測器，加強監測")
    
    if len(confirmed_risk) > 0:
        print("\n🔴 撤離準備 (確認高風險):")
        for _, town in confirmed_risk.iterrows():
            print(f"  • {town['鄉鎮']} ({town['縣市']}): 準備撤離計畫")
    
    if len(safe_zones) > 0:
        print("\n✅ 監控狀態 (低風險):")
        for _, town in safe_zones.head(3).iterrows():
            print(f"  • {town['鄉鎮']} ({town['縣市']}): 持續監控")
    
    print("\n📊 方法選擇建議:")
    print("  • 高可信度區域: 使用 Kriging 預測 (有變異數資訊)")
    print("  • 低可信度區域: 使用 RF 預測 (較穩定)")
    print("  • 方法差異大區域: 綜合考慮兩種方法")
    print("  • 緊急決策: 優先考慮高可信度預測")

# 主要執行函數
def main_cell11_no_simulation():
    """Cell 11 無模擬版主要執行函數"""
    print("Lab 2 Cell 11: Zonal Statistics — Township Decision Table (無模擬版)")
    print("僅使用真實資料，整合 NLSC 網站自動下載鄉鎮邊界檔案功能")
    print("=" * 60)
    
    try:
        # 載入鄉鎮邊界 (包含自動下載)
        towns_gdf = load_township_boundaries_with_auto_download()
        
        if towns_gdf is None:
            print("❌ 鄉鎮邊界載入失敗")
            print("❌ 無法繼續執行，需要真實的鄉鎮邊界檔案和柵格檔案")
            return None
        
        # 計算真實的區域統計量
        zonal_results = compute_zonal_statistics(towns_gdf)
        
        if zonal_results is None:
            print("❌ 區域統計計算失敗")
            return None
        
        # 建立決策表格
        decision_table = create_decision_table(towns_gdf, zonal_results)
        
        # 計算可信度等級
        decision_table, p33, p66 = calculate_confidence_levels(decision_table)
        
        # 分析關鍵組合
        analysis_results = analyze_critical_combinations(decision_table)
        
        # 比較不同方法
        decision_table = compare_methods(decision_table)
        
        # 產生最終報告
        generate_final_report(decision_table, analysis_results)
        
        print("\n" + "=" * 60)
        print("🎉 Cell 11 無模擬版分析完成！")
        print("=" * 60)
        print("✅ 僅使用真實資料")
        print("✅ 整合自動下載功能")
        print("✅ 完整的決策支援分析")
        print("✅ 具體的指揮官建議")
        
        return decision_table
        
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None

# 執行分析
decision_table = main_cell11_no_simulation()

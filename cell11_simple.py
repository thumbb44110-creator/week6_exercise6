#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 11: Zonal Statistics — Township Decision Table (Simple Version)
Compute per-township statistics from Kriging and RF rasters, then compare them side-by-side.
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def check_dependencies():
    """檢查必要的函式庫依賴"""
    print("檢查函式庫依賴...")
    
    try:
        from rasterstats import zonal_stats
        print("rasterstats: 可用")
    except ImportError:
        print("rasterstats: 未安裝")
        return False
    
    try:
        import geopandas as gpd
        print("geopandas: 可用")
    except ImportError:
        print("geopandas: 未安裝")
        return False
    
    try:
        import rasterio
        print("rasterio: 可用")
    except ImportError:
        print("rasterio: 未安裝")
        return False
    
    return True

def load_township_boundaries():
    """載入鄉鎮邊界"""
    print("\n載入鄉鎮邊界...")
    
    try:
        import geopandas as gpd
        from pathlib import Path
        
        # 使用完整路徑
        base_dir = Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6")
        shp_path = base_dir / "data/TOWN_MOI.shp"
        
        if not shp_path.exists():
            print(f"鄉鎮邊界檔案不存在: {shp_path}")
            return None, []
        
        # 載入 Shapefile
        towns_gdf = gpd.read_file(shp_path)
        print(f"載入成功: {len(towns_gdf)} 個鄉鎮")
        print(f"座標系統: {towns_gdf.crs}")
        
        # 檢查縣市資訊
        if 'COUNTYNAME' in towns_gdf.columns:
            counties = towns_gdf['COUNTYNAME'].unique()
            print(f"縣市數量: {len(counties)}")
            
            # 尋找目標縣市
            target_counties = []
            for county in counties:
                county_str = str(county).strip()
                if '花蓮' in county_str or '宜蘭' in county_str:
                    target_counties.append(county)
            
            if target_counties:
                print(f"找到目標縣市: {target_counties}")
                study_towns = towns_gdf[towns_gdf['COUNTYNAME'].isin(target_counties)].copy()
                print(f"目標鄉鎮數: {len(study_towns)}")
            else:
                print("沒有找到花蓮或宜蘭縣，使用所有縣市")
                study_towns = towns_gdf.copy()
                target_counties = list(counties)
        else:
            print("沒有 COUNTYNAME 欄位，使用所有鄉鎮")
            study_towns = towns_gdf.copy()
            target_counties = []
        
        # 轉換座標系統為 EPSG:3826
        if str(study_towns.crs) != 'EPSG:3826':
            print("轉換座標系統為 EPSG:3826...")
            study_towns = study_towns.to_crs('EPSG:3826')
            print(f"轉換完成: {study_towns.crs}")
        
        return study_towns, target_counties
        
    except Exception as e:
        print(f"載入失敗: {e}")
        return None, []

def compute_zonal_statistics(towns_gdf):
    """計算區域統計量"""
    print("\n計算區域統計量...")
    
    try:
        from rasterstats import zonal_stats
        from pathlib import Path
        import os
        
        # 使用完整路徑
        base_dir = Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6")
        
        raster_files = {
            'kriging_rainfall.tif': 'kriging_stats',
            'kriging_variance.tif': 'variance_stats',
            'rf_rainfall.tif': 'rf_stats'
        }
        
        results = {}
        
        for filename, key in raster_files.items():
            filepath = base_dir / filename
            
            if not filepath.exists():
                print(f"檔案不存在: {filepath}")
                results[key] = None
                continue
            
            try:
                print(f"處理 {filename}...")
                
                # 計算區域統計量
                if 'variance' in filename:
                    stats = zonal_stats(
                        towns_gdf,
                        str(filepath),
                        stats=['mean'],
                        geojson_out=False,
                        nodata=-9999.0
                    )
                else:
                    stats = zonal_stats(
                        towns_gdf,
                        str(filepath),
                        stats=['mean', 'max'],
                        geojson_out=False,
                        nodata=-9999.0
                    )
                
                results[key] = stats
                valid_count = sum(1 for s in stats if s.get('mean') is not None)
                print(f"  有效統計量: {valid_count}/{len(stats)}")
                
            except Exception as e:
                print(f"  計算失敗: {e}")
                results[key] = None
        
        return results
        
    except Exception as e:
        print(f"區域統計計算失敗: {e}")
        return None

def create_decision_table(towns_gdf, stats_results, target_counties):
    """建立決策表格"""
    print("\n建立決策表格...")
    
    try:
        # 提取統計結果
        kriging_stats = stats_results.get('kriging_stats')
        variance_stats = stats_results.get('variance_stats')
        rf_stats = stats_results.get('rf_stats')
        
        if not all([kriging_stats, variance_stats, rf_stats]):
            print("統計結果不完整")
            return None
        
        # 提取鄉鎮資訊
        town_names = []
        county_names = []
        
        if 'TOWNNAME' in towns_gdf.columns:
            town_names = towns_gdf['TOWNNAME'].tolist()
        elif 'town_name' in towns_gdf.columns:
            town_names = towns_gdf['town_name'].tolist()
        else:
            town_names = [f"Town_{i}" for i in range(len(towns_gdf))]
        
        if 'COUNTYNAME' in towns_gdf.columns:
            county_names = towns_gdf['COUNTYNAME'].tolist()
        elif 'county_name' in towns_gdf.columns:
            county_names = towns_gdf['county_name'].tolist()
        else:
            county_names = ["Unknown"] * len(towns_gdf)
        
        # 提取統計數值
        kriging_means = [s.get('mean', np.nan) for s in kriging_stats]
        kriging_maxs = [s.get('max', np.nan) for s in kriging_stats]
        rf_means = [s.get('mean', np.nan) for s in rf_stats]
        variance_means = [s.get('mean', np.nan) for s in variance_stats]
        
        # 建立 DataFrame
        decision_table = pd.DataFrame({
            '鄉鎮': town_names,
            '縣市': county_names,
            'Kriging平均': kriging_means,
            'Kriging最大': kriging_maxs,
            'RF平均': rf_means,
            '平均variance': variance_means
        })
        
        # 移除無效資料
        valid_mask = ~(decision_table[['Kriging平均', 'RF平均', '平均variance']].isnull().any(axis=1))
        decision_table = decision_table[valid_mask].copy()
        
        print(f"有效資料: {len(decision_table)} 鄉鎮")
        
        return decision_table
        
    except Exception as e:
        print(f"決策表格建立失敗: {e}")
        return None

def calculate_confidence_levels(decision_table):
    """計算可信度等級"""
    print("\n計算可信度等級...")
    
    try:
        variance_values = decision_table['平均variance'].values
        p33 = np.percentile(variance_values, 33)
        p66 = np.percentile(variance_values, 66)
        
        print(f"變異數分佈:")
        print(f"  33rd 百分位數: {p33:.4f}")
        print(f"  66th 百分位數: {p66:.4f}")
        
        def classify_confidence(variance):
            if variance < p33:
                return 'HIGH'
            elif variance < p66:
                return 'MEDIUM'
            else:
                return 'LOW'
        
        decision_table['可信度'] = decision_table['平均variance'].apply(classify_confidence)
        
        confidence_counts = decision_table['可信度'].value_counts()
        print(f"可信度分佈:")
        for level in ['HIGH', 'MEDIUM', 'LOW']:
            count = confidence_counts.get(level, 0)
            percentage = count / len(decision_table) * 100
            print(f"  {level}: {count} 鄉鎮 ({percentage:.1f}%)")
        
        return decision_table
        
    except Exception as e:
        print(f"可信度計算失敗: {e}")
        return decision_table

def analyze_results(decision_table):
    """分析結果"""
    print("\n分析結果...")
    
    try:
        # 高雨量門檻
        rainfall_threshold = np.percentile(decision_table['Kriging平均'], 75)
        print(f"高雨量門檻: {rainfall_threshold:.1f} mm/hr")
        
        high_rainfall = decision_table['Kriging平均'] >= rainfall_threshold
        low_confidence = decision_table['可信度'] == 'LOW'
        
        critical_towns = decision_table[high_rainfall & low_confidence]
        confirmed_risk = decision_table[high_rainfall & (decision_table['可信度'] == 'HIGH')]
        
        print(f"關鍵組合分析:")
        print(f"  高雨量 + 低可信度: {len(critical_towns)} 鄉鎮")
        print(f"  高雨量 + 高可信度: {len(confirmed_risk)} 鄉鎮")
        
        # 方法比較
        decision_table['方法差異'] = decision_table['Kriging平均'] - decision_table['RF平均']
        abs_diff = np.abs(decision_table['方法差異'])
        
        print(f"方法比較:")
        print(f"  平均絕對差異: {np.mean(abs_diff):.2f} mm/hr")
        print(f"  最大絕對差異: {np.max(abs_diff):.2f} mm/hr")
        
        return critical_towns, confirmed_risk
        
    except Exception as e:
        print(f"結果分析失敗: {e}")
        return None, None

def main_cell11():
    """主要執行函數"""
    print("Lab 2 Cell 11: Zonal Statistics - Township Decision Table")
    print("計算鄉鎮統計量並建立決策表格")
    print("=" * 60)
    
    # 檢查依賴
    if not check_dependencies():
        print("缺少必要函式庫，無法執行")
        return False
    
    # 載入鄉鎮邊界
    towns_gdf, target_counties = load_township_boundaries()
    if towns_gdf is None:
        print("鄉鎮邊界載入失敗")
        return False
    
    # 計算區域統計量
    stats_results = compute_zonal_statistics(towns_gdf)
    if not stats_results:
        print("區域統計計算失敗")
        return False
    
    # 建立決策表格
    decision_table = create_decision_table(towns_gdf, stats_results, target_counties)
    if decision_table is None:
        print("決策表格建立失敗")
        return False
    
    # 計算可信度
    decision_table = calculate_confidence_levels(decision_table)
    
    # 分析結果
    critical_towns, confirmed_risk = analyze_results(decision_table)
    
    # 儲存結果
    try:
        decision_table.to_csv('township_decision_table.csv', index=False, encoding='utf-8-sig')
        print("決策表格已儲存: township_decision_table.csv")
    except Exception as e:
        print(f"表格儲存失敗: {e}")
    
    # 顯示結果
    print("\n" + "=" * 60)
    print("鄉鎮決策表格")
    print("=" * 60)
    
    # 按可信度和雨量排序
    display_table = decision_table.sort_values(['可信度', 'Kriging平均'], ascending=[False, False])
    print(display_table.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("Zonal Statistics 分析完成！")
    print("=" * 60)
    print("關鍵發現:")
    print(f"  • 需要關注鄉鎮: {len(critical_towns) if critical_towns is not None else 0} 個")
    print(f"  • 確認風險鄉鎮: {len(confirmed_risk) if confirmed_risk is not None else 0} 個")
    print("  • Kriging vs RF 差異已量化")
    print("  • 可信度分類支援決策制定")
    
    return True

if __name__ == "__main__":
    success = main_cell11()
else:
    print("Cell 11 模組已載入")
    print("使用 main_cell11() 函數執行完整分析")

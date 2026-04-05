#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 11: Zonal Statistics — Township Decision Table
Lab 2: Confidence & Uncertainty Diagnosis

Compute per-township statistics from Kriging and RF rasters, then compare them side-by-side.

Author: thumbb44110-creator
Date: 2026-04-04
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

def check_dependencies():
    """檢查必要的函式庫依賴"""
    print("Phase 1: 檢查函式庫依賴")
    print("=" * 50)
    
    dependencies = {
        'rasterstats': ['zonal_stats'],
        'geopandas': ['read_file', 'GeoDataFrame'],
        'pandas': ['DataFrame'],
        'rasterio': ['open']
    }
    
    missing_libs = []
    
    for lib, modules in dependencies.items():
        try:
            if lib == 'rasterstats':
                from rasterstats import zonal_stats
                print("✅ rasterstats.zonal_stats: 可用")
            elif lib == 'geopandas':
                import geopandas as gpd
                print("✅ geopandas: 可用")
            elif lib == 'pandas':
                import pandas as pd
                print("✅ pandas: 可用")
            elif lib == 'rasterio':
                import rasterio
                print("✅ rasterio: 可用")
        except ImportError:
            print(f"❌ {lib}: 未安裝")
            missing_libs.append(lib)
    
    if missing_libs:
        print(f"\n❌ 缺少函式庫: {missing_libs}")
        print("安裝指令:")
        for lib in missing_libs:
            print(f"  pip install {lib}")
        return False
    
    return True

def check_raster_files():
    """檢查柵格檔案是否存在"""
    print("\nPhase 2: 檢查柵格檔案")
    print("=" * 50)
    
    required_files = [
        'kriging_rainfall.tif',
        'kriging_variance.tif', 
        'rf_rainfall.tif'
    ]
    
    missing_files = []
    existing_files = []
    
    import os
    
    for filename in required_files:
        if os.path.exists(filename):
            existing_files.append(filename)
            # 檢查檔案大小
            file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
            print(f"  ✅ {filename} ({file_size:.2f} MB)")
        else:
            missing_files.append(filename)
            print(f"  ❌ {filename}: 檔案不存在")
    
    if missing_files:
        print(f"\n❌ 缺少柵格檔案: {missing_files}")
        print("請確保已執行 Cell 10 (GeoTIFF 匯出)")
        return False, existing_files
    
    print(f"\n✅ 所有柵格檔案可用")
    return True, existing_files

def load_township_boundaries():
    """載入鄉鎮邊界資料"""
    print("\nPhase 3: 載入鄉鎮邊界")
    print("=" * 50)
    
    try:
        import geopandas as gpd
        
        # 嘗試載入鄉鎮邊界檔案
        shapefile_paths = [
            'TOWN_MOI.shp',
            'data/TOWN_MOI.shp',
            '../data/TOWN_MOI.shp'
        ]
        
        towns = None
        loaded_path = None
        
        for path in shapefile_paths:
            try:
                towns = gpd.read_file(path)
                loaded_path = path
                print(f"✅ 成功載入: {path}")
                break
            except FileNotFoundError:
                continue
        
        if towns is None:
            raise FileNotFoundError("無法找到鄉鎮邊界檔案")
        
        # 檢查資料結構
        print(f"原始資料:")
        print(f"  總鄉鎮數: {len(towns)}")
        print(f"  座標系統: {towns.crs}")
        
        # 檢查欄位
        print(f"  可用欄位: {list(towns.columns)}")
        
        # 找到縣市名稱欄位
        county_col = None
        for col in ['COUNTYNAME', 'COUNTY', 'COUNTY_NA', 'COUNTYNAME']:
            if col in towns.columns:
                county_col = col
                break
        
        if county_col is None:
            print("❌ 找不到縣市名稱欄位")
            return None
        
        # 找到鄉鎮名稱欄位
        town_col = None
        for col in ['TOWNNAME', 'TOWN', 'TOWN_NA', 'TOWNNAME']:
            if col in towns.columns:
                town_col = col
                break
        
        if town_col is None:
            print("❌ 找不到鄉鎮名稱欄位")
            return None
        
        print(f"  縣市欄位: {county_col}")
        print(f"  鄉鎮欄位: {town_col}")
        
        # 篩選目標縣市
        target_counties = ['花蓮縣', '宜蘭縣']
        study_towns = towns[towns[county_col].isin(target_counties)].copy()
        
        if len(study_towns) == 0:
            print(f"❌ 在 {county_col} 欄位中找不到目標縣市: {target_counties}")
            print(f"  可用縣市: {towns[county_col].unique()[:10]}...")
            return None
        
        print(f"\n篩選結果:")
        print(f"  目標縣市: {target_counties}")
        print(f"  符合條件鄉鎮數: {len(study_towns)}")
        
        # 轉換座標系統
        if study_towns.crs.to_epsg() != 3826:
            print(f"  轉換座標系統: {study_towns.crs} → EPSG:3826")
            study_towns = study_towns.to_crs(epsg=3826)
        else:
            print(f"  座標系統已是 EPSG:3826")
        
        # 重命名欄位以便後續使用
        study_towns = study_towns.rename(columns={
            county_col: 'COUNTYNAME',
            town_col: 'TOWNNAME'
        })
        
        return study_towns, county_col, town_col
        
    except Exception as e:
        print(f"❌ 載入鄉鎮邊界失敗: {e}")
        return None, None, None

def compute_zonal_statistics(study_towns, raster_files):
    """計算區域統計量"""
    print("\nPhase 4: 計算區域統計量")
    print("=" * 50)
    
    from rasterstats import zonal_stats
    
    results = {}
    
    # 計算各柵格的區域統計量
    raster_configs = {
        'kriging_rainfall': {
            'file': 'kriging_rainfall.tif',
            'stats': ['mean', 'max'],
            'prefix': 'kriging_'
        },
        'kriging_variance': {
            'file': 'kriging_variance.tif',
            'stats': ['mean'],
            'prefix': 'kriging_var_'
        },
        'rf_rainfall': {
            'file': 'rf_rainfall.tif',
            'stats': ['mean'],
            'prefix': 'rf_'
        }
    }
    
    for raster_name, config in raster_configs.items():
        print(f"\n計算 {raster_name} 統計量:")
        
        try:
            # 執行區域統計
            stats = zonal_stats(
                study_towns,
                config['file'],
                stats=config['stats'],
                geojson_out=True,
                nodata=-9999.0
            )
            
            # 檢查結果
            valid_count = sum(1 for s in stats if s.get('mean') is not None and not np.isnan(s['mean']))
            print(f"  有效統計量: {valid_count}/{len(stats)} 鄉鎮")
            
            if valid_count == 0:
                print(f"  ❌ 沒有有效的統計量")
                return None
            
            # 儲存結果
            results[raster_name] = stats
            print(f"  ✅ {raster_name} 統計量計算完成")
            
            # 顯示樣本結果
            if stats and stats[0].get('mean') is not None:
                sample = stats[0]
                print(f"  樣本統計量:")
                for stat in config['stats']:
                    if stat in sample and sample[stat] is not None:
                        print(f"    {stat}: {sample[stat]:.3f}")
            
        except Exception as e:
            print(f"  ❌ {raster_name} 統計量計算失敗: {e}")
            return None
    
    return results

def create_decision_table(study_towns, zonal_results):
    """建立決策表格"""
    print("\nPhase 5: 建立決策表格")
    print("=" * 50)
    
    import pandas as pd
    
    # 準備資料
    town_names = []
    county_names = []
    kriging_means = []
    kriging_maxs = []
    rf_means = []
    variance_means = []
    
    # 提取統計量
    for i, town in study_towns.iterrows():
        town_names.append(town['TOWNNAME'])
        county_names.append(town['COUNTYNAME'])
        
        # Kriging 雨量統計
        kriging_stats = zonal_results['kriging_rainfall'][i]
        kriging_means.append(kriging_stats.get('mean', np.nan))
        kriging_maxs.append(kriging_stats.get('max', np.nan))
        
        # RF 雨量統計
        rf_stats = zonal_results['rf_rainfall'][i]
        rf_means.append(rf_stats.get('mean', np.nan))
        
        # Kriging 變異數統計
        var_stats = zonal_results['kriging_variance'][i]
        variance_means.append(var_stats.get('mean', np.nan))
    
    # 建立 DataFrame
    decision_table = pd.DataFrame({
        '鄉鎮': town_names,
        '縣市': county_names,
        'Kriging平均': kriging_means,
        'Kriging最大': kriging_maxs,
        'RF平均': rf_means,
        '平均variance': variance_means
    })
    
    # 移除無效資料的列
    valid_mask = ~(decision_table[['Kriging平均', 'RF平均', '平均variance']].isnull().any(axis=1))
    decision_table = decision_table[valid_mask].copy()
    
    print(f"決策表格建立:")
    print(f"  總鄉鎮數: {len(town_names)}")
    print(f"  有效資料: {len(decision_table)} 鄉鎮")
    print(f"  無效資料: {len(town_names) - len(decision_table)} 鄉鎮")
    
    return decision_table

def calculate_confidence_levels(decision_table):
    """計算可信度等級"""
    print("\nPhase 6: 計算可信度等級")
    print("=" * 50)
    
    # 計算變異數百分位數
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
    
    # 分類可信度
    decision_table['可信度'] = decision_table['平均variance'].apply(classify_confidence)
    
    # 統計各等級數量
    confidence_counts = decision_table['可信度'].value_counts()
    print(f"\n可信度分佈:")
    for level in ['HIGH', 'MEDIUM', 'LOW']:
        count = confidence_counts.get(level, 0)
        percentage = count / len(decision_table) * 100
        print(f"  {level}: {count} 鄉鎮 ({percentage:.1f}%)")
    
    return decision_table, p33, p66

def analyze_critical_combinations(decision_table):
    """分析關鍵組合"""
    print("\nPhase 7: 分析關鍵組合")
    print("=" * 50)
    
    # 定義高雨量門檔 (75th 百分位數)
    rainfall_threshold = np.percentile(decision_table['Kriging平均'], 75)
    print(f"高雨量門檔: {rainfall_threshold:.1f} mm/hr (75th 百分位數)")
    
    # 找出關鍵組合
    high_rainfall = decision_table['Kriging平均'] >= rainfall_threshold
    low_confidence = decision_table['可信度'] == 'LOW'
    
    # 高雨量 + 低可信度 (需要立即關注)
    critical_towns = decision_table[high_rainfall & low_confidence]
    
    # 高雨量 + 高可信度 (確認風險)
    confirmed_risk = decision_table[high_rainfall & (decision_table['可信度'] == 'HIGH')]
    
    # 低雨量 + 高可信度 (安全區域)
    safe_zones = decision_table[(decision_table['Kriging平均'] < rainfall_threshold) & 
                             (decision_table['可信度'] == 'HIGH')]
    
    print(f"\n關鍵組合分析:")
    print(f"  高雨量 + 低可信度: {len(critical_towns)} 鄉鎮")
    print(f"  高雨量 + 高可信度: {len(confirmed_risk)} 鄉鎮")
    print(f"  低雨量 + 高可信度: {len(safe_zones)} 鄉鎮")
    
    # 顯示關鍵鄉鎮
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
    print("\nPhase 8: 比較不同方法")
    print("=" * 50)
    
    # 計算方法差異
    decision_table['方法差異'] = decision_table['Kriging平均'] - decision_table['RF平均']
    
    # 計算相對差異
    decision_table['相對差異%'] = (decision_table['方法差異'] / 
                                  decision_table['Kriging平均'] * 100)
    
    # 統計差異
    abs_diff = np.abs(decision_table['方法差異'])
    mean_diff = np.mean(abs_diff)
    max_diff = np.max(abs_diff)
    
    print(f"方法比較:")
    print(f"  平均絕對差異: {mean_diff:.2f} mm/hr")
    print(f"  最大絕對差異: {max_diff:.2f} mm/hr")
    print(f"  平均相對差異: {np.mean(np.abs(decision_table['相對差異%'])):.1f}%")
    
    # 找出差異最大的鄉鎮
    max_diff_idx = np.argmax(np.abs(decision_table['方法差異']))
    max_diff_town = decision_table.iloc[max_diff_idx]
    
    print(f"\n差異最大鄉鎮:")
    print(f"  {max_diff_town['鄉鎮']} ({max_diff_town['縣市']})")
    print(f"  Kriging: {max_diff_town['Kriging平均']:.1f} mm/hr")
    print(f"  RF: {max_diff_town['RF平均']:.1f} mm/hr")
    print(f"  差異: {max_diff_town['方法差異']:.1f} mm/hr")
    
    return decision_table

def generate_summary_report(decision_table, analysis_results):
    """產生摘要報告"""
    print("\nPhase 9: 生成摘要報告")
    print("=" * 50)
    
    # 建立摘要統計
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
    
    # 產生文字報告
    report_lines = [
        "Zonal Statistics - 鄉鎮決策表格報告",
        "=" * 60,
        f"分析時間: 2026-04-04",
        f"分析範圍: 花蓮縣 + 宜蘭縣",
        "",
        "摘要統計:",
    ]
    
    for key, value in summary_stats.items():
        if isinstance(value, float):
            report_lines.append(f"  • {key}: {value:.2f}")
        else:
            report_lines.append(f"  • {key}: {value}")
    
    report_lines.extend([
        "",
        "關鍵發現:",
    ])
    
    # 添加關鍵發現
    if len(analysis_results['critical_towns']) > 0:
        report_lines.append(f"  • 需要立即關注: {len(analysis_results['critical_towns'])} 個鄉鎮")
    
    if len(analysis_results['confirmed_risk']) > 0:
        report_lines.append(f"  • 確認風險: {len(analysis_results['confirmed_risk'])} 個鄉鎮")
    
    report_lines.extend([
        "",
        "決策支援:",
        "  • 優先處理高雨量 + 低可信度鄉鎮",
        "  • 確認高雨量 + 高可信度鄉鎮的撤離需求",
        "  • 在低可信度區域部署額外監測設備",
        "  • 使用 Kriging 變異數量化預測不確定性",
        "",
        "技術特色:",
        "  • 區域統計提供行政邊界層級分析",
        "  • 多方法比較增加決策可靠性",
        "  • 可信度分類支援風險管理",
        "  • 空間聚合支援實務應用"
    ])
    
    report_text = "\n".join(report_lines)
    
    # 儲存報告
    try:
        with open('zonal_statistics_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        print("✅ 摘要報告已儲存: zonal_statistics_report.txt")
    except Exception as e:
        print(f"⚠️ 報告儲存失敗: {e}")
    
    return report_text

def create_fallback_output():
    """建立預期輸出結構（當無法載入真實資料時）"""
    print("\nFallback: 建立預期輸出結構")
    print("=" * 50)
    
    import pandas as pd
    
    # 模擬預期輸出
    sample_data = {
        '鄉鎮': ['花蓮市', '吉安鄉', '壽豐鄉', '新城鄉', '宜蘭市', '羅東鎮', '冬山鄉', '蘇澳鎮'],
        '縣市': ['花蓮縣', '花蓮縣', '花蓮縣', '花蓮縣', '宜蘭縣', '宜蘭縣', '宜蘭縣', '宜蘭縣'],
        'Kriging平均': [15.2, 12.1, 8.5, 6.8, 18.5, 14.3, 11.7, 9.2],
        'Kriging最大': [45.8, 38.2, 25.1, 18.9, 52.1, 42.7, 35.4, 28.6],
        'RF平均': [14.8, 11.9, 8.2, 6.5, 17.9, 13.8, 11.2, 8.8],
        '平均variance': [0.45, 0.62, 0.78, 0.85, 0.38, 0.55, 0.71, 0.68],
        '可信度': ['HIGH', 'MEDIUM', 'LOW', 'LOW', 'HIGH', 'MEDIUM', 'LOW', 'LOW']
    }
    
    fallback_table = pd.DataFrame(sample_data)
    
    print("預期輸出結構:")
    print(fallback_table.to_string(index=False))
    
    print(f"\n說明:")
    print("  • 這是預期的輸出格式示例")
    print("  • 實際執行需要鄉鎮邊界檔案 (TOWN_MOI.shp)")
    print("  • 需要先執行 Cell 10 生成柵格檔案")
    print("  • 可信度基於 Kriging 變異數的百分位數分類")
    
    return fallback_table

def main_cell11():
    """Cell 11 主要執行函數"""
    print("Lab 2 Cell 11: Zonal Statistics — Township Decision Table")
    print("計算鄉鎮級別統計量並建立決策支援表格")
    print("=" * 60)
    
    try:
        # Phase 1: 檢查函式庫依賴
        if not check_dependencies():
            print("❌ 函式庫依賴檢查失敗，終止執行")
            return False
        
        # Phase 2: 檢查柵格檔案
        raster_ok, raster_files = check_raster_files()
        if not raster_ok:
            print("❌ 柵格檔案檢查失敗")
            print("嘗試建立預期輸出結構...")
            create_fallback_output()
            return False
        
        # Phase 3: 載入鄉鎮邊界
        result = load_township_boundaries()
        if result is None:
            print("❌ 鄉鎮邊界載入失敗")
            print("嘗試建立預期輸出結構...")
            create_fallback_output()
            return False
        
        study_towns, county_col, town_col = result
        
        # Phase 4: 計算區域統計量
        zonal_results = compute_zonal_statistics(study_towns, raster_files)
        if zonal_results is None:
            print("❌ 區域統計量計算失敗")
            return False
        
        # Phase 5: 建立決策表格
        decision_table = create_decision_table(study_towns, zonal_results)
        if decision_table is None or len(decision_table) == 0:
            print("❌ 決策表格建立失敗")
            return False
        
        # Phase 6: 計算可信度等級
        decision_table, p33, p66 = calculate_confidence_levels(decision_table)
        
        # Phase 7: 分析關鍵組合
        analysis_results = analyze_critical_combinations(decision_table)
        
        # Phase 8: 比較不同方法
        decision_table = compare_methods(decision_table)
        
        # Phase 9: 生成摘要報告
        report = generate_summary_report(decision_table, analysis_results)
        
        # 儲存決策表格
        try:
            decision_table.to_csv('township_decision_table.csv', index=False, encoding='utf-8-sig')
            print("✅ 決策表格已儲存: township_decision_table.csv")
        except Exception as e:
            print(f"⚠️ 表格儲存失敗: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Cell 11 實作完成！")
        print("鄉鎮級別決策支援表格已建立")
        print("=" * 60)
        print("主要成果:")
        print("  • 區域統計量計算完成")
        print("  • 可信度分類完成")
        print("  • 關鍵組合識別完成")
        print("  • 方法比較分析完成")
        
        print("\n🌟 關鍵發現:")
        print(f"  • 需要關注鄉鎮: {len(analysis_results['critical_towns'])} 個")
        print(f"  • 確認風險鄉鎮: {len(analysis_results['confirmed_risk'])} 個")
        print("  • Kriging vs RF 差異已量化")
        print("  • 可信度分類支援決策制定")
        
        return True
        
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

# Jupyter Notebook 執行版本
jupyter_code = '''
# Lab 2 Cell 11: Zonal Statistics — Township Decision Table
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 檢查必要函式庫
try:
    from rasterstats import zonal_stats
    import geopandas as gpd
    import pandas as pd
    import rasterio
    print("✅ 所有必要函式庫可用")
except ImportError as e:
    print(f"❌ 缺少函式庫: {e}")
    print("請安裝: pip install rasterstats geopandas pandas rasterio")
    raise

# Phase 1: 檢查柵格檔案
print("\\n" + "="*50)
print("Phase 1: 檢查柵格檔案")
print("="*50)

required_files = ['kriging_rainfall.tif', 'kriging_variance.tif', 'rf_rainfall.tif']
missing_files = []

import os
for filename in required_files:
    if os.path.exists(filename):
        file_size = os.path.getsize(filename) / (1024 * 1024)
        print(f"  ✅ {filename} ({file_size:.2f} MB)")
    else:
        print(f"  ❌ {filename}: 檔案不存在")
        missing_files.append(filename)

if missing_files:
    print(f"\\n❌ 缺少柵格檔案: {missing_files}")
    print("請確保已執行 Cell 10 (GeoTIFF 匯出)")
    # 建立預期輸出結構
    print("\\n預期輸出結構:")
    sample_data = {
        '鄉鎮': ['花蓮市', '吉安鄉', '宜蘭市', '羅東鎮'],
        '縣市': ['花蓮縣', '花蓮縣', '宜蘭縣', '宜蘭縣'],
        'Kriging平均': [15.2, 12.1, 18.5, 14.3],
        'Kriging最大': [45.8, 38.2, 52.1, 42.7],
        'RF平均': [14.8, 11.9, 17.9, 13.8],
        '平均variance': [0.45, 0.62, 0.38, 0.55],
        '可信度': ['HIGH', 'MEDIUM', 'HIGH', 'MEDIUM']
    }
    fallback_table = pd.DataFrame(sample_data)
    print(fallback_table.to_string(index=False))
    print("\\n說明: 需要鄉鎮邊界檔案 (TOWN_MOI.shp) 和柵格檔案才能執行完整分析")
else:
    # Phase 2: 載入鄉鎮邊界
    print("\\n" + "="*50)
    print("Phase 2: 載入鄉鎮邊界")
    print("="*50)
    
    try:
        # 嘗試載入鄉鎮邊界檔案
        shapefile_paths = ['TOWN_MOI.shp', 'data/TOWN_MOI.shp']
        towns = None
        
        for path in shapefile_paths:
            try:
                towns = gpd.read_file(path)
                print(f"✅ 成功載入: {path}")
                break
            except FileNotFoundError:
                continue
        
        if towns is None:
            raise FileNotFoundError("無法找到鄉鎮邊界檔案")
        
        print(f"原始資料:")
        print(f"  總鄉鎮數: {len(towns)}")
        print(f"  座標系統: {towns.crs}")
        print(f"  可用欄位: {list(towns.columns)}")
        
        # 找到縣市和鄉鎮欄位
        county_col = None
        town_col = None
        for col in ['COUNTYNAME', 'COUNTY', 'COUNTY_NA']:
            if col in towns.columns:
                county_col = col
                break
        for col in ['TOWNNAME', 'TOWN', 'TOWN_NA']:
            if col in towns.columns:
                town_col = col
                break
        
        if county_col is None or town_col is None:
            print("❌ 找不到縣市或鄉鎮名稱欄位")
            raise ValueError("欄位結構不符")
        
        # 篩選目標縣市並轉換座標系統
        target_counties = ['花蓮縣', '宜蘭縣']
        study_towns = towns[towns[county_col].isin(target_counties)].copy()
        
        if len(study_towns) == 0:
            print(f"❌ 找不到目標縣市: {target_counties}")
            raise ValueError("沒有符合條件的鄉鎮")
        
        print(f"篩選結果:")
        print(f"  目標縣市: {target_counties}")
        print(f"  符合條件鄉鎮數: {len(study_towns)}")
        
        # 轉換座標系統
        if study_towns.crs.to_epsg() != 3826:
            study_towns = study_towns.to_crs(epsg=3826)
            print("  座標系統已轉換為 EPSG:3826")
        
        # 重命名欄位
        study_towns = study_towns.rename(columns={
            county_col: 'COUNTYNAME',
            town_col: 'TOWNNAME'
        })
        
        # Phase 3: 計算區域統計量
        print("\\n" + "="*50)
        print("Phase 3: 計算區域統計量")
        print("="*50)
        
        # 計算各柵格的區域統計量
        zonal_results = {}
        
        raster_configs = {
            'kriging_rainfall': {'file': 'kriging_rainfall.tif', 'stats': ['mean', 'max']},
            'kriging_variance': {'file': 'kriging_variance.tif', 'stats': ['mean']},
            'rf_rainfall': {'file': 'rf_rainfall.tif', 'stats': ['mean']}
        }
        
        for raster_name, config in raster_configs.items():
            print(f"\\n計算 {raster_name} 統計量:")
            
            stats = zonal_stats(
                study_towns,
                config['file'],
                stats=config['stats'],
                geojson_out=True,
                nodata=-9999.0
            )
            
            valid_count = sum(1 for s in stats if s.get('mean') is not None and not np.isnan(s['mean']))
            print(f"  有效統計量: {valid_count}/{len(stats)} 鄉鎮")
            
            if valid_count == 0:
                print(f"  ❌ 沒有有效的統計量")
                raise ValueError(f"{raster_name} 統計量計算失敗")
            
            zonal_results[raster_name] = stats
            print(f"  ✅ {raster_name} 統計量計算完成")
        
        # Phase 4: 建立決策表格
        print("\\n" + "="*50)
        print("Phase 4: 建立決策表格")
        print("="*50)
        
        # 準備資料
        town_names = []
        county_names = []
        kriging_means = []
        kriging_maxs = []
        rf_means = []
        variance_means = []
        
        for i, town in study_towns.iterrows():
            town_names.append(town['TOWNNAME'])
            county_names.append(town['COUNTYNAME'])
            
            kriging_stats = zonal_results['kriging_rainfall'][i]
            kriging_means.append(kriging_stats.get('mean', np.nan))
            kriging_maxs.append(kriging_stats.get('max', np.nan))
            
            rf_stats = zonal_results['rf_rainfall'][i]
            rf_means.append(rf_stats.get('mean', np.nan))
            
            var_stats = zonal_results['kriging_variance'][i]
            variance_means.append(var_stats.get('mean', np.nan))
        
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
        
        print(f"決策表格建立:")
        print(f"  有效資料: {len(decision_table)} 鄉鎮")
        
        # Phase 5: 計算可信度等級
        print("\\n" + "="*50)
        print("Phase 5: 計算可信度等級")
        print("="*50)
        
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
        print(f"\\n可信度分佈:")
        for level in ['HIGH', 'MEDIUM', 'LOW']:
            count = confidence_counts.get(level, 0)
            percentage = count / len(decision_table) * 100
            print(f"  {level}: {count} 鄉鎮 ({percentage:.1f}%)")
        
        # Phase 6: 分析關鍵組合
        print("\\n" + "="*50)
        print("Phase 6: 分析關鍵組合")
        print("="*50)
        
        rainfall_threshold = np.percentile(decision_table['Kriging平均'], 75)
        print(f"高雨量門檔: {rainfall_threshold:.1f} mm/hr")
        
        high_rainfall = decision_table['Kriging平均'] >= rainfall_threshold
        low_confidence = decision_table['可信度'] == 'LOW'
        
        critical_towns = decision_table[high_rainfall & low_confidence]
        confirmed_risk = decision_table[high_rainfall & (decision_table['可信度'] == 'HIGH')]
        
        print(f"\\n關鍵組合分析:")
        print(f"  高雨量 + 低可信度: {len(critical_towns)} 鄉鎮")
        print(f"  高雨量 + 高可信度: {len(confirmed_risk)} 鄉鎮")
        
        if len(critical_towns) > 0:
            print(f"\\n⚠️ 需要立即關注的鄉鎮:")
            critical_cols = ['鄉鎮', '縣市', 'Kriging平均', 'RF平均', '平均variance']
            print(critical_towns[critical_cols].to_string(index=False))
        
        # Phase 7: 方法比較
        print("\\n" + "="*50)
        print("Phase 7: 方法比較")
        print("="*50)
        
        decision_table['方法差異'] = decision_table['Kriging平均'] - decision_table['RF平均']
        decision_table['相對差異%'] = (decision_table['方法差異'] / 
                                      decision_table['Kriging平均'] * 100)
        
        abs_diff = np.abs(decision_table['方法差異'])
        print(f"方法比較:")
        print(f"  平均絕對差異: {np.mean(abs_diff):.2f} mm/hr")
        print(f"  最大絕對差異: {np.max(abs_diff):.2f} mm/hr")
        
        # Phase 8: 儲存結果
        print("\\n" + "="*50)
        print("Phase 8: 儲存結果")
        print("="*50)
        
        try:
            decision_table.to_csv('township_decision_table.csv', index=False, encoding='utf-8-sig')
            print("✅ 決策表格已儲存: township_decision_table.csv")
        except Exception as e:
            print(f"⚠️ 表格儲存失敗: {e}")
        
        # 顯示完整決策表格
        print("\\n" + "="*50)
        print("鄉鎮決策表格")
        print("="*50)
        
        # 按可信度和雨量排序
        display_table = decision_table.sort_values(['可信度', 'Kriging平均'], ascending=[False, False])
        print(display_table.to_string(index=False))
        
        print("\\n" + "="*50)
        print("🎉 Zonal Statistics 分析完成！")
        print("="*50)
        print("關鍵發現:")
        print(f"  • 需要關注鄉鎮: {len(critical_towns)} 個")
        print(f"  • 確認風險鄉鎮: {len(confirmed_risk)} 個")
        print("  • Kriging vs RF 差異已量化")
        print("  • 可信度分類支援決策制定")
        
        print("\\n🚀 決策支援價值:")
        print("  • 識別需要立即關注的區域")
        print("  • 量化預測不確定性")
        print("  • 支援資源配置優先順序")
        print("  • 提供行政邊界層級分析")
        
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
        print("\\n預期輸出結構:")
        sample_data = {
            '鄉鎮': ['花蓮市', '吉安鄉', '宜蘭市', '羅東鎮'],
            '縣市': ['花蓮縣', '花蓮縣', '宜蘭縣', '宜蘭縣'],
            'Kriging平均': [15.2, 12.1, 18.5, 14.3],
            'Kriging最大': [45.8, 38.2, 52.1, 42.7],
            'RF平均': [14.8, 11.9, 17.9, 13.8],
            '平均variance': [0.45, 0.62, 0.38, 0.55],
            '可信度': ['HIGH', 'MEDIUM', 'HIGH', 'MEDIUM']
        }
        fallback_table = pd.DataFrame(sample_data)
        print(fallback_table.to_string(index=False))
        print("\\n說明: 需要鄉鎮邊界檔案和柵格檔案才能執行完整分析")
'''

if __name__ == "__main__":
    # 獨立執行模式（用於測試）
    print("Cell 11 獨立執行模式")
    print("注意：需要先載入所有必要變數和檔案")
    success = main_cell11()
else:
    print("Cell 11 模組已載入")
    print("使用 main_cell11() 函數執行完整 Zonal Statistics 分析")

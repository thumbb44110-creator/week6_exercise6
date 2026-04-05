#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 10: Export to GeoTIFF
Lab 2: Confidence & Uncertainty Diagnosis

Save 2D numpy arrays as GeoTIFF using rasterio with proper coordinate system transformation.

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
    
    try:
        import rasterio
        from rasterio.transform import from_bounds
        from rasterio.crs import CRS
        print("✅ rasterio: 可用")
        print(f"  版本: {rasterio.__version__}")
    except ImportError:
        print("❌ rasterio: 未安裝")
        print("  安裝指令: pip install rasterio")
        return False
    
    try:
        import os
        print("✅ os: 可用")
    except ImportError:
        print("❌ os: 不可用")
        return False
    
    return True

def check_prerequisites():
    """檢查必要的前置變數"""
    print("\nPhase 2: 檢查前置變數")
    print("=" * 50)
    
    required_vars = {
        '網格座標': ['grid_x', 'grid_y'],
        '插值結果': ['z_kriging', 'ss_kriging', 'z_rf']
    }
    
    missing_vars = []
    
    for category, vars_list in required_vars.items():
        print(f"\n{category}:")
        for var in vars_list:
            if var in globals() or var in locals():
                # 獲取變數值進行檢查
                var_value = globals().get(var, locals().get(var))
                if var_value is not None:
                    if hasattr(var_value, 'shape'):
                        print(f"  ✅ {var}: {var_value.shape}")
                    else:
                        print(f"  ✅ {var}: {type(var_value).__name__}")
                else:
                    print(f"  ⚠️ {var}: 存在但為 None")
                    missing_vars.append(var)
            else:
                print(f"  ❌ {var}: 未定義")
                missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ 缺少必要變數: {missing_vars}")
        print("請確保已執行 Cell 1-4 (插值計算)")
        return False
    
    return True

def validate_grid_coordinates():
    """驗證網格座標的完整性"""
    print("\nPhase 3: 驗證網格座標")
    print("=" * 50)
    
    # 獲取網格座標
    grid_x = globals().get('grid_x', locals().get('grid_x'))
    grid_y = globals().get('grid_y', locals().get('grid_y'))
    
    if grid_x is None or grid_y is None:
        print("❌ 網格座標未找到")
        return None
    
    # 計算邊界
    x_min, x_max = grid_x.min(), grid_x.max()
    y_min, y_max = grid_y.min(), grid_y.max()
    
    print("網格座標驗證:")
    print(f"  X 範圍: {x_min:.0f} - {x_max:.0f} m")
    print(f"  Y 範圍: {y_min:.0f} - {y_max:.0f} m")
    print(f"  X 解析度: {np.mean(np.diff(grid_x)):.1f} m")
    print(f"  Y 解析度: {np.mean(np.diff(grid_y)):.1f} m")
    print(f"  網格尺寸: {len(grid_x)} × {len(grid_y)} = {len(grid_x)*len(grid_y):,} 點")
    
    # 檢查合理性
    if x_min >= x_max or y_min >= y_max:
        print("❌ 座標範圍不合理")
        return None
    
    if len(grid_x) < 10 or len(grid_y) < 10:
        print("⚠️ 網格尺寸較小，可能影響輸出品質")
    
    # 計算覆蓋面積
    area_km2 = (x_max - x_min) * (y_max - y_min) / 1_000_000
    print(f"  覆蓋面積: {area_km2:.1f} km²")
    
    return {
        'x_min': x_min, 'x_max': x_max,
        'y_min': y_min, 'y_max': y_max,
        'nx': len(grid_x), 'ny': len(grid_y),
        'area_km2': area_km2
    }

def prepare_data_arrays():
    """準備要匯出的資料陣列"""
    print("\nPhase 4: 準備資料陣列")
    print("=" * 50)
    
    # 獲取插值結果
    z_kriging = globals().get('z_kriging', locals().get('z_kriging'))
    ss_kriging = globals().get('ss_kriging', locals().get('ss_kriging'))
    z_rf = globals().get('z_rf', locals().get('z_rf'))
    
    if any(v is None for v in [z_kriging, ss_kriging, z_rf]):
        print("❌ 插值結果未完整")
        return None
    
    # 準備資料字典
    data_arrays = {
        'kriging_rainfall': {
            'data': z_kriging,
            'description': 'Kriging rainfall predictions',
            'units': 'mm/hr',
            'filename': 'kriging_rainfall.tif'
        },
        'kriging_variance': {
            'data': ss_kriging,
            'description': 'Kriging variance estimates',
            'units': 'variance (log-space)',
            'filename': 'kriging_variance.tif'
        },
        'rf_rainfall': {
            'data': z_rf,
            'description': 'Random Forest rainfall predictions',
            'units': 'mm/hr',
            'filename': 'rf_rainfall.tif'
        }
    }
    
    print("資料陣列驗證:")
    for name, info in data_arrays.items():
        data = info['data']
        print(f"\n{name}:")
        print(f"  形狀: {data.shape}")
        print(f"  資料類型: {data.dtype}")
        print(f"  數值範圍: {np.nanmin(data):.3f} - {np.nanmax(data):.3f}")
        print(f"  平均值: {np.nanmean(data):.3f}")
        print(f"  NaN 數量: {np.sum(np.isnan(data))} ({np.sum(np.isnan(data))/data.size*100:.1f}%)")
        print(f"  描述: {info['description']}")
        print(f"  單位: {info['units']}")
        print(f"  檔名: {info['filename']}")
    
    return data_arrays

def create_geotiff_profile(grid_info):
    """建立 GeoTIFF 設定檔"""
    print("\nPhase 5: 建立 GeoTIFF 設定檔")
    print("=" * 50)
    
    # 匯入 rasterio 函數
    try:
        from rasterio.transform import from_bounds
        from rasterio.crs import CRS
        print("✅ rasterio 函數匯入成功")
    except ImportError as e:
        print(f"❌ rasterio 函數匯入失敗: {e}")
        return None
    
    # 建立仿射變換
    transform = from_bounds(
        grid_info['x_min'], grid_info['y_min'],
        grid_info['x_max'], grid_info['y_max'],
        grid_info['nx'], grid_info['ny']
    )
    
    print("仿射變換參數:")
    print(f"  左上角 X: {transform[2]:.1f}")
    print(f"  左上角 Y: {transform[5]:.1f}")
    print(f"  像素寬度: {transform[0]:.1f} m")
    print(f"  像素高度: {transform[4]:.1f} m")
    
    # 建立 CRS
    try:
        crs = CRS.from_epsg(3826)  # TWD97
        print(f"✅ 座標系統: {crs.name}")
        print(f"  EPSG 代碼: {crs.to_epsg()}")
        print(f"  投影: {crs.to_proj4()}")
    except Exception as e:
        print(f"❌ CRS 建立失敗: {e}")
        return None
    
    # 建立設定檔
    profile = {
        'driver': 'GTiff',
        'dtype': 'float32',
        'width': grid_info['nx'],
        'height': grid_info['ny'],
        'count': 1,
        'crs': crs,
        'transform': transform,
        'nodata': -9999.0,
        'compress': 'lzw',
        'tiled': True,
        'blockxsize': 256,
        'blockysize': 256
    }
    
    print("\nGeoTIFF 設定檔:")
    for key, value in profile.items():
        if key == 'crs':
            print(f"  {key}: {value.name}")
        else:
            print(f"  {key}: {value}")
    
    return profile

def export_geotiff_file(data_info, profile, grid_info):
    """匯出單個 GeoTIFF 檔案"""
    import rasterio
    
    name = data_info['name']
    data = data_info['data']
    description = data_info['description']
    filename = data_info['filename']
    
    print(f"\n匯出 {name}:")
    print(f"  描述: {description}")
    print(f"  檔名: {filename}")
    
    try:
        # 資料前處理
        print("  資料前處理...")
        
        # 轉換為 float32
        data_float32 = data.astype(np.float32)
        print(f"    資料類型: {data.dtype} → float32")
        
        # 處理 NaN 值
        nan_count = np.sum(np.isnan(data_float32))
        if nan_count > 0:
            data_processed = np.where(np.isnan(data_float32), -9999.0, data_float32)
            print(f"    NaN 處理: {nan_count} → -9999.0")
        else:
            data_processed = data_float32
            print(f"    NaN 數量: 0")
        
        # 座標轉換 (numpy → GeoTIFF)
        print("  座標轉換...")
        data_geotiff = np.flipud(data_processed)
        print(f"    翻轉陣列: {data_processed.shape} → {data_geotiff.shape}")
        
        # 寫入 GeoTIFF
        print(f"  寫入檔案...")
        with rasterio.open(filename, 'w', **profile) as dst:
            dst.write(data_geotiff, 1)
            
            # 添加中繼資料
            dst.update_tags(
                description=description,
                units=data_info['units'],
                created_by='Cell 10: GeoTIFF Export',
                creation_date='2026-04-04',
                coordinate_system='EPSG:3826'
            )
        
        print(f"  ✅ 檔案已儲存: {filename}")
        
        # 檢查檔案大小
        import os
        file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
        print(f"  檔案大小: {file_size:.2f} MB")
        
        return True, filename
        
    except Exception as e:
        print(f"  ❌ 匯出失敗: {e}")
        return False, None

def verify_geotiff_file(filename, expected_shape):
    """驗證 GeoTIFF 檔案的完整性"""
    print(f"\n驗證 {filename}:")
    
    try:
        import rasterio
        
        with rasterio.open(filename) as src:
            # 檢查基本屬性
            print(f"  驅動程式: {src.driver}")
            print(f"  資料類型: {src.dtypes[0]}")
            print(f"  尺寸: {src.width} × {src.height}")
            print(f"  頻道數: {src.count}")
            print(f"  座標系統: {src.crs.to_string()}")
            print(f"  NoData 值: {src.nodata}")
            
            # 檢查尺寸
            if (src.height, src.width) != expected_shape:
                print(f"  ❌ 尺寸不符: 預期 {expected_shape}, 實際 {(src.height, src.width)}")
                return False
            
            # 檢查資料讀取
            data = src.read(1)
            print(f"  讀取資料範圍: {np.nanmin(data):.3f} - {np.nanmax(data):.3f}")
            
            # 檢查座標轉換
            transform = src.transform
            print(f"  左上角座標: ({transform[2]:.1f}, {transform[5]:.1f})")
            print(f"  像素解析度: ({transform[0]:.1f}, {transform[4]:.1f})")
        
        print(f"  ✅ 檔案驗證通過")
        return True
        
    except Exception as e:
        print(f"  ❌ 驗證失敗: {e}")
        return False

def generate_export_summary(results, grid_info):
    """產生匯出摘要報告"""
    print("\nPhase 6: 生成匯出摘要")
    print("=" * 50)
    
    success_count = sum(1 for success, _ in results if success)
    total_count = len(results)
    
    print("匯出結果摘要:")
    print(f"  總檔案數: {total_count}")
    print(f"  成功匯出: {success_count}")
    print(f"  失敗數量: {total_count - success_count}")
    print(f"  成功率: {success_count/total_count*100:.1f}%")
    
    print(f"\n網格資訊:")
    print(f"  覆蓋範圍: {grid_info['x_min']:.0f} - {grid_info['x_max']:.0f} m (Easting)")
    print(f"             {grid_info['y_min']:.0f} - {grid_info['y_max']:.0f} m (Northing)")
    print(f"  網格尺寸: {grid_info['nx']} × {grid_info['ny']} = {grid_info['nx']*grid_info['ny']:,} 點")
    print(f"  覆蓋面積: {grid_info['area_km2']:.1f} km²")
    print(f"  座標系統: EPSG:3826 (TWD97)")
    
    print(f"\n輸出檔案:")
    for success, filename in results:
        if success:
            import os
            file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
            print(f"  ✅ {filename} ({file_size:.2f} MB)")
        else:
            print(f"  ❌ {filename} (失敗)")
    
    # 產生文字報告
    report_lines = [
        "GeoTIFF Export - 匯出摘要報告",
        "=" * 50,
        f"匯出時間: 2026-04-04",
        f"座標系統: EPSG:3826 (TWD97)",
        "",
        "網格資訊:",
        f"  • 覆蓋範圍: {grid_info['x_min']:.0f} - {grid_info['x_max']:.0f} m",
        f"  • 網格尺寸: {grid_info['nx']} × {grid_info['ny']}",
        f"  • 覆蓋面積: {grid_info['area_km2']:.1f} km²",
        "",
        "輸出檔案:",
    ]
    
    for success, filename in results:
        if success:
            report_lines.append(f"  • ✅ {filename}")
        else:
            report_lines.append(f"  • ❌ {filename}")
    
    report_lines.extend([
        "",
        "技術規格:",
        "  • 格式: GeoTIFF (LZW 壓縮)",
        "  • 資料類型: Float32",
        "  • NoData 值: -9999.0",
        "  • 分塊: 256×256",
        "",
        "座標轉換:",
        "  • 原始: numpy (row 0 = south)",
        "  • 輸出: GeoTIFF (row 0 = north)",
        "  • 方法: np.flipud()",
        "",
        "應用價值:",
        "  • GIS 軟體直接讀取 (QGIS, ArcGIS)",
        "  • 空間分析與視覺化",
        "  • 災害管理系統整合",
        "  • 科學研究可重現性"
    ])
    
    report_text = "\n".join(report_lines)
    
    # 儲存報告
    try:
        with open('geotiff_export_summary.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        print("✅ 匯出摘要已儲存: geotiff_export_summary.txt")
    except Exception as e:
        print(f"⚠️ 報告儲存失敗: {e}")
    
    return report_text

def main_cell10():
    """Cell 10 主要執行函數"""
    print("Lab 2 Cell 10: Export to GeoTIFF")
    print("將插值結果匯出為標準地理空間格式")
    print("=" * 60)
    
    try:
        # Phase 1: 檢查函式庫依賴
        if not check_dependencies():
            print("❌ 函式庫依賴檢查失敗，終止執行")
            return False
        
        # Phase 2: 檢查前置變數
        if not check_prerequisites():
            print("❌ 前置變數檢查失敗，終止執行")
            return False
        
        # Phase 3: 驗證網格座標
        grid_info = validate_grid_coordinates()
        if grid_info is None:
            print("❌ 網格座標驗證失敗")
            return False
        
        # Phase 4: 準備資料陣列
        data_arrays = prepare_data_arrays()
        if data_arrays is None:
            print("❌ 資料陣列準備失敗")
            return False
        
        # Phase 5: 建立 GeoTIFF 設定檔
        profile = create_geotiff_profile(grid_info)
        if profile is None:
            print("❌ GeoTIFF 設定檔建立失敗")
            return False
        
        # Phase 6: 匯出 GeoTIFF 檔案
        print("\nPhase 6: 匯出 GeoTIFF 檔案")
        print("=" * 50)
        
        results = []
        for name, info in data_arrays.items():
            # 添加資料名稱到資訊中
            info_with_name = info.copy()
            info_with_name['name'] = name
            
            success, filename = export_geotiff_file(info_with_name, profile, grid_info)
            results.append((success, filename))
            
            if success:
                # 驗證檔案
                verify_geotiff_file(filename, info['data'].shape)
        
        # Phase 7: 生成匯出摘要
        summary = generate_export_summary(results, grid_info)
        
        # 檢查整體成功狀態
        success_count = sum(1 for success, _ in results if success)
        total_count = len(results)
        
        print("\n" + "=" * 60)
        if success_count == total_count:
            print("🎉 Cell 10 實作完成！")
            print("所有 GeoTIFF 檔案成功匯出")
        else:
            print("⚠️ Cell 10 部分完成")
            print(f"成功匯出 {success_count}/{total_count} 個檔案")
        
        print("=" * 60)
        print("輸出成果:")
        for success, filename in results:
            if success:
                print(f"  - {filename}")
        
        print("\n🌟 GeoTIFF 檔案特色:")
        print("  • 標準地理空間格式")
        print("  • 完整座標參考系統 (EPSG:3826)")
        print("  • GIS 軟體直接讀取")
        print("  • 高效 LZW 壓縮")
        
        return success_count == total_count
        
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

# Jupyter Notebook 執行版本
jupyter_code = '''
# Lab 2 Cell 10: Export to GeoTIFF
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 檢查 rasterio
try:
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.crs import CRS
    print("✅ rasterio 可用")
except ImportError:
    print("❌ 請先安裝 rasterio: pip install rasterio")
    raise ImportError("需要安裝 rasterio")

# 檢查必要變數
required_vars = ['grid_x', 'grid_y', 'z_kriging', 'ss_kriging', 'z_rf']
missing_vars = [var for var in required_vars if var not in locals() and var not in globals()]

if missing_vars:
    raise NameError(f"缺少必要變數: {missing_vars}. 請先執行 Cell 1-4")

print("✅ 前置檢查通過: 所有必要變數可用")

# 計算網格邊界
x_min, x_max = grid_x.min(), grid_x.max()
y_min, y_max = grid_y.min(), grid_y.max()

print(f"\\n網格資訊:")
print(f"  範圍: ({x_min:.0f}, {y_min:.0f}) - ({x_max:.0f}, {y_max:.0f})")
print(f"  尺寸: {len(grid_x)} × {len(grid_y)} = {len(grid_x)*len(grid_y):,} 點")
print(f"  面積: {(x_max-x_min)*(y_max-y_min)/1_000_000:.1f} km²")

# 建立 GeoTIFF 設定檔
transform = from_bounds(x_min, y_min, x_max, y_max, len(grid_x), len(grid_y))
crs = CRS.from_epsg(3826)  # TWD97

profile = {
    'driver': 'GTiff',
    'dtype': 'float32',
    'width': len(grid_x),
    'height': len(grid_y),
    'count': 1,
    'crs': crs,
    'transform': transform,
    'nodata': -9999.0,
    'compress': 'lzw',
    'tiled': True
}

print(f"\\nGeoTIFF 設定:")
print(f"  座標系統: {crs.name}")
print(f"  資料類型: float32")
print(f"  壓縮: LZW")

# 準備匯出資料
data_arrays = {
    'kriging_rainfall': {
        'data': z_kriging,
        'filename': 'kriging_rainfall.tif',
        'description': 'Kriging rainfall predictions'
    },
    'kriging_variance': {
        'data': ss_kriging,
        'filename': 'kriging_variance.tif',
        'description': 'Kriging variance estimates'
    },
    'rf_rainfall': {
        'data': z_rf,
        'filename': 'rf_rainfall.tif',
        'description': 'Random Forest rainfall predictions'
    }
}

# 匯出函數
def export_to_geotiff(name, data, filename):
    print(f"\\n匯出 {name}:")
    
    # 資料前處理
    data_float32 = data.astype(np.float32)
    data_processed = np.where(np.isnan(data_float32), -9999.0, data_float32)
    
    # 座標轉換 (numpy → GeoTIFF)
    data_geotiff = np.flipud(data_processed)
    
    # 寫入 GeoTIFF
    with rasterio.open(filename, 'w', **profile) as dst:
        dst.write(data_geotiff, 1)
        dst.update_tags(
            description=name,
            created_by='Cell 10: GeoTIFF Export',
            coordinate_system='EPSG:3826'
        )
    
    print(f"  ✅ 已儲存: {filename}")
    
    # 檢查檔案
    import os
    file_size = os.path.getsize(filename) / (1024 * 1024)
    print(f"  檔案大小: {file_size:.2f} MB")
    
    return True

# 執行匯出
print("\\n" + "="*50)
print("開始匯出 GeoTIFF 檔案")
print("="*50)

results = []
for name, info in data_arrays.items():
    success = export_to_geotiff(
        info['description'], 
        info['data'], 
        info['filename']
    )
    results.append(success)

# 匯出摘要
success_count = sum(results)
print(f"\\n" + "="*50)
print(f"匯出摘要:")
print(f"  成功: {success_count}/{len(results)} 個檔案")
print("="*50)

if success_count == len(results):
    print("🎉 所有 GeoTIFF 檔案成功匯出！")
else:
    print("⚠️ 部分檔案匯出失敗")

print("\\n輸出檔案:")
for name, info in data_arrays.items():
    print(f"  • {info['filename']}")

print("\\n🌟 檔案特色:")
print("  • 標準 GeoTIFF 格式")
print("  • EPSG:3826 座標系統")
print("  • GIS 軟體直接讀取")
print("  • LZW 壓縮節省空間")
'''

if __name__ == "__main__":
    # 獨立執行模式（用於測試）
    print("Cell 10 獨立執行模式")
    print("注意：需要先載入所有必要變數")
    success = main_cell10()
else:
    print("Cell 10 模組已載入")
    print("使用 main_cell10() 函數執行完整 GeoTIFF 匯出")

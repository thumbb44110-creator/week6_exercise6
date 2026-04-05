# 簡化資料檢查

import os
import geopandas as gpd
import rasterio
import numpy as np
from pathlib import Path

def check_township_data():
    """檢查鄉鎮邊界資料"""
    print("=== 檢查鄉鎮邊界資料 ===")
    
    data_dir = Path("data")
    shp_path = data_dir / "TOWN_MOI.shp"
    
    if not shp_path.exists():
        print("鄉鎮邊界檔案不存在")
        return None, []
    
    try:
        # 載入 Shapefile
        gdf = gpd.read_file(shp_path)
        
        print(f"鄉鎮邊界載入成功")
        print(f"總圖層數: {len(gdf)}")
        print(f"座標系統: {gdf.crs}")
        print(f"欄位: {list(gdf.columns)}")
        
        # 檢查縣市資訊
        if 'COUNTYNAME' in gdf.columns:
            counties = gdf['COUNTYNAME'].unique()
            print(f"縣市數量: {len(counties)}")
            print(f"所有縣市:")
            
            target_counties = []
            for i, county in enumerate(counties):
                count = len(gdf[gdf['COUNTYNAME'] == county])
                county_str = str(county).strip()
                print(f"  {i+1:2d}. {county_str} ({count} 個鄉鎮)")
                
                # 尋找目標縣市
                if '花蓮' in county_str or '宜蘭' in county_str:
                    target_counties.append(county)
            
            print(f"目標縣市 (包含花蓮/宜蘭): {target_counties}")
            
            if target_counties:
                target_towns = gdf[gdf['COUNTYNAME'].isin(target_counties)]
                print(f"目標鄉鎮數: {len(target_towns)}")
                
                for county in target_counties:
                    towns = gdf[gdf['COUNTYNAME'] == county]
                    print(f"  {county}: {len(towns)} 個鄉鎮")
                
                return gdf, target_counties
            else:
                print("沒有找到包含花蓮或宜蘭的縣市")
                return gdf, []
        else:
            print("沒有 COUNTYNAME 欄位")
            return gdf, []
    
    except Exception as e:
        print(f"鄉鎮邊界載入失敗: {e}")
        return None, []

def check_raster_data():
    """檢查柵格資料"""
    print("\n=== 檢查柵格資料 ===")
    
    raster_files = {
        'kriging_rainfall.tif': 'Kriging 雨量',
        'kriging_variance.tif': 'Kriging 變異數',
        'rf_rainfall.tif': 'Random Forest 雨量'
    }
    
    raster_info = {}
    
    for filename, description in raster_files.items():
        filepath = Path(filename)
        
        if not filepath.exists():
            print(f"{description} ({filename}): 檔案不存在")
            continue
        
        try:
            with rasterio.open(filepath) as src:
                info = {
                    'width': src.width,
                    'height': src.height,
                    'count': src.count,
                    'dtype': src.dtypes[0],
                    'crs': src.crs,
                    'nodata': src.nodata
                }
                
                # 讀取一小部分資料檢查數值範圍
                try:
                    data = src.read(1, window=rasterio.windows.Window(0, 0, 100, 100))
                    valid_data = data[data != src.nodata]
                    
                    if len(valid_data) > 0:
                        info['min'] = float(np.min(valid_data))
                        info['max'] = float(np.max(valid_data))
                        info['mean'] = float(np.mean(valid_data))
                        info['valid_count'] = len(valid_data)
                    else:
                        info['min'] = info['max'] = info['mean'] = None
                        info['valid_count'] = 0
                        
                except Exception:
                    info['min'] = info['max'] = info['mean'] = None
                    info['valid_count'] = 0
                
                raster_info[filename] = info
                
                print(f"{description} ({filename}):")
                print(f"  尺寸: {src.width} x {src.height}")
                print(f"  波段數: {src.count}")
                print(f"  資料類型: {src.dtypes[0]}")
                print(f"  座標系統: {src.crs}")
                print(f"  數值範圍: {info['min']:.3f} - {info['max']:.3f}")
                print(f"  有效像素: {info['valid_count']}")
                
        except Exception as e:
            print(f"{description} ({filename}): 讀取失敗 - {e}")
            raster_info[filename] = None
    
    return raster_info

def main():
    """主要檢查函數"""
    print("Cell 11 資料狀況檢查")
    print("=" * 50)
    
    # 檢查鄉鎮邊界
    gdf, target_counties = check_township_data()
    
    # 檢查柵格資料
    raster_info = check_raster_data()
    
    # 總結
    print("\n" + "=" * 50)
    print("檢查結果總結:")
    
    if gdf is not None:
        print(f"鄉鎮邊界: 可用 ({len(gdf)} 個鄉鎮)")
        if target_counties:
            print(f"目標縣市: {len(target_counties)} 個")
        else:
            print(f"目標縣市: 未找到 (將使用所有縣市)")
    else:
        print(f"鄉鎮邊界: 不可用")
    
    valid_rasters = sum(1 for info in raster_info.values() if info is not None)
    print(f"柵格資料: {valid_rasters}/3 個可用")
    
    # 判斷是否可以執行 Cell 11
    can_execute = (gdf is not None and valid_rasters >= 3)
    
    if can_execute:
        print(f"\n可以執行 Cell 11!")
        if not target_counties:
            print(f"將使用所有縣市資料")
    else:
        print(f"\n無法執行 Cell 11，需要解決上述問題")
    
    return gdf, target_counties, raster_info

if __name__ == "__main__":
    gdf, target_counties, raster_info = main()

# 簡化測試 Cell 11

import warnings
warnings.filterwarnings('ignore')

try:
    import geopandas as gpd
    import rasterio
    from rasterstats import zonal_stats
    print("所有必要函式庫可用")
except ImportError as e:
    print(f"缺少函式庫: {e}")
    exit(1)

# 測試 Shapefile
print("測試 Shapefile 載入...")
shp_path = "data/TOWN_MOI.shp"
gdf = gpd.read_file(shp_path)
print(f"載入成功: {len(gdf)} 個圖層")

# 檢查縣市
if 'COUNTYNAME' in gdf.columns:
    counties = gdf['COUNTYNAME'].unique()
    print(f"縣市數量: {len(counties)}")
    
    has_hualien = any('花蓮' in str(county) for county in counties)
    has_yilan = any('宜蘭' in str(county) for county in counties)
    
    print(f"花蓮縣: {has_hualien}")
    print(f"宜蘭縣: {has_yilan}")
    
    if has_hualien and has_yilan:
        target_towns = gdf[gdf['COUNTYNAME'].isin(['花蓮縣', '宜蘭縣'])]
        print(f"目標鄉鎮數: {len(target_towns)}")
        
        # 測試區域統計
        print("測試區域統計...")
        stats = zonal_stats(
            target_towns,
            'kriging_rainfall.tif',
            stats=['mean'],
            geojson_out=True
        )
        
        valid_stats = [s for s in stats if s.get('mean') is not None]
        print(f"有效統計量: {len(valid_stats)}")
        
        if len(valid_stats) > 0:
            print("測試成功！Cell 11 可以執行")
        else:
            print("區域統計計算失敗")
    else:
        print("缺少目標縣市")
else:
    print("缺少 COUNTYNAME 欄位")

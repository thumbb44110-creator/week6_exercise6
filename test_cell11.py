# 測試 Cell 11 執行

import warnings
warnings.filterwarnings('ignore')

try:
    # 載入必要函式庫
    from rasterstats import zonal_stats
    import geopandas as gpd
    import rasterio
    from shapely.geometry import Point, Polygon
    print("✅ 所有必要函式庫可用")
except ImportError as e:
    print(f"❌ 缺少函式庫: {e}")
    exit(1)

def test_shapefile_loading():
    """測試 Shapefile 載入"""
    print("\n=== 測試 Shapefile 載入 ===")
    
    try:
        # 載入 Shapefile
        shp_path = "data/TOWN_MOI.shp"
        gdf = gpd.read_file(shp_path)
        
        print(f"✅ Shapefile 載入成功")
        print(f"   總圖層數: {len(gdf)}")
        print(f"   座標系統: {gdf.crs}")
        print(f"   欄位數量: {len(gdf.columns)}")
        print(f"   主要欄位: {list(gdf.columns)[:5]}")
        
        # 檢查是否包含目標縣市
        if 'COUNTYNAME' in gdf.columns:
            counties = gdf['COUNTYNAME'].unique()
            print(f"\n所有縣市: {len(counties)} 個")
            for county in sorted(counties):
                count = len(gdf[gdf['COUNTYNAME'] == county])
                print(f"   {county}: {count} 個鄉鎮")
            
            # 檢查目標縣市
            has_hualien = any('花蓮' in str(county) for county in counties)
            has_yilan = any('宜蘭' in str(county) for county in counties)
            
            print(f"\n目標縣市檢查:")
            print(f"   花蓮縣: {'✅' if has_hualien else '❌'}")
            print(f"   宜蘭縣: {'✅' if has_yilan else '❌'}")
            
            if has_hualien and has_yilan:
                target_towns = gdf[gdf['COUNTYNAME'].isin(['花蓮縣', '宜蘭縣'])]
                print(f"\n目標鄉鎮分析:")
                print(f"   目標鄉鎮數: {len(target_towns)}")
                
                hualien_towns = gdf[gdf['COUNTYNAME'] == '花蓮縣']
                yilan_towns = gdf[gdf['COUNTYNAME'] == '宜蘭縣']
                print(f"   花蓮縣鄉鎮: {len(hualien_towns)}")
                print(f"   宜蘭縣鄉鎮: {len(yilan_towns)}")
                
                print(f"\n花蓮縣鄉鎮列表:")
                for _, town in hualien_towns.iterrows():
                    town_name = town.get('TOWNNAME', 'N/A')
                    print(f"   {town_name}")
                
                print(f"\n宜蘭縣鄉鎮列表:")
                for _, town in yilan_towns.iterrows():
                    town_name = town.get('TOWNNAME', 'N/A')
                    print(f"   {town_name}")
                
                return True
            else:
                print(f"\n❌ 缺少目標縣市")
                return False
        else:
            print(f"\n❌ 缺少 COUNTYNAME 欄位")
            return False
    
    except Exception as e:
        print(f"\n❌ Shapefile 載入失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_raster_files():
    """測試柵格檔案"""
    print("\n=== 測試柵格檔案 ===")
    
    required_files = [
        'kriging_rainfall.tif',
        'kriging_variance.tif', 
        'rf_rainfall.tif'
    ]
    
    all_exist = True
    
    for filename in required_files:
        try:
            import rasterio
            with rasterio.open(filename) as src:
                print(f"✅ {filename}: {src.width}x{src.height}, {src.count} bands, {src.crs}")
        except FileNotFoundError:
            print(f"❌ {filename}: 檔案不存在")
            all_exist = False
        except Exception as e:
            print(f"❌ {filename}: 讀取失敗 - {e}")
            all_exist = False
    
    return all_exist

def test_zonal_statistics():
    """測試區域統計計算"""
    print("\n=== 測試區域統計計算 ===")
    
    try:
        # 載入 Shapefile
        shp_path = "data/TOWN_MOI.shp"
        towns_gdf = gpd.read_file(shp_path)
        
        # 篩選目標縣市
        target_counties = ['花蓮縣', '宜蘭縣']
        study_towns = towns_gdf[towns_gdf['COUNTYNAME'].isin(target_counties)].copy()
        
        if len(study_towns) == 0:
            print("❌ 找不到目標縣市")
            return False
        
        print(f"目標鄉鎮數: {len(study_towns)}")
        
        # 計算區域統計
        stats = zonal_stats(
            study_towns,
            'kriging_rainfall.tif',
            stats=['mean', 'max'],
            geojson_out=True,
            nodata=-9999.0
        )
        
        valid_count = sum(1 for s in stats if s.get('mean') is not None and not np.isnan(s['mean']))
        print(f"有效統計量: {valid_count}/{len(stats)} 鄉鎮")
        
        if valid_count > 0:
            print("✅ 區域統計計算成功")
            return True
        else:
            print("❌ 沒有有效的統計量")
            return False
    
    except Exception as e:
        print(f"❌ 區域統計計算失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主要測試函數"""
    print("=== Cell 11 執行前測試 ===")
    print("=" * 50)
    
    # 1. 測試 Shapefile 載入
    shapefile_ok = test_shapefile_loading()
    
    # 2. 測試柵格檔案
    raster_ok = test_raster_files()
    
    # 3. 測試區域統計
    zonal_ok = test_zonal_statistics()
    
    # 總結
    print("\n" + "=" * 50)
    print("=== 測試結果總結 ===")
    
    print(f"Shapefile 載入: {'✅' if shapefile_ok else '❌'}")
    print(f"柵格檔案檢查: {'✅' if raster_ok else '❌'}")
    print(f"區域統計計算: {'✅' if zonal_ok else '❌'}")
    
    if shapefile_ok and raster_ok and zonal_ok:
        print("\n🎉 所有測試通過！可以執行 Cell 11")
        print("執行指令: exec(open('cell11_no_simulation.py').read())")
    else:
        print("\n⚠️ 部分測試失敗，請檢查錯誤訊息")
    
    return shapefile_ok and raster_ok and zonal_ok

if __name__ == "__main__":
    main()
else:
    print("=== Cell 11 測試模組 ===")
    print("使用 main() 執行測試")

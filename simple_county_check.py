import geopandas as gpd

# 載入 Shapefile
shp_path = "data/TOWN_MOI.shp"
gdf = gpd.read_file(shp_path)

print("Shapefile 資訊:")
print(f"  總圖層數: {len(gdf)}")
print(f"  欄位: {list(gdf.columns)}")

# 檢查縣市
if 'COUNTYNAME' in gdf.columns:
    counties = gdf['COUNTYNAME'].unique()
    print(f"  縣市數量: {len(counties)}")
    
    print("\n所有縣市:")
    for i, county in enumerate(counties):
        count = len(gdf[gdf['COUNTYNAME'] == county])
        print(f"  {i+1}. {county} ({count} 個鄉鎮)")
    
    # 尋找目標縣市
    print("\n目標縣市檢查:")
    
    target_found = False
    for county in counties:
        if '花蓮' in str(county):
            print(f"  找到花蓮相關縣市: {county}")
            target_found = True
        if '宜蘭' in str(county):
            print(f"  找到宜蘭相關縣市: {county}")
            target_found = True
    
    if not target_found:
        print("  沒有找到花蓮縣或宜蘭縣")
        print("  可能的縣市名稱不同，需要手動檢查")
        
        # 顯示所有縣市名稱供手動檢查
        print("\n所有縣市名稱 (供手動檢查):")
        for i, county in enumerate(counties):
            print(f"  {i+1}. '{county}'")

else:
    print("  沒有 COUNTYNAME 欄位")

print("\n檢查完成！")

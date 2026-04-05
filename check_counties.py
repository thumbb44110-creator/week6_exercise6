import geopandas as gpd

# 載入 Shapefile
shp_path = "data/TOWN_MOI.shp"
gdf = gpd.read_file(shp_path)

print(f"總圖層數: {len(gdf)}")
print(f"座標系統: {gdf.crs}")
print(f"欄位: {list(gdf.columns)}")

# 檢查所有縣市
if 'COUNTYNAME' in gdf.columns:
    counties = gdf['COUNTYNAME'].unique()
    print(f"\n所有縣市 ({len(counties)} 個):")
    
    county_counts = {}
    for county in sorted(counties):
        count = len(gdf[gdf['COUNTYNAME'] == county])
        county_counts[county] = count
        print(f"  {county}: {count} 個鄉鎮")
    
    # 尋找可能的目標縣市
    print(f"\n尋找目標縣市...")
    
    # 檢查包含"花蓮"的縣市
    hualien_counties = [c for c in counties if '花蓮' in str(c)]
    print(f"包含'花蓮'的縣市: {hualien_counties}")
    
    # 檢查包含"宜蘭"的縣市
    yilan_counties = [c for c in counties if '宜蘭' in str(c)]
    print(f"包含'宜蘭'的縣市: {yilan_counties}")
    
    # 檢查所有可能的欄位
    print(f"\n檢查所有欄位...")
    for col in gdf.columns:
        if 'COUNTY' in col.upper() or 'NAME' in col.upper():
            unique_values = gdf[col].unique()
            print(f"{col}: {len(unique_values)} 個唯一值")
            if len(unique_values) < 50:  # 只顯示較少的唯一值
                print(f"  值: {list(unique_values)}")
    
    # 顯示前幾個圖層的詳細資訊
    print(f"\n前10個圖層詳細資訊:")
    for i, (_, row) in enumerate(gdf.head(10).iterrows()):
        print(f"{i+1}. {dict(row)}")

else:
    print("沒有 COUNTYNAME 欄位")

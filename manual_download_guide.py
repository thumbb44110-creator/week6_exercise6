# Manual Download Guide and Offline Test

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

def show_manual_download_guide():
    """顯示手動下載指南"""
    print("=== Manual Township Boundary Download Guide ===")
    print("=" * 60)
    
    print("PROBLEM: Network connection to NLSC server failed")
    print("SOLUTION: Manual download required")
    print()
    
    print("STEP 1: Open NLSC Website")
    print("  URL: https://whgis-nlsc.moi.gov.tw/Opendata/Files.aspx")
    print()
    
    print("STEP 2: Download Process")
    print("  1. Click 'Physical Files' tab")
    print("  2. Look for township boundary files")
    print("  3. Click download button")
    print("  4. Save ZIP file")
    print("  5. Extract ZIP file")
    print("  6. Copy files to data/ directory")
    print()
    
    print("STEP 3: Required Files")
    print("  • TOWN_MOI.shp (main file)")
    print("  • TOWN_MOI.shx (index file)")
    print("  • TOWN_MOI.dbf (attribute file)")
    print("  • TOWN_MOI.prj (coordinate system file)")
    print()
    
    print("STEP 4: File Placement")
    print("  Create directory: data/")
    print("  Copy all 4 files to: data/TOWN_MOI.*")
    print()
    
    print("STEP 5: Verification")
    print("  Files should contain Hualien and Yilan counties")
    print("  Total townships should be around 25")
    print()

def test_existing_files():
    """測試現有檔案"""
    print("=== Testing Existing Township Files ===")
    
    # 檢查可能的檔案位置
    possible_paths = [
        'TOWN_MOI.shp',
        'data/TOWN_MOI.shp',
        '../data/TOWN_MOI.shp',
        'test_download/TOWN_MOI.shp'
    ]
    
    found_path = None
    for path in possible_paths:
        if os.path.exists(path):
            found_path = path
            print(f"Found existing file: {path}")
            break
    
    if found_path:
        return validate_shapefile(found_path)
    else:
        print("No existing township boundary files found")
        print("Please download files manually following the guide above")
        return False

def validate_shapefile(shp_path):
    """驗證 Shapefile"""
    print(f"\n=== Validating Shapefile: {shp_path} ===")
    
    try:
        import geopandas as gpd
        
        # 讀取 Shapefile
        gdf = gpd.read_file(shp_path)
        
        print(f"✅ Successfully loaded shapefile")
        print(f"   Total features: {len(gdf)}")
        print(f"   Coordinate system: {gdf.crs}")
        print(f"   Columns: {list(gdf.columns)}")
        
        # 檢查欄位
        county_col = None
        town_col = None
        
        for col in gdf.columns:
            if 'COUNTY' in col.upper():
                county_col = col
            if 'TOWN' in col.upper() and 'NAME' in col.upper():
                town_col = col
        
        print(f"\nColumn Analysis:")
        print(f"   County column: {county_col}")
        print(f"   Town column: {town_col}")
        
        if county_col and town_col:
            # 檢查縣市
            counties = gdf[county_col].unique()
            print(f"\nCounties found: {len(counties)}")
            for county in sorted(counties):
                count = len(gdf[gdf[county_col] == county])
                print(f"   {county}: {count} townships")
            
            # 檢查目標縣市
            has_hualien = any('花蓮' in str(county) for county in counties)
            has_yilan = any('宜蘭' in str(county) for county in counties)
            
            print(f"\nTarget Counties Check:")
            print(f"   Hualien County: {'✅' if has_hualien else '❌'}")
            print(f"   Yilan County: {'✅' if has_yilan else '❌'}")
            
            if has_hualien and has_yilan:
                # 篩選目標縣市
                target_towns = gdf[gdf[county_col].isin(['花蓮縣', '宜蘭縣'])]
                print(f"\nTarget Analysis:")
                print(f"   Target townships: {len(target_towns)}")
                
                hualien_towns = gdf[gdf[county_col] == '花蓮縣']
                yilan_towns = gdf[gdf[county_col] == '宜蘭縣']
                print(f"   Hualien townships: {len(hualien_towns)}")
                print(f"   Yilan townships: {len(yilan_towns)}")
                
                print(f"\nTarget Township Names:")
                for _, town in target_towns.iterrows():
                    print(f"   {town[town_col]} ({town[county_col]})")
                
                print(f"\n✅ Shapefile validation PASSED!")
                return True
            else:
                print(f"\n❌ Missing target counties (Hualien or Yilan)")
                return False
        else:
            print(f"\n❌ Missing required columns (county or town names)")
            return False
    
    except ImportError:
        print(f"\n❌ Cannot validate shapefile (geopandas not available)")
        return False
    
    except Exception as e:
        print(f"\n❌ Shapefile validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_data():
    """建立範例資料結構"""
    print("\n=== Creating Sample Data Structure ===")
    
    # 建立範例目錄結構
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # 建立範例檔案
    sample_files = {
        'TOWN_MOI.shp': 'Shapefile main file',
        'TOWN_MOI.shx': 'Shapefile index file', 
        'TOWN_MOI.dbf': 'Shapefile attribute file',
        'TOWN_MOI.prj': 'Shapefile projection file'
    }
    
    for filename, description in sample_files.items():
        file_path = data_dir / filename
        if not file_path.exists():
            # 建立空檔案作為範例
            file_path.write_text(f"# {description}\n# Please replace with actual file")
            print(f"Created sample file: {file_path}")
    
    print(f"\n✅ Sample directory structure created")
    print(f"   Please replace sample files with actual downloaded files")

def test_raster_files():
    """測試柵格檔案"""
    print("\n=== Testing Raster Files ===")
    
    required_files = [
        'kriging_rainfall.tif',
        'kriging_variance.tif', 
        'rf_rainfall.tif'
    ]
    
    all_exist = True
    
    for filename in required_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename}: {size} bytes")
        else:
            print(f"❌ {filename}: File not found")
            all_exist = False
    
    if all_exist:
        print(f"\n✅ All required raster files found")
        return True
    else:
        print(f"\n❌ Missing raster files")
        print(f"   Please ensure Cell 10 has been executed to generate these files")
        return False

def main():
    """主要執行函數"""
    print("=== Township Boundary Setup Assistant ===")
    print("=" * 50)
    
    # 顯示手動下載指南
    show_manual_download_guide()
    
    # 測試現有檔案
    has_shapefile = test_existing_files()
    
    # 測試柵格檔案
    has_rasters = test_raster_files()
    
    # 總結
    print(f"\n=== Summary ===")
    print(f"Shapefile available: {'✅' if has_shapefile else '❌'}")
    print(f"Raster files available: {'✅' if has_rasters else '❌'}")
    
    if has_shapefile and has_rasters:
        print(f"\n🎉 Ready to execute Cell 11!")
        print(f"   You can now run: exec(open('cell11_no_simulation.py').read())")
    elif has_shapefile:
        print(f"\n⚠️ Shapefile ready, but missing raster files")
        print(f"   Please execute Cell 10 first to generate raster files")
    elif has_rasters:
        print(f"\n⚠️ Raster files ready, but missing shapefile")
        print(f"   Please download township boundary files manually")
    else:
        print(f"\n❌ Both shapefile and raster files missing")
        print(f"   1. Download township boundary files manually")
        print(f"   2. Execute Cell 10 to generate raster files")
    
    # 建立範例目錄結構
    if not has_shapefile:
        create_sample_data()

if __name__ == "__main__":
    main()
else:
    print("=== Manual Download Guide Module Loaded ===")
    print("Use main() to run the setup assistant")

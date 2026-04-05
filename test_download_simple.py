# Test NLSC Download Function - Simple Version

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

def safe_mkdir(path):
    """安全建立目錄，處理檔案/目錄衝突"""
    path = Path(path)
    
    if path.exists():
        if path.is_file():
            print(f"Found file with same name {path}, deleting...")
            path.unlink()
            path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"Directory already exists: {path}")
    else:
        path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {path}")
    
    return path

def test_nlsc_download():
    """測試 NLSC 下載功能"""
    print("=== Testing NLSC Township Boundary Download ===")
    
    # 安全建立目標目錄
    target_path = safe_mkdir("test_download")
    
    # 檢查是否已存在檔案
    township_files = [
        target_path / "TOWN_MOI.shp",
        target_path / "TOWN_MOI.shx", 
        target_path / "TOWN_MOI.dbf",
        target_path / "TOWN_MOI.prj"
    ]
    
    existing_files = [f for f in township_files if f.exists()]
    all_files_exist = len(existing_files) == len(township_files)
    
    if all_files_exist:
        print(f"All township boundary files exist:")
        for f in existing_files:
            print(f"    {f.name}")
            print(f"    Size: {f.stat().st_size} bytes")
        print(f"Skipping download, validating existing files...")
        return validate_downloaded_files(target_path)
    
    print(f"No complete files found, starting download test...")
    print(f"Existing files: {len(existing_files)}")
    for f in existing_files:
        print(f"    {f.name}")
    
    # NLSC 下載 URL 模式測試
    print("\n=== Starting NLSC Download Endpoint Test ===")
    
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
        print(f"\nTesting {i}/{len(download_candidates)}: {url}")
        
        try:
            print(f"  Sending request...")
            response = session.get(url, timeout=30, stream=True)
            
            print(f"  Response status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = response.headers.get('content-length', '0')
                
                print(f"  Content type: {content_type}")
                print(f"  Content length: {int(content_length)/1024:.1f} KB")
                
                if int(content_length) > 1024:
                    print(f"  Starting download...")
                    
                    file_content = b''
                    downloaded_size = 0
                    start_time = time.time()
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file_content += chunk
                            downloaded_size += len(chunk)
                            # Show progress
                            if downloaded_size % (100*1024) == 0:
                                elapsed = time.time() - start_time
                                speed = downloaded_size / elapsed / 1024
                                print(f"      Downloaded: {downloaded_size/1024:.1f} KB (Speed: {speed:.1f} KB/s)")
                    
                    download_time = time.time() - start_time
                    print(f"  Download completed: {downloaded_size/1024:.1f} KB")
                    print(f"  Download time: {download_time:.1f} seconds")
                    print(f"  Average speed: {downloaded_size/download_time/1024:.1f} KB/s")
                    
                    # Test ZIP extraction
                    print(f"  Testing ZIP extraction...")
                    try:
                        with zipfile.ZipFile(io.BytesIO(file_content)) as zip_file:
                            file_list = zip_file.namelist()
                            print(f"    ZIP contains: {len(file_list)} files")
                            
                            # Check for township boundary files
                            shp_files = [f for f in file_list if f.upper().endswith('.SHP')]
                            dbf_files = [f for f in file_list if f.upper().endswith('.DBF')]
                            shx_files = [f for f in file_list if f.upper().endswith('.SHX')]
                            prj_files = [f for f in file_list if f.upper().endswith('.PRJ')]
                            
                            print(f"    SHP files: {len(shp_files)}")
                            print(f"    DBF files: {len(dbf_files)}")
                            print(f"    SHX files: {len(shx_files)}")
                            print(f"    PRJ files: {len(prj_files)}")
                            
                            has_township_files = any(
                                'TOWN' in filename.upper() or 'TOWN' in filename.upper()
                                for filename in file_list
                            )
                            
                            if has_township_files and len(shp_files) > 0:
                                print(f"    Found township boundary files!")
                                
                                # Extract files
                                extracted_files = []
                                for filename in file_list:
                                    if any(ext in filename.upper() for ext in ['.SHP', '.SHX', '.DBF', '.PRJ']):
                                        try:
                                            zip_file.extract(filename, target_path)
                                            extracted_files.append(filename)
                                            print(f"      Extracted: {filename}")
                                        except Exception as e:
                                            print(f"      Failed to extract {filename}: {e}")
                                
                                successful_download = url
                                print(f"    Successfully downloaded and extracted!")
                                print(f"    Extracted files: {len(extracted_files)}")
                                break
                            else:
                                print(f"    Not township boundary files")
                                print(f"    File list: {file_list[:5]}...")  # Show first 5 files
                    
                    except zipfile.BadZipFile:
                        print(f"    Not a valid ZIP file")
                    
                    except Exception as e:
                        print(f"    Extraction failed: {e}")
                
                else:
                    print(f"    File too small, may not be target file")
            
            else:
                print(f"    HTTP error: {response.status_code}")
                if response.status_code == 404:
                    print(f"      File not found")
                elif response.status_code == 403:
                    print(f"      Access denied")
                elif response.status_code == 500:
                    print(f"      Server error")
        
        except requests.exceptions.Timeout:
            print(f"    Request timeout")
        
        except requests.exceptions.ConnectionError:
            print(f"    Connection error")
        
        except requests.exceptions.RequestException as e:
            print(f"    Request error: {e}")
        
        except Exception as e:
            print(f"    Other error: {e}")
        
        # Short delay to avoid blocking
        time.sleep(0.5)
        
        if successful_download:
            break
    
    # Test results
    if successful_download:
        print(f"\n=== Download Test Successful! ===")
        print(f"   Successful URL: {successful_download}")
        print(f"   Directory: {target_path.absolute()}")
        
        return validate_downloaded_files(target_path)
    else:
        print(f"\n=== Download Test Failed ===")
        print(f"   All URLs failed to download township boundary files")
        return False

def validate_downloaded_files(target_path):
    """驗證下載的檔案"""
    print("\n=== Validating Downloaded Files ===")
    
    township_files = {
        'TOWN_MOI.shp': 'Main file',
        'TOWN_MOI.shx': 'Index file',
        'TOWN_MOI.dbf': 'Attribute file',
        'TOWN_MOI.prj': 'Coordinate system file'
    }
    
    all_valid = True
    
    for filename, description in township_files.items():
        file_path = target_path / filename
        
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"OK {filename}: {size} bytes ({description})")
            
            # Check if file size is reasonable
            if size < 100:
                print(f"  WARNING: File size is too small")
                all_valid = False
            elif filename.endswith('.shp') and size > 100000000:  # 100MB
                print(f"  WARNING: File size is too large")
                all_valid = False
        else:
            print(f"FAIL {filename}: File does not exist ({description})")
            all_valid = False
    
    # Try to load Shapefile
    if all_valid:
        try:
            import geopandas as gpd
            shp_path = target_path / "TOWN_MOI.shp"
            gdf = gpd.read_file(shp_path)
            
            print(f"\n=== Shapefile Validation ===")
            print(f"  Total features: {len(gdf)}")
            print(f"  Coordinate system: {gdf.crs}")
            print(f"  Number of columns: {len(gdf.columns)}")
            print(f"  Main columns: {list(gdf.columns)[:5]}")
            
            # Check if contains Hualien and Yilan counties
            if 'COUNTYNAME' in gdf.columns:
                counties = gdf['COUNTYNAME'].unique()
                has_hualien = any('花蓮' in str(county) for county in counties)
                has_yilan = any('宜蘭' in str(county) for county in counties)
                
                print(f"\n=== Target Counties Check ===")
                print(f"  Hualien County: {'OK' if has_hualien else 'FAIL'}")
                print(f"  Yilan County: {'OK' if has_yilan else 'FAIL'}")
                
                if has_hualien and has_yilan:
                    target_towns = gdf[gdf['COUNTYNAME'].isin(['花蓮縣', '宜蘭縣'])]
                    print(f"  Target townships: {len(target_towns)}")
                    print(f"  Hualien townships: {len(gdf[gdf['COUNTYNAME'] == '花蓮縣'])}")
                    print(f"  Yilan townships: {len(gdf[gdf['COUNTYNAME'] == '宜蘭縣'])}")
                    
                    print(f"\n=== Complete Validation Passed! ===")
                    return True
                else:
                    print(f"  Missing target counties")
                    all_valid = False
            else:
                print(f"  No COUNTYNAME column")
                all_valid = False
        
        except ImportError:
            print(f"\nWARNING: Cannot validate Shapefile (missing geopandas)")
        except Exception as e:
            print(f"\nERROR: Shapefile validation failed: {e}")
            all_valid = False
    
    if all_valid:
        print(f"\n=== File Validation Passed! ===")
    else:
        print(f"\n=== File Validation Failed! ===")
    
    return all_valid

def cleanup_test_files():
    """清理測試檔案"""
    print("\n=== Cleaning Up Test Files ===")
    
    test_dir = Path("test_download")
    if test_dir.exists():
        try:
            import shutil
            shutil.rmtree(test_dir)
            print(f"Deleted test directory: {test_dir}")
        except Exception as e:
            print(f"Cleanup failed: {e}")
    else:
        print(f"Test directory does not exist")

# 執行測試
if __name__ == "__main__":
    print("=== NLSC Township Boundary Download Function Test ===")
    print("=" * 60)
    
    try:
        success = test_nlsc_download()
        
        if success:
            print("\n=== Test Complete - Download Function Works! ===")
        else:
            print("\n=== Test Failed - Download Function Has Issues! ===")
        
        # Ask if cleanup files
        print("\nClean up test files? (Run cleanup_test_files())")
        # cleanup_test_files()  # Uncomment to clean up files
        
    except Exception as e:
        print(f"\nERROR during test: {e}")
        import traceback
        traceback.print_exc()

else:
    print("=== Download test module loaded ===")
    print("Use test_nlsc_download() to run test")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Week 6 Cell 1: Environment Setup & Data Loading
Spatial Prediction Shootout - Data Processing Functions

Author: thumbb44110-creator
Date: 2026-03-31
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import warnings
from shapely.geometry import Point

warnings.filterwarnings('ignore')

def safe_parse_float(value):
    """安全解析浮點數"""
    try:
        if value is None or value == '':
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def normalize_cwa_json(data):
    """標準化 CWA 模擬資料格式"""
    normalized = []
    
    try:
        records = data.get('records', {})
        stations = records.get('Station', [])
        
        for station in stations:
            station_name = station.get('StationName', '')
            
            # 提取座標資訊
            geo_info = station.get('GeoInfo', {})
            coordinates = geo_info.get('Coordinates', [])
            
            lat = 0.0
            lon = 0.0
            
            if coordinates and len(coordinates) > 0:
                coord = coordinates[0]
                lat = safe_parse_float(coord.get('StationLatitude'))
                lon = safe_parse_float(coord.get('StationLongitude'))
            
            # 提取行政區資訊
            town_name = geo_info.get('TownName', '')
            county_name = geo_info.get('CountyName', '')
            
            # 提取雨量資訊
            rainfall_element = station.get('RainfallElement', {})
            
            rain_1hr = 0.0
            rain_3hr = 0.0
            rain_24hr = 0.0
            
            if 'Past1hr' in rainfall_element:
                rain_1hr = safe_parse_float(rainfall_element['Past1hr'].get('Precipitation'))
            
            if 'Past3hr' in rainfall_element:
                rain_3hr = safe_parse_float(rainfall_element['Past3hr'].get('Precipitation'))
            
            if 'Past24hr' in rainfall_element:
                rain_24hr = safe_parse_float(rainfall_element['Past24hr'].get('Precipitation'))
            
            # 建立標準化資料
            station_data = {
                'station_name': station_name,
                'county_name': county_name,
                'town_name': f"{county_name}{town_name}",
                'latitude': lat,
                'longitude': lon,
                'rain_1hr': rain_1hr,
                'rain_3hr': rain_3hr,
                'rain_24hr': rain_24hr
            }
            
            normalized.append(station_data)
            
    except Exception as e:
        print(f"CWA 模擬資料標準化失敗: {e}")
    
    return normalized

def parse_rainfall_json(json_file_path):
    """解析雨量 JSON 資料為 GeoDataFrame"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 標準化資料
        normalized_data = normalize_cwa_json(data)
        
        if not normalized_data:
            print("無有效資料")
            return None
        
        # 轉換為 DataFrame
        df = pd.DataFrame(normalized_data)
        
        # 過濾有效座標
        valid_coords = (df['latitude'] != 0) & (df['longitude'] != 0)
        df_valid = df[valid_coords].copy()
        
        if len(df_valid) == 0:
            print("無有效座標資料")
            return None
        
        # 建立幾何點
        geometry = [Point(lon, lat) for lat, lon in zip(df_valid['latitude'], df_valid['longitude'])]
        
        # 建立 GeoDataFrame
        gdf = gpd.GeoDataFrame(
            df_valid,
            geometry=geometry,
            crs='EPSG:4326'  # WGS84
        )
        
        return gdf
        
    except Exception as e:
        print(f"資料解析失敗: {e}")
        return None

def main():
    """主要執行函式"""
    print("載入鳳凰颱風資料...")
    
    # 載入資料
    gdf_all = parse_rainfall_json('D:/114學年/遙測/windsurf_project/week6/week6_exercise6/fungwong_202511.json')
    
    if gdf_all is not None:
        print(f"載入 {len(gdf_all)} 個測站資料")
        
        # 篩選花蓮縣 + 宜蘭縣
        target_counties = ['花蓮縣', '宜蘭縣']
        study_rain = gdf_all[gdf_all['county_name'].isin(target_counties)].copy()
        print(f"篩選 {len(study_rain)} 個目標縣市測站")
        
        # 移除無效雨量站
        study_rain = study_rain[study_rain['rain_1hr'] > 0].copy()
        print(f"移除無效雨量站後剩餘 {len(study_rain)} 個測站")
        
        # 轉換至 EPSG:3826
        study_rain_3826 = study_rain.to_crs('EPSG:3826')
        print(f"轉換至 EPSG:3826: {study_rain_3826.crs}")
        
        # 提取座標陣列
        x = study_rain_3826.geometry.x.values  # Easting (meters)
        y = study_rain_3826.geometry.y.values  # Northing (meters)
        z = study_rain_3826['rain_1hr'].values
        
        print(f"\n研究區域測站統計 (rain > 0): {len(study_rain_3826)}")
        print(f"CRS: {study_rain_3826.crs}")
        print(f"\n前 5 個測站 (時雨量):")
        top5 = study_rain_3826.nlargest(5, 'rain_1hr')[['station_name', 'county_name', 'rain_1hr']]
        print(top5.to_string(index=False))
        
        # 顯示基本統計
        print(f"\n雨量統計:")
        print(f"  平均時雨量: {z.mean():.2f} mm/hr")
        print(f"  最大時雨量: {z.max():.2f} mm/hr")
        print(f"  最小時雨量: {z.min():.2f} mm/hr")
        
        return study_rain_3826, x, y, z
        
    else:
        print("資料載入失敗")
        return None, None, None, None

if __name__ == "__main__":
    study_rain_3826, x, y, z = main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 3: Define the Interpolation Grid & Run Kriging
Week 6 Spatial Prediction Shootout - Grid Interpolation Implementation

Author: thumbb44110-creator
Date: 2026-03-31
"""

import numpy as np
import matplotlib.pyplot as plt
import time
import warnings
from pykrige.ok import OrdinaryKriging
from cell1_data_processing import main

warnings.filterwarnings('ignore')

def calculate_grid_extent(x, y, buffer_m=5000):
    """計算網格範圍"""
    print("計算網格範圍...")
    
    x_min = x.min() - buffer_m
    x_max = x.max() + buffer_m
    y_min = y.min() - buffer_m
    y_max = y.max() + buffer_m
    
    print(f"  原始範圍: X({x.min():.0f}-{x.max():.0f}m), Y({y.min():.0f}-{y.max():.0f}m)")
    print(f"  緩衝後範圍: X({x_min:.0f}-{x_max:.0f}m), Y({y_min:.0f}-{y_max:.0f}m)")
    print(f"  緩衝區: {buffer_m}m")
    
    return x_min, x_max, y_min, y_max

def create_interpolation_grid(x_min, x_max, y_min, y_max, resolution=1000):
    """建立插值網格"""
    print(f"\n建立插值網格 (解析度: {resolution}m)...")
    
    # 使用 np.arange 建立網格座標
    grid_x = np.arange(x_min, x_max, resolution)
    grid_y = np.arange(y_min, y_max, resolution)
    
    # 網格統計
    grid_size = len(grid_x) * len(grid_y)
    grid_width_km = (x_max - x_min) / 1000
    grid_height_km = (y_max - y_min) / 1000
    
    print(f"  網格尺寸: {len(grid_x)} × {len(grid_y)} = {grid_size:,} 點")
    print(f"  覆蓋範圍: {grid_width_km:.1f} × {grid_height_km:.1f} km")
    print(f"  預估記憶體: ~{grid_size * 8 / 1024 / 1024:.1f} MB (每個陣列)")
    
    return grid_x, grid_y

def setup_kriging_model(x, y, z_log):
    """設置 Kriging 模型"""
    print("\n設置 Kriging 模型...")
    
    # 基於 log-transform 資料的參數
    initial_sill = float(z_log.var())
    initial_range = 50000.0  # 50km
    initial_nugget = float(z_log.var() * 0.1)
    
    print(f"  初始參數 (log-space):")
    print(f"    Sill:   {initial_sill:.3f}")
    print(f"    Range:  {initial_range/1000:.1f} km")
    print(f"    Nugget: {initial_nugget:.3f}")
    
    # 建立 Ordinary Kriging 模型
    OK = OrdinaryKriging(x, y, z_log, variogram_model='spherical',
                        verbose=False, enable_plotting=False, nlags=15,
                        variogram_parameters={
                            'sill': initial_sill,
                            'range': initial_range,
                            'nugget': initial_nugget
                        })
    
    # 獲取擬合參數
    fitted_params = OK.variogram_model_parameters
    print(f"  擬合參數:")
    print(f"    Sill:   {fitted_params[0]:.3f}")
    print(f"    Range:  {fitted_params[1]/1000:.1f} km")
    print(f"    Nugget: {fitted_params[2]:.3f}")
    
    return OK

def execute_kriging_prediction(OK, grid_x, grid_y):
    """執行 Kriging 預測"""
    print(f"\n執行 Kriging 預測...")
    print(f"  網格點數: {len(grid_x) * len(grid_y):,}")
    
    # 計時開始
    t0 = time.time()
    
    # 在對數空間執行 Kriging
    z_kriging_log, ss_kriging_log = OK.execute('grid', grid_x, grid_y)
    
    # 計時結束
    execution_time = time.time() - t0
    
    print(f"  * Kriging (log-space) 完成，耗時 {execution_time:.1f}s")
    print(f"  輸出陣列形狀: {z_kriging_log.shape}")
    
    return z_kriging_log, ss_kriging_log, execution_time

def transform_predictions(z_kriging_log, ss_kriging_log):
    """轉換預測結果回原始單位"""
    print("\n轉換預測結果...")
    
    # 轉換回原始雨量單位
    z_kriging = np.expm1(z_kriging_log)
    
    # 處理負值（物理限制）
    negative_count = np.sum(z_kriging < 0)
    if negative_count > 0:
        print(f"  警告: 發現 {negative_count} 個負值，設為 0")
        z_kriging[z_kriging < 0] = 0
    
    # 保留對數空間的變異數用於不確定性分析
    ss_kriging = ss_kriging_log
    
    # 統計資訊
    z_min = np.nanmin(z_kriging)
    z_max = np.nanmax(z_kriging)
    z_mean = np.nanmean(z_kriging)
    
    print(f"  預測值範圍: {z_min:.1f} - {z_max:.1f} mm/hr")
    print(f"  預測值平均: {z_mean:.1f} mm/hr")
    print(f"  不確定性範圍: {np.nanmin(ss_kriging):.3f} - {np.nanmax(ss_kriging):.3f}")
    
    return z_kriging, ss_kriging

def validate_results(z_kriging, ss_kriging, grid_x, grid_y, x, y, z):
    """驗證結果合理性"""
    print("\n驗證結果合理性...")
    
    # 基本檢查
    nan_count_z = np.sum(np.isnan(z_kriging))
    nan_count_ss = np.sum(np.isnan(ss_kriging))
    
    print(f"  NaN 檢查:")
    print(f"    預測值 NaN: {nan_count_z}")
    print(f"    不確定性 NaN: {nan_count_ss}")
    
    # 與原始資料比較
    original_min = z.min()
    original_max = z.max()
    predicted_min = np.nanmin(z_kriging)
    predicted_max = np.nanmax(z_kriging)
    
    print(f"\n  原始資料 vs 預測結果:")
    print(f"    原始範圍: {original_min:.1f} - {original_max:.1f} mm/hr")
    print(f"    預測範圍: {predicted_min:.1f} - {predicted_max:.1f} mm/hr")
    
    # 範圍合理性檢查
    if predicted_min < 0:
        print("  ⚠️  警告: 預測值包含負值")
    if predicted_max > original_max * 2:
        print("  ⚠️  警告: 預測最大值遠大於原始最大值")
    
    # 網格覆蓋檢查
    grid_extent_x = (grid_x.min(), grid_x.max())
    grid_extent_y = (grid_y.min(), grid_y.max())
    data_extent_x = (x.min(), x.max())
    data_extent_y = (y.min(), y.max())
    
    print(f"\n  網格覆蓋檢查:")
    print(f"    網格 X 範圍: {grid_extent_x[0]:.0f} - {grid_extent_x[1]:.0f}m")
    print(f"    資料 X 範圍: {data_extent_x[0]:.0f} - {data_extent_x[1]:.0f}m")
    print(f"    網格 Y 範圍: {grid_extent_y[0]:.0f} - {grid_extent_y[1]:.0f}m")
    print(f"    資料 Y 範圍: {data_extent_y[0]:.0f} - {data_extent_y[1]:.0f}m")
    
    coverage_ok = (grid_extent_x[0] <= data_extent_x[0] and 
                  grid_extent_x[1] >= data_extent_x[1] and
                  grid_extent_y[0] <= data_extent_y[0] and 
                  grid_extent_y[1] >= data_extent_y[1])
    
    print(f"    覆蓋完整性: {'* 通過' if coverage_ok else 'X 失敗'}")

def create_summary_report(grid_x, grid_y, z_kriging, ss_kriging, execution_time, 
                        buffer_m, resolution):
    """建立摘要報告"""
    print("\n" + "="*60)
    print("Cell 3: 插值網格與 Kriging 執行摘要")
    print("="*60)
    
    grid_points = len(grid_x) * len(grid_y)
    coverage_area_km2 = ((grid_x.max() - grid_x.min()) / 1000) * ((grid_y.max() - grid_y.min()) / 1000)
    
    print(f"\n網格設定:")
    print(f"  解析度: {resolution}m")
    print(f"  緩衝區: {buffer_m}m")
    print(f"  網格點數: {grid_points:,}")
    print(f"  覆蓋面積: {coverage_area_km2:.1f} km^2")
    
    print(f"\n執行效能:")
    print(f"  執行時間: {execution_time:.1f}s")
    print(f"  處理速度: {grid_points/execution_time:.0f} 點/秒")
    
    print(f"\n預測結果:")
    print(f"  雨量範圍: {np.nanmin(z_kriging):.1f} - {np.nanmax(z_kriging):.1f} mm/hr")
    print(f"  平均雨量: {np.nanmean(z_kriging):.1f} mm/hr")
    print(f"  不確定性範圍: {np.nanmin(ss_kriging):.3f} - {np.nanmax(ss_kriging):.3f}")
    
    print(f"\n輸出變數:")
    print(f"  - z_kriging: 2D 陣列, 插值雨量 (mm/hr)")
    print(f"  - ss_kriging: 2D 陣列, 預測不確定性")
    print(f"  - grid_x, grid_y: 1D 陣列, 網格座標")
    
    print("\n" + "="*60)

def main_cell3_execution():
    """Cell 3 主要執行函式"""
    print("Cell 3: Define the Interpolation Grid & Run Kriging")
    print("="*60)
    
    # 載入資料
    print("載入前置資料...")
    study_rain_3826, x, y, z = main()
    
    if study_rain_3826 is None:
        print("無法載入資料，終止執行")
        return None, None, None, None
    
    print(f"成功載入 {len(z)} 個測站資料")
    
    # 計算 log-transform
    z_log = np.log1p(z)
    print(f"完成 log-transform，偏態從 {np.sum(((z - z.mean()) / z.std()) ** 3) / len(z):.2f} 降至 {np.sum(((z_log - z_log.mean()) / z_log.std()) ** 3) / len(z_log):.2f}")
    
    # Phase 1: 計算網格範圍
    buffer_m = 5000
    x_min, x_max, y_min, y_max = calculate_grid_extent(x, y, buffer_m)
    
    # Phase 2: 建立插值網格
    resolution = 1000
    grid_x, grid_y = create_interpolation_grid(x_min, x_max, y_min, y_max, resolution)
    
    # Phase 3: 設置 Kriging 模型
    OK = setup_kriging_model(x, y, z_log)
    
    # Phase 4: 執行 Kriging 預測
    z_kriging_log, ss_kriging_log, execution_time = execute_kriging_prediction(OK, grid_x, grid_y)
    
    # Phase 5: 轉換預測結果
    z_kriging, ss_kriging = transform_predictions(z_kriging_log, ss_kriging_log)
    
    # Phase 6: 驗證結果
    validate_results(z_kriging, ss_kriging, grid_x, grid_y, x, y, z)
    
    # Phase 7: 生成摘要報告
    create_summary_report(grid_x, grid_y, z_kriging, ss_kriging, execution_time, 
                        buffer_m, resolution)
    
    print(f"\n* Cell 3 執行完成！")
    print(f"  網格尺寸: {len(grid_x)} × {len(grid_y)}")
    print(f"  預測範圍: {np.nanmin(z_kriging):.1f} - {np.nanmax(z_kriging):.1f} mm/hr")
    print(f"  執行時間: {execution_time:.1f}s")
    
    return {
        'z_kriging': z_kriging,
        'ss_kriging': ss_kriging,
        'grid_x': grid_x,
        'grid_y': grid_y,
        'execution_time': execution_time
    }

if __name__ == "__main__":
    results = main_cell3_execution()

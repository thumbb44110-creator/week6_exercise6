#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 6 插值測試腳本
Lab 1: Nearest Neighbor + IDW 插值測試

Author: thumbb44110-creator
Date: 2026-04-03
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import NearestNDInterpolator
from scipy.spatial.distance import cdist
import sys
import os

def create_test_data():
    """建立測試資料"""
    print("建立測試資料...")
    
    # 模擬測站座標和雨量資料
    np.random.seed(42)
    n_stations = 20
    
    # 在矩形區域內隨機分佈測站
    x = np.random.uniform(100000, 200000, n_stations)  # Easting
    y = np.random.uniform(2500000, 2600000, n_stations)  # Northing
    
    # 模擬雨量資料（包含一些極端值）
    z = np.random.exponential(10, n_stations)  # 指數分佈，模擬雨量
    z = np.clip(z, 0.5, 100)  # 限制在合理範圍內
    
    # 建立網格
    grid_x = np.arange(95000, 205000, 5000)  # 5000m 解析度
    grid_y = np.arange(2495000, 2605000, 5000)
    
    print(f"* 測試資料建立完成:")
    print(f"  測站數量: {len(x)}")
    print(f"  網格尺寸: {len(grid_x)}×{len(grid_y)} = {len(grid_x)*len(grid_y)} 點")
    print(f"  雨量範圍: {z.min():.2f} - {z.max():.2f} mm/hr")
    
    return x, y, z, grid_x, grid_y

def test_nearest_neighbor(x, y, z, grid_x, grid_y):
    """測試 Nearest Neighbor 插值"""
    print("\n" + "="*50)
    print("測試 Nearest Neighbor 插值")
    print("="*50)
    
    try:
        # 建立網格矩陣
        grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)
        
        # Nearest Neighbor 插值
        nn_interp = NearestNDInterpolator(np.column_stack([x, y]), z)
        z_nn = nn_interp(grid_xx, grid_yy)
        
        # 驗證結果
        print(f"* Nearest Neighbor 插值成功")
        print(f"  預測範圍: {np.nanmin(z_nn):.2f} - {np.nanmax(z_nn):.2f} mm/hr")
        print(f"  平均值: {np.nanmean(z_nn):.2f} mm/hr")
        print(f"  NaN 數量: {np.isnan(z_nn).sum()}")
        
        # 檢查是否在原始資料範圍內
        if np.nanmin(z_nn) >= z.min() and np.nanmax(z_nn) <= z.max():
            print("* 範圍檢查通過")
        else:
            print("! 範圍檢查失敗")
        
        return z_nn, True
        
    except Exception as e:
        print(f"! Nearest Neighbor 插值失敗: {e}")
        return None, False

def test_idw(x, y, z, grid_x, grid_y):
    """測試 IDW 插值"""
    print("\n" + "="*50)
    print("測試 IDW 插值 (power=2)")
    print("="*50)
    
    try:
        # 建立網格矩陣
        grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)
        
        # IDW 插值
        obs_points = np.column_stack([x, y])
        pred_points = np.column_stack([grid_xx.ravel(), grid_yy.ravel()])
        
        # 計算距離矩陣
        distances = cdist(pred_points, obs_points)
        
        # 避免除零
        distances[distances < 1e-10] = 1e-10
        
        # 計算權重 (power=2)
        power = 2
        weights = 1.0 / (distances ** power)
        
        # 權重標準化
        weights = weights / weights.sum(axis=1, keepdims=True)
        
        # 加權平均
        z_pred = np.dot(weights, z)
        z_idw = z_pred.reshape(grid_xx.shape)
        
        # 驗證結果
        print(f"* IDW 插值成功")
        print(f"  預測範圍: {np.nanmin(z_idw):.2f} - {np.nanmax(z_idw):.2f} mm/hr")
        print(f"  平均值: {np.nanmean(z_idw):.2f} mm/hr")
        print(f"  NaN 數量: {np.isnan(z_idw).sum()}")
        
        # 檢查是否在原始資料範圍內
        if np.nanmin(z_idw) >= z.min() and np.nanmax(z_idw) <= z.max():
            print("* 範圍檢查通過")
        else:
            print("! 範圍檢查失敗")
        
        return z_idw, True
        
    except Exception as e:
        print(f"! IDW 插值失敗: {e}")
        return None, False

def create_comparison_plot(z_nn, z_idw, grid_x, grid_y, x, y, z):
    """建立比較圖表"""
    print("\n" + "="*50)
    print("建立比較圖表")
    print("="*50)
    
    try:
        # 建立圖表
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        
        # 計算網格範圍
        x_min, x_max = grid_x.min(), grid_x.max()
        y_min, y_max = grid_y.min(), grid_y.max()
        
        # 統一色彩範圍
        vmin, vmax = 0, max(np.nanmax(z_nn), np.nanmax(z_idw))
        
        # Nearest Neighbor
        im1 = axes[0].imshow(z_nn, extent=[x_min, x_max, y_min, y_max], 
                            origin='lower', cmap='YlOrRd', vmin=vmin, vmax=vmax)
        axes[0].set_title('Nearest Neighbor 插值', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Easting (m)')
        axes[0].set_ylabel('Northing (m)')
        
        # 添加測站點
        axes[0].scatter(x, y, c=z, s=50, edgecolors='black', linewidths=1, 
                       cmap='YlOrRd', vmin=vmin, vmax=vmax, alpha=0.8)
        plt.colorbar(im1, ax=axes[0], label='Rainfall (mm/hr)')
        
        # IDW
        im2 = axes[1].imshow(z_idw, extent=[x_min, x_max, y_min, y_max], 
                            origin='lower', cmap='YlOrRd', vmin=vmin, vmax=vmax)
        axes[1].set_title('IDW 插值 (power=2)', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Easting (m)')
        axes[1].set_ylabel('Northing (m)')
        
        # 添加測站點
        axes[1].scatter(x, y, c=z, s=50, edgecolors='black', linewidths=1, 
                       cmap='YlOrRd', vmin=vmin, vmax=vmax, alpha=0.8)
        plt.colorbar(im2, ax=axes[1], label='Rainfall (mm/hr)')
        
        # 總標題
        fig.suptitle('Cell 6 測試: Nearest Neighbor vs IDW 插值比較', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        plt.savefig('test_cell6_interpolation.png', dpi=300, bbox_inches='tight')
        print("* 圖表已儲存: test_cell6_interpolation.png")
        plt.show()
        
        return True
        
    except Exception as e:
        print(f"! 圖表建立失敗: {e}")
        return False

def run_performance_test():
    """執行效能測試"""
    print("\n" + "="*50)
    print("效能測試")
    print("="*50)
    
    import time
    
    # 建立較大的測試資料
    n_stations = 100
    grid_size = 100
    
    x = np.random.uniform(100000, 200000, n_stations)
    y = np.random.uniform(2500000, 2600000, n_stations)
    z = np.random.exponential(10, n_stations)
    
    grid_x = np.linspace(100000, 200000, grid_size)
    grid_y = np.linspace(2500000, 2600000, grid_size)
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)
    
    total_points = grid_size * grid_size
    print(f"測試規模: {n_stations} 測站, {total_points:,} 網格點")
    
    # 測試 Nearest Neighbor
    start_time = time.time()
    nn_interp = NearestNDInterpolator(np.column_stack([x, y]), z)
    z_nn = nn_interp(grid_xx, grid_yy)
    nn_time = time.time() - start_time
    
    print(f"Nearest Neighbor: {nn_time:.3f} 秒 ({total_points/nn_time:.0f} 點/秒)")
    
    # 測試 IDW
    start_time = time.time()
    obs_points = np.column_stack([x, y])
    pred_points = np.column_stack([grid_xx.ravel(), grid_yy.ravel()])
    distances = cdist(pred_points, obs_points)
    distances[distances < 1e-10] = 1e-10
    weights = 1.0 / (distances ** 2)
    weights = weights / weights.sum(axis=1, keepdims=True)
    z_pred = np.dot(weights, z)
    z_idw = z_pred.reshape(grid_xx.shape)
    idw_time = time.time() - start_time
    
    print(f"IDW: {idw_time:.3f} 秒 ({total_points/idw_time:.0f} 點/秒)")
    
    print(f"效能比較: IDW/NN = {idw_time/nn_time:.1f}x")

def main():
    """主要測試函數"""
    print("Cell 6 插值測試開始")
    print("=" * 60)
    
    # 建立測試資料
    x, y, z, grid_x, grid_y = create_test_data()
    
    # 測試 Nearest Neighbor
    z_nn, nn_success = test_nearest_neighbor(x, y, z, grid_x, grid_y)
    
    # 測試 IDW
    z_idw, idw_success = test_idw(x, y, z, grid_x, grid_y)
    
    # 如果兩種方法都成功，建立比較圖表
    if nn_success and idw_success:
        plot_success = create_comparison_plot(z_nn, z_idw, grid_x, grid_y, x, y, z)
        
        # 效能測試
        run_performance_test()
        
        # 總結
        print("\n" + "="*60)
        print("* Cell 6 測試完成！")
        print("="*60)
        print("測試結果:")
        print(f"  Nearest Neighbor: {'* 成功' if nn_success else '! 失敗'}")
        print(f"  IDW: {'* 成功' if idw_success else '! 失敗'}")
        print(f"  比較圖表: {'* 成功' if plot_success else '! 失敗'}")
        print("\n生成檔案:")
        print("  - test_cell6_interpolation.png")
        
        if nn_success and idw_success:
            print("\n統計摘要:")
            print(f"  NN 範圍: {np.nanmin(z_nn):.2f} - {np.nanmax(z_nn):.2f} mm/hr")
            print(f"  IDW 範圍: {np.nanmin(z_idw):.2f} - {np.nanmax(z_idw):.2f} mm/hr")
            print(f"  原始範圍: {z.min():.2f} - {z.max():.2f} mm/hr")
        
        return True
    else:
        print("! 測試失敗，請檢查錯誤訊息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

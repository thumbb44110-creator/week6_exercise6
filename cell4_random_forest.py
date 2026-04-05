#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 4: Machine Learning — Random Forest Prediction (Slide 9)
Week 6 Spatial Prediction Shootout - Random Forest Implementation

Author: thumbb44110-creator
Date: 2026-04-01

Description: 使用 Random Forest 演算法進行空間降雨預測
             將座標作為輸入特徵，預測雨量分佈
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import time
import warnings
from typing import Tuple, Optional
warnings.filterwarnings('ignore')

def load_previous_results():
    """載入之前 Cell 的處理結果"""
    try:
        # 嘗試載入 Cell 1 的資料
        from cell1_data_processing import main
        study_rain_3826, x, y, z = main()
        
        # 嘗試載入 Cell 3 的網格
        try:
            from cell3_grid_interpolation import load_grid_data
            grid_x, grid_y = load_grid_data()
            print("Successfully loaded Cell 1 and Cell 3 data")
        except (ImportError, AttributeError):
            print("Cannot load Cell 3 grid, creating new one")
            grid_x, grid_y = create_interpolation_grid(x, y)
        
        return study_rain_3826, x, y, z, grid_x, grid_y
        
    except ImportError as e:
        print(f"Cannot load dependency data: {e}")
        return None, None, None, None, None, None

def create_interpolation_grid(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """建立插值網格 (與 Cell 3 相同的設定)"""
    buffer_m = 5000
    resolution = 1000  # meters
    
    x_min = x.min() - buffer_m
    x_max = x.max() + buffer_m
    y_min = y.min() - buffer_m
    y_max = y.max() + buffer_m
    
    grid_x = np.arange(x_min, x_max, resolution)
    grid_y = np.arange(y_min, y_max, resolution)
    
    print(f"建立網格: {len(grid_x)}×{len(grid_y)} = {len(grid_x)*len(grid_y):,} 點 @ {resolution}m")
    return grid_x, grid_y

def validate_input_data(x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                       grid_x: np.ndarray, grid_y: np.ndarray) -> bool:
    """驗證輸入資料的完整性和合理性"""
    print("驗證輸入資料...")
    
    # 檢查基本維度
    if not (len(x) == len(y) == len(z)):
        print(f"Coordinate and rainfall dimensions mismatch: x={len(x)}, y={len(y)}, z={len(z)}")
        return False
    
    # 檢查數值範圍
    if len(x) == 0 or len(y) == 0 or len(z) == 0:
        print("Input data is empty")
        return False
    
    # 檢查網格資料
    if len(grid_x) == 0 or len(grid_y) == 0:
        print("Grid data is empty")
        return False
    
    # 檢查座標範圍合理性 (EPSG:3826 範圍)
    if not (200000 < x.min() < 400000 and 200000 < y.min() < 3000000):
        print(f"Coordinate range may be incorrect: X({x.min():.0f}-{x.max():.0f}), Y({y.min():.0f}-{y.max():.0f})")
    
    # 檢查雨量範圍
    if z.min() < 0 or z.max() > 500:
        print(f"Rainfall range abnormal: {z.min():.1f} - {z.max():.1f} mm/hr")
    
    print(f"Data validation passed: {len(z)} stations, grid {len(grid_x)}x{len(grid_y)}")
    return True

def prepare_training_data(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """準備訓練資料"""
    print("準備訓練資料...")
    
    # 組合座標特徵
    X_train = np.column_stack([x, y])
    y_train = z
    
    print(f"訓練資料維度: X_train{X_train.shape}, y_train{y_train.shape}")
    print(f"座標範圍: X({X_train[:, 0].min():.0f}-{X_train[:, 0].max():.0f}), Y({X_train[:, 1].min():.0f}-{X_train[:, 1].max():.0f})")
    print(f"雨量範圍: {y_train.min():.1f} - {y_train.max():.1f} mm/hr")
    
    return X_train, y_train

def train_random_forest(X_train: np.ndarray, y_train: np.ndarray) -> Tuple[RandomForestRegressor, float]:
    """訓練 Random Forest 模型"""
    print("訓練 Random Forest 模型...")
    
    # 模型初始化
    rf = RandomForestRegressor(
        n_estimators=200,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1  # 使用所有 CPU 核心
    )
    
    # 訓練模型
    start_time = time.time()
    rf.fit(X_train, y_train)
    training_time = time.time() - start_time
    
    # 計算訓練 R²
    train_r2 = rf.score(X_train, y_train)
    
    print(f"✓ 模型訓練完成 (耗時: {training_time:.2f}秒)")
    print(f"訓練集 R² 分數: {train_r2:.4f}")
    
    # 特徵重要性
    feature_names = ['Easting', 'Northing']
    importances = rf.feature_importances_
    print("特徵重要性:")
    for name, importance in zip(feature_names, importances):
        print(f"  {name}: {importance:.3f}")
    
    return rf, training_time

def create_prediction_grid(grid_x: np.ndarray, grid_y: np.ndarray) -> np.ndarray:
    """建立預測網格"""
    print("建立預測網格...")
    
    # 建立 meshgrid
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)
    
    # 重塑為預測格式
    X_pred = np.column_stack([grid_xx.ravel(), grid_yy.ravel()])
    
    print(f"預測網格維度: {X_pred.shape}")
    print(f"網格範圍: X({X_pred[:, 0].min():.0f}-{X_pred[:, 0].max():.0f}), Y({X_pred[:, 1].min():.0f}-{X_pred[:, 1].max():.0f})")
    
    return X_pred, grid_xx.shape

def predict_on_grid(rf: RandomForestRegressor, X_pred: np.ndarray, grid_shape: Tuple[int, int]) -> Tuple[np.ndarray, float]:
    """在網格上執行預測"""
    print("執行網格預測...")
    
    start_time = time.time()
    z_pred = rf.predict(X_pred)
    prediction_time = time.time() - start_time
    
    # 重塑為網格格式
    z_rf = z_pred.reshape(grid_shape)
    
    print(f"✓ 預測完成 (耗時: {prediction_time:.2f}秒)")
    print(f"預測值範圍: {z_rf.min():.1f} - {z_rf.max():.1f} mm/hr")
    print(f"預測平均值: {z_rf.mean():.1f} mm/hr")
    
    return z_rf, prediction_time

def validate_predictions(z_rf: np.ndarray, original_z: np.ndarray) -> bool:
    """驗證預測結果的合理性"""
    print("驗證預測結果...")
    
    # 檢查基本統計
    pred_min, pred_max = z_rf.min(), z_rf.max()
    orig_min, orig_max = original_z.min(), original_z.max()
    
    print(f"原始雨量範圍: {orig_min:.1f} - {orig_max:.1f} mm/hr")
    print(f"預測雨量範圍: {pred_min:.1f} - {pred_max:.1f} mm/hr")
    
    # 檢查異常值
    if pred_min < 0:
        print(f"⚠ 預測包含負值: {pred_min:.1f}")
        z_rf[z_rf < 0] = 0
        print("✓ 負值已修正為 0")
    
    if pred_max > orig_max * 2:
        print(f"⚠ 預測最大值異常高: {pred_max:.1f} mm/hr")
    
    # 檢查 NaN
    nan_count = np.isnan(z_rf).sum()
    if nan_count > 0:
        print(f"❌ 預測包含 {nan_count} 個 NaN 值")
        return False
    
    print("✓ 預測驗證通過")
    return True

def save_results(z_rf: np.ndarray, grid_x: np.ndarray, grid_y: np.ndarray, 
                 training_time: float, prediction_time: float, train_r2: float):
    """儲存預測結果"""
    print("儲存預測結果...")
    
    # 儲存 NumPy 陣列
    try:
        np.savez('cell4_random_forest_results.npz',
                z_rf=z_rf,
                grid_x=grid_x,
                grid_y=grid_y)
        print("✓ 結果已儲存至 cell4_random_forest_results.npz")
    except Exception as e:
        print(f"❌ 儲存失敗: {e}")
    
    # 建立結果摘要
    summary = {
        'method': 'Random Forest',
        'training_time_seconds': training_time,
        'prediction_time_seconds': prediction_time,
        'train_r2_score': train_r2,
        'grid_shape': z_rf.shape,
        'prediction_range_mm_hr': (float(z_rf.min()), float(z_rf.max())),
        'prediction_mean_mm_hr': float(z_rf.mean()),
        'total_points': int(z_rf.size)
    }
    
    try:
        pd.Series(summary).to_json('cell4_random_forest_summary.json')
        print("✓ 摘要已儲存至 cell4_random_forest_summary.json")
    except Exception as e:
        print(f"❌ 摘要儲存失敗: {e}")

def create_visualization(z_rf: np.ndarray, grid_x: np.ndarray, grid_y: np.ndarray, 
                       x: np.ndarray, y: np.ndarray, z: np.ndarray):
    """建立結果可視化"""
    print("建立可視化圖表...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # 左圖：Random Forest 預測結果
    im1 = axes[0].imshow(z_rf, extent=[grid_x.min(), grid_x.max(), grid_y.min(), grid_y.max()],
                       origin='lower', cmap='YlOrRd', aspect='auto')
    axes[0].scatter(x, y, c=z, s=50, cmap='YlOrRd', edgecolors='black', linewidths=1)
    axes[0].set_title('Random Forest 預測結果', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Easting (m)')
    axes[0].set_ylabel('Northing (m)')
    plt.colorbar(im1, ax=axes[0], label='雨量 (mm/hr)')
    
    # 右圖：預測值分佈直方圖
    axes[1].hist(z_rf.ravel(), bins=50, color='steelblue', edgecolor='black', alpha=0.7)
    axes[1].axvline(z_rf.mean(), color='red', linestyle='--', label=f'平均: {z_rf.mean():.1f}')
    axes[1].set_title('預測值分佈', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('雨量 (mm/hr)')
    axes[1].set_ylabel('網格點數量')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('cell4_random_forest_results.png', dpi=300, bbox_inches='tight')
    print("✓ 可視化已儲存至 cell4_random_forest_results.png")
    plt.show()

def main():
    """主要執行函式"""
    print("="*60)
    print("Cell 4: Machine Learning — Random Forest Prediction")
    print("="*60)
    
    # 載入依賴資料
    study_rain_3826, x, y, z, grid_x, grid_y = load_previous_results()
    
    if any(v is None for v in [x, y, z, grid_x, grid_y]):
        print("❌ 無法載入必要資料，終止執行")
        return None
    
    # 驗證輸入資料
    if not validate_input_data(x, y, z, grid_x, grid_y):
        print("❌ 輸入資料驗證失敗，終止執行")
        return None
    
    # Phase 1: 資料準備
    X_train, y_train = prepare_training_data(x, y, z)
    
    # Phase 2: 模型訓練
    rf, training_time = train_random_forest(X_train, y_train)
    
    # Phase 3: 網格預測
    X_pred, grid_shape = create_prediction_grid(grid_x, grid_y)
    z_rf, prediction_time = predict_on_grid(rf, X_pred, grid_shape)
    
    # Phase 4: 結果驗證
    if not validate_predictions(z_rf, z):
        print("❌ 預測驗證失敗")
        return None
    
    # 儲存結果
    train_r2 = rf.score(X_train, y_train)
    save_results(z_rf, grid_x, grid_y, training_time, prediction_time, train_r2)
    
    # 建立可視化
    create_visualization(z_rf, grid_x, grid_y, x, y, z)
    
    print("\n" + "="*60)
    print("Cell 4 Random Forest 實作完成！")
    print("="*60)
    print(f"訓練時間: {training_time:.2f}秒")
    print(f"預測時間: {prediction_time:.2f}秒")
    print(f"訓練 R²: {train_r2:.4f}")
    print(f"預測網格: {z_rf.shape}")
    print(f"預測範圍: {z_rf.min():.1f} - {z_rf.max():.1f} mm/hr")
    print("輸出變數: z_rf (可用於後續比較)")
    
    return z_rf, rf, grid_x, grid_y

if __name__ == "__main__":
    results = main()

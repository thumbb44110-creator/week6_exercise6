#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Cell 4 Random Forest Implementation
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

# Test data (mock)
print("Testing Cell 4 Random Forest implementation...")

# Create mock data
np.random.seed(42)
n_stations = 89
x = np.random.uniform(269261, 346034, n_stations)  # Easting
y = np.random.uniform(2563311, 2763948, n_stations)  # Northing  
z = np.random.exponential(12.37, n_stations)  # Rainfall (skewed distribution)
z = np.maximum(z, 0.5)  # Minimum rainfall

# Create grid
grid_x = np.arange(264261, 351034, 1000)  # 87 points
grid_y = np.arange(2558311, 2773948, 1000)  # 211 points

print(f"Mock data created: {n_stations} stations")
print(f"Grid: {len(grid_x)}x{len(grid_y)} = {len(grid_x)*len(grid_y)} points")

# Test Random Forest
print("\n=== Testing Random Forest ===")

# Phase 1: 準備訓練資料
X_train = np.column_stack([x, y])
y_train = z

print(f"Training data: X_train{X_train.shape}, y_train{y_train.shape}")

# Phase 2: 訓練模型
rf = RandomForestRegressor(n_estimators=200, min_samples_leaf=3, random_state=42)
rf.fit(X_train, y_train)
train_r2 = rf.score(X_train, y_train)

print(f"Training R2: {train_r2:.4f}")

# Phase 3: 網格預測
grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)
X_pred = np.column_stack([grid_xx.ravel(), grid_yy.ravel()])
z_pred = rf.predict(X_pred)
z_rf = z_pred.reshape(grid_xx.shape)

print(f"Prediction completed: {z_rf.shape}")
print(f"Prediction range: {z_rf.min():.1f} - {z_rf.max():.1f} mm/hr")

# Phase 4: 驗證
if z_rf.min() < 0:
    z_rf[z_rf < 0] = 0
    print("Negative values corrected")

nan_count = np.isnan(z_rf).sum()
print(f"NaN values: {nan_count}")

print("\n* Cell 4 Random Forest test completed successfully!")
print("Ready to run in Jupyter Notebook.")

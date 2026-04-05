# Cell 4: Machine Learning — Random Forest Prediction (Slide 9)
# Notebook 版本程式碼 - 直接複製到 Jupyter Notebook 中執行

from sklearn.ensemble import RandomForestRegressor
import numpy as np
import time

# Phase 1: 準備訓練資料
print("=== Phase 1: 資料準備 ===")

# 準備特徵和目標變數
X_train = np.column_stack([x, y])  # 特徵: [easting, northing]
y_train = z  # 目標: 雨量

print(f"訓練資料維度: X_train{X_train.shape}, y_train{y_train.shape}")
print(f"座標範圍: X({X_train[:, 0].min():.0f}-{X_train[:, 0].max():.0f}), Y({X_train[:, 1].min():.0f}-{X_train[:, 1].max():.0f})")
print(f"雨量範圍: {y_train.min():.1f} - {y_train.max():.1f} mm/hr")

# Phase 2: 訓練 Random Forest 模型
print("\n=== Phase 2: 模型訓練 ===")

# 初始化 Random Forest
rf = RandomForestRegressor(n_estimators=200, min_samples_leaf=3, random_state=42)

# 訓練模型
start_time = time.time()
rf.fit(X_train, y_train)
training_time = time.time() - start_time

# 評估訓練效果
train_r2 = rf.score(X_train, y_train)
print(f"訓練時間: {training_time:.2f}秒")
print(f"訓練集 R² 分數: {train_r2:.4f}")

# 顯示特徵重要性
feature_names = ['Easting', 'Northing']
importances = rf.feature_importances_
print("特徵重要性:")
for name, importance in zip(feature_names, importances):
    print(f"  {name}: {importance:.3f}")

# Phase 3: 網格預測
print("\n=== Phase 3: 網格預測 ===")

# 建立預測網格
grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)
X_pred = np.column_stack([grid_xx.ravel(), grid_yy.ravel()])

print(f"預測網格維度: {X_pred.shape}")

# 執行預測
start_time = time.time()
z_pred = rf.predict(X_pred)
prediction_time = time.time() - start_time

# 重塑為網格格式
z_rf = z_pred.reshape(grid_xx.shape)

print(f"預測時間: {prediction_time:.2f}秒")
print(f"預測值範圍: {z_rf.min():.1f} - {z_rf.max():.1f} mm/hr")
print(f"預測平均值: {z_rf.mean():.1f} mm/hr")

# Phase 4: 結果驗證
print("\n=== Phase 4: 結果驗證 ===")

# 檢查預測值合理性
print(f"原始雨量範圍: {z.min():.1f} - {z.max():.1f} mm/hr")
print(f"預測雨量範圍: {z_rf.min():.1f} - {z_rf.max():.1f} mm/hr")

# 處理負值
if z_rf.min() < 0:
    print(f"修正負值: {z_rf.min():.1f} -> 0")
    z_rf[z_rf < 0] = 0

# 檢查 NaN
nan_count = np.isnan(z_rf).sum()
print(f"NaN 值數量: {nan_count}")

print("\n=== Random Forest 預測完成 ===")
print(f"輸出變數: z_rf (形狀: {z_rf.shape})")
print("✓ 可用於後續方法比較")

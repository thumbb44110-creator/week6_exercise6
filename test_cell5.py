#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Cell 5 Feature Importance Implementation
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

# Test data (mock)
print("Testing Cell 5 Feature Importance implementation...")

# Create mock Random Forest model
np.random.seed(42)
n_stations = 89
x = np.random.uniform(269261, 346034, n_stations)
y = np.random.uniform(2563311, 2763948, n_stations)
z = np.random.exponential(12.37, n_stations)

# Train mock model
X_train = np.column_stack([x, y])
rf = RandomForestRegressor(n_estimators=200, min_samples_leaf=3, random_state=42)
rf.fit(X_train, z)

print("Mock Random Forest model created")

# Test Cell 5 functionality
print("\n=== Phase 1: 特徵重要性提取 ===")

importances = rf.feature_importances_
print("Feature Importance:")
print(f"  Easting (X):  {importances[0]:.3f} ({importances[0]*100:.1f}%)")
print(f"  Northing (Y): {importances[1]:.3f} ({importances[1]*100:.1f}%)")

dominant_feature = 'easting' if importances[0] > importances[1] else 'northing'
importance_diff = abs(importances[0] - importances[1])

print(f"\n模型主要依賴: {dominant_feature}")
print(f"重要性差異: {importance_diff:.3f}")

print("\n=== Phase 2: 物理意義解釋 ===")

if importance_diff < 0.05:
    print("分析結果: 兩個維度重要性相當")
    print("物理意義: 颱風降雨在空間分佈相對均勻")
elif dominant_feature == 'easting':
    print("分析結果: 東西向座標 (Easting) 更重要")
    print("物理意義: 可能反映地形影響或颱風路徑")
else:
    print("分析結果: 南北向座標 (Northing) 更重要")
    print("物理意義: 可能反映颱風結構或緯度效應")

print("\n颱風 Fung-wong 特定考量:")
print("  - 颱風路徑: 主要影響東北部地區")
print("  - 地形效應: 中央山脈阻擋效應")

print("\n=== Phase 3: 視覺化測試 ===")

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

features = ['Easting (X)', 'Northing (Y)']
colors = ['#FF6B6B', '#4ECDC4'] if dominant_feature == 'easting' else ['#4ECDC4', '#FF6B6B']

bars = ax1.bar(features, importances, color=colors, alpha=0.8, edgecolor='black')
ax1.set_title('Random Forest 特徵重要性', fontsize=14, fontweight='bold')
ax1.set_ylabel('重要性', fontsize=12)
ax1.set_ylim(0, max(importances) * 1.2)

for bar, importance in zip(bars, importances):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
            f'{importance:.3f}\n({importance*100:.1f}%)',
            ha='center', va='bottom', fontweight='bold')

ax1.grid(True, alpha=0.3, axis='y')

explode = (0.1, 0) if dominant_feature == 'easting' else (0, 0.1)
pie_colors = ['#FF6B6B', '#4ECDC4'] if dominant_feature == 'easting' else ['#4ECDC4', '#FF6B6B']

wedges, texts, autotexts = ax2.pie(importances, labels=features, explode=explode,
                                   colors=pie_colors, autopct='%1.1f%%',
                                   shadow=True, startangle=90)
ax2.set_title('特徵重要性分佈', fontsize=14, fontweight='bold')

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(12)

plt.suptitle('颱風 Fung-wong 降雨預測 - Random Forest 特徵分析', 
            fontsize=16, fontweight='bold', y=1.05)
plt.tight_layout()
plt.savefig('test_cell5_feature_importance.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n=== Phase 4: 結論總結 ===")

print(f"主要發現:")
print(f"  1. {dominant_feature} 是更重要的預測特徵")
print(f"  2. 重要性比例: {max(importances):.3f} vs {min(importances):.3f}")
print(f"  3. 模型解釋性: Random Forest 提供了透明的特徵分析")

print(f"\n實際應用:")
print(f"  - 預測模型主要依據 {dominant_feature} 進行判斷")
print(f"  - 這為颱風降雨預測提供了物理可解釋性")
print(f"  - 有助於理解模型決策機制")

# Save test results
np.savez('test_cell5_results.npz', 
         importances=importances,
         features=features)

print("\n* Cell 5 Feature Importance test completed successfully!")
print("Ready to run in Jupyter Notebook.")

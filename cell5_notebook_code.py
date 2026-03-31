# Cell 5: ML Glass Box — Feature Importance (Slide 11)
# Captain's Question: "AI used what to predict floods — latitude or elevation?"

import matplotlib.pyplot as plt
import numpy as np

# Phase 1: 提取特徵重要性
print("=== Phase 1: 特徵重要性提取 ===")

try:
    # 確保 rf 模型存在
    if 'rf' not in locals():
        print("錯誤: 請先執行 Cell 4 訓練 Random Forest 模型")
    else:
        # 提取特徵重要性
        importances = rf.feature_importances_
        
        print("Feature Importance:")
        print(f"  Easting (X):  {importances[0]:.3f} ({importances[0]*100:.1f}%)")
        print(f"  Northing (Y): {importances[1]:.3f} ({importances[1]*100:.1f}%)")
        
        # 判斷主要特徵
        dominant_feature = 'easting' if importances[0] > importances[1] else 'northing'
        importance_diff = abs(importances[0] - importances[1])
        
        print(f"\n模型主要依賴: {dominant_feature}")
        print(f"重要性差異: {importance_diff:.3f}")
        
        # Phase 2: 物理意義解釋
        print("\n=== Phase 2: 物理意義解釋 ===")
        
        if importance_diff < 0.05:
            print("分析結果: 兩個維度重要性相當")
            print("物理意義: 颱風降雨在空間分佈相對均勻，無明顯方向性偏見")
        elif dominant_feature == 'easting':
            print("分析結果: 東西向座標 (Easting) 更重要")
            print("物理意義:")
            print("  - 可能反映地形影響: 中央山脈東西向降雨差異")
            print("  - 可能反映颱風路徑: 東西向移動造成的降雨分佈")
            print("  - 可能反映海陸分佈: 海洋與陸地的交互作用")
        else:
            print("分析結果: 南北向座標 (Northing) 更重要")
            print("物理意義:")
            print("  - 可能反映颱風結構: 颱風眼牆南北不對稱")
            print("  - 可能反映緯度效應: 不同緯度的溫度/濕度差異")
            print("  - 可能反映鋒面系統: 南北向氣團交匯帶來的降雨")
        
        # 颱風 Fung-wong 特定分析
        print("\n颱風 Fung-wong 特定考量:")
        print("  - 颱風路徑: 主要影響東北部地區")
        print("  - 地形效應: 中央山脈阻擋效應")
        print("  - 季節因素: 11月颱風的季節性特徵")
        
        # Phase 3: 視覺化呈現
        print("\n=== Phase 3: 視覺化分析 ===")
        
        # 建立特徵重要性圖表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左圖: 特徵重要性條形圖
        features = ['Easting (X)', 'Northing (Y)']
        colors = ['#FF6B6B', '#4ECDC4'] if dominant_feature == 'easting' else ['#4ECDC4', '#FF6B6B']
        
        bars = ax1.bar(features, importances, color=colors, alpha=0.8, edgecolor='black')
        ax1.set_title('Random Forest 特徵重要性', fontsize=14, fontweight='bold')
        ax1.set_ylabel('重要性', fontsize=12)
        ax1.set_ylim(0, max(importances) * 1.2)
        
        # 添加數值標籤
        for bar, importance in zip(bars, importances):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{importance:.3f}\n({importance*100:.1f}%)',
                    ha='center', va='bottom', fontweight='bold')
        
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 右圖: 特徵重要性餅圖
        explode = (0.1, 0) if dominant_feature == 'easting' else (0, 0.1)
        pie_colors = ['#FF6B6B', '#4ECDC4'] if dominant_feature == 'easting' else ['#4ECDC4', '#FF6B6B']
        
        wedges, texts, autotexts = ax2.pie(importances, labels=features, explode=explode,
                                           colors=pie_colors, autopct='%1.1f%%',
                                           shadow=True, startangle=90)
        ax2.set_title('特徵重要性分佈', fontsize=14, fontweight='bold')
        
        # 設定餅圖文字樣式
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)
        
        plt.suptitle('颱風 Fung-wong 降雨預測 - Random Forest 特徵分析', 
                    fontsize=16, fontweight='bold', y=1.05)
        plt.tight_layout()
        plt.show()
        
        # Phase 4: 結論總結
        print("\n=== Phase 4: 結論總結 ===")
        
        print(f"主要發現:")
        print(f"  1. {dominant_feature} 是更重要的預測特徵")
        print(f"  2. 重要性比例: {max(importances):.3f} vs {min(importances):.3f}")
        print(f"  3. 模型解釋性: Random Forest 提供了透明的特徵分析")
        
        print(f"\n實際應用:")
        print(f"  - 預測模型主要依據 {dominant_feature} 進行判斷")
        print(f"  - 這為颱風降雨預測提供了物理可解釋性")
        print(f"  - 有助於理解模型決策機制")
        
        # 保存結果
        try:
            np.savez('cell5_feature_importance.npz', 
                    importances=importances,
                    features=features)
            print("\n結果已保存至 cell5_feature_importance.npz")
        except Exception as e:
            print(f"保存結果時出錯: {e}")
        
        print("\n🔍 ML Glass Box 分析完成!")
        print("Random Forest 不再是黑盒子 - 我們看到了它的思考邏輯")

except Exception as e:
    print(f"執行錯誤: {e}")
    print("請確保已正確執行 Cell 4 並訓練了 Random Forest 模型")

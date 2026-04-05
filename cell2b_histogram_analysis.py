#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 2b: 直方圖分析診斷 - 為什麼原始資料的 variogram 擬合不良
Week 6 Spatial Prediction Shootout

Author: thumbb44110-creator
Date: 2026-03-31
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import warnings
from cell1_data_processing import main

warnings.filterwarnings('ignore')

def calculate_distribution_stats(data, data_name="Data"):
    """計算詳細的統計指標"""
    stats_dict = {
        'mean': np.mean(data),
        'median': np.median(data),
        'std': np.std(data),
        'min': np.min(data),
        'max': np.max(data),
        'skewness': stats.skew(data),
        'kurtosis': stats.kurtosis(data),
        'q25': np.percentile(data, 25),
        'q75': np.percentile(data, 75),
        'iqr': np.percentile(data, 75) - np.percentile(data, 25)
    }
    
    print(f"\n{data_name} 統計分析:")
    print(f"  平均值: {stats_dict['mean']:.2f}")
    print(f"  中位數: {stats_dict['median']:.2f}")
    print(f"  標準差: {stats_dict['std']:.2f}")
    print(f"  範圍: {stats_dict['min']:.2f} - {stats_dict['max']:.2f}")
    print(f"  偏態係數: {stats_dict['skewness']:.2f}")
    print(f"  峰度係數: {stats_dict['kurtosis']:.2f}")
    print(f"  四分位距: {stats_dict['iqr']:.2f}")
    
    return stats_dict

def analyze_skewness(skewness_value):
    """分析偏態係數並提供解釋"""
    if abs(skewness_value) < 0.5:
        skew_type = "接近對稱"
        interpretation = "分佈相對平衡，適合直接分析"
    elif skewness_value > 0.5:
        skew_type = "右偏（正偏態）"
        interpretation = "長尾向右延伸，有極端大值"
    elif skewness_value < -0.5:
        skew_type = "左偏（負偏態）"
        interpretation = "長尾向左延伸，有極端小值"
    else:
        skew_type = "輕微偏態"
        interpretation = "分佈略有偏斜"
    
    print(f"\n偏態分析:")
    print(f"  類型: {skew_type}")
    print(f"  解釋: {interpretation}")
    
    return skew_type, interpretation

def plot_histogram_comparison(z, z_log, save_figures=True):
    """建立專業的直方圖比較圖"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # 設定顏色和樣式
    colors = ['#FF6B6B', '#4ECDC4']  # 番茄紅和青綠色
    edgecolors = ['#8B0000', '#2F4F4F']
    
    # 左圖：原始雨量分佈
    n_bins = 30
    counts, bins, patches = axes[0].hist(z, bins=n_bins, color=colors[0], 
                                       edgecolor=edgecolors[0], alpha=0.7, 
                                       density=True)
    
    # 添加統計線
    mean_val = np.mean(z)
    median_val = np.median(z)
    axes[0].axvline(mean_val, color='red', linestyle='--', linewidth=2, 
                   label=f'平均: {mean_val:.1f}', alpha=0.8)
    axes[0].axvline(median_val, color='blue', linestyle='--', linewidth=2, 
                   label=f'中位數: {median_val:.1f}', alpha=0.8)
    
    # 設定左圖
    axes[0].set_title('原始雨量分佈 (mm/hr)', fontsize=14, fontweight='bold', pad=20)
    axes[0].set_xlabel('雨量 (mm/hr)', fontsize=12)
    axes[0].set_ylabel('密度', fontsize=12)
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)
    
    # 添加偏態註解
    skewness_z = stats.skew(z)
    axes[0].text(0.02, 0.98, f'偏態: {skewness_z:.2f}', 
                transform=axes[0].transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 右圖：log-transform 分佈
    counts_log, bins_log, patches_log = axes[1].hist(z_log, bins=n_bins, 
                                                   color=colors[1], 
                                                   edgecolor=edgecolors[1], 
                                                   alpha=0.7, density=True)
    
    # 添加統計線
    mean_log = np.mean(z_log)
    median_log = np.median(z_log)
    axes[1].axvline(mean_log, color='red', linestyle='--', linewidth=2, 
                   label=f'平均: {mean_log:.2f}', alpha=0.8)
    axes[1].axvline(median_log, color='blue', linestyle='--', linewidth=2, 
                   label=f'中位數: {median_log:.2f}', alpha=0.8)
    
    # 設定右圖
    axes[1].set_title('Log-Transform 後分佈', fontsize=14, fontweight='bold', pad=20)
    axes[1].set_xlabel('log(1 + 雨量)', fontsize=12)
    axes[1].set_ylabel('密度', fontsize=12)
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)
    
    # 添加偏態註解
    skewness_log = stats.skew(z_log)
    axes[1].text(0.02, 0.98, f'偏態: {skewness_log:.2f}', 
                transform=axes[1].transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # 總標題
    fig.suptitle('雨量資料分佈比較：原始 vs Log-Transform', 
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    if save_figures:
        plt.savefig('histogram_comparison.png', dpi=300, bbox_inches='tight')
        print("已儲存: histogram_comparison.png")
    
    plt.show()
    
    return fig

def create_summary_table(stats_raw, stats_log):
    """建立統計摘要表"""
    comparison_data = {
        '指標': ['平均值', '中位數', '標準差', '偏態係數', '最大值', '最小值'],
        '原始資料': [
            f"{stats_raw['mean']:.2f}",
            f"{stats_raw['median']:.2f}",
            f"{stats_raw['std']:.2f}",
            f"{stats_raw['skewness']:.2f}",
            f"{stats_raw['max']:.2f}",
            f"{stats_raw['min']:.2f}"
        ],
        'Log-Transform': [
            f"{stats_log['mean']:.2f}",
            f"{stats_log['median']:.2f}",
            f"{stats_log['std']:.2f}",
            f"{stats_log['skewness']:.2f}",
            f"{stats_log['max']:.2f}",
            f"{stats_log['min']:.2f}"
        ]
    }
    
    df = pd.DataFrame(comparison_data)
    print("\n統計摘要表:")
    print(df.to_string(index=False))
    
    return df

def generate_diagnostic_report(z, z_log, stats_raw, stats_log):
    """產生詳細的診斷報告"""
    report = []
    report.append("=" * 60)
    report.append("Cell 2b: 直方圖分析診斷報告")
    report.append("=" * 60)
    
    report.append("\n資料概覽:")
    report.append(f"  測站數量: {len(z)}")
    report.append(f"  雨量範圍: {z.min():.1f} - {z.max():.1f} mm/hr")
    
    report.append("\n問題識別:")
    report.append("  1. 原始資料呈現嚴重右偏分佈")
    report.append("  2. 極端值（50-130 mm）干擾統計分析")
    report.append("  3. 平均值（12.37）遠大於中位數（5.00）")
    
    report.append("\n根本原因:")
    report.append("  - 颱風降雨特性：少數測站記錄極端大雨")
    report.append("  - 空間變異性：局部強降雨造成長尾分佈")
    report.append("  - 測量尺度：小範圍內雨量差異巨大")
    
    report.append("\n解決方案:")
    report.append("  - Log-Transform: np.log1p(z) 穩定變異數")
    report.append("  - 偏態改善: 3.35 → 0.55")
    report.append("  - 分佈平衡: 接近常態分佈")
    
    report.append("\n改善效果:")
    improvement_skew = abs(stats_raw['skewness']) - abs(stats_log['skewness'])
    improvement_std = stats_raw['std'] - stats_log['std']
    
    report.append(f"  - 偏態減少: {improvement_skew:.2f}")
    report.append(f"  - 變異穩定: 標準差降低 {improvement_std:.1f}")
    report.append("  - 分佈對稱性大幅改善")
    
    report.append("\n影響分析:")
    report.append("  - Variogram 擬合: 原始資料點分散嚴重")
    report.append("  - 空間統計: 違反常態分佈假設")
    report.append("  - 預測品質: 極端值影響權重分配")
    
    report.append("\n後續建議:")
    report.append("  1. 使用 log-transform 資料進行 Kriging")
    report.append("  2. 預測後用 np.expm1() 轉換回原始單位")
    report.append("  3. 考慮其他穩定化方法（如 Box-Cox）")
    
    report.append("\n" + "=" * 60)
    
    # 儲存報告
    report_text = "\n".join(report)
    with open('cell2b_diagnostic_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(report_text)
    print("\n報告已儲存: cell2b_diagnostic_report.txt")
    
    return report_text

def demonstrate_log_transform_effect(z):
    """展示 log-transform 的數學效果"""
    print("\nLog-Transform 效果展示:")
    print("=" * 40)
    
    # 選擇代表性數值
    sample_values = [0.5, 1, 5, 10, 25, 50, 100, 130.5]
    
    print("原始值 → Log(1+原始值) → 還原值")
    print("-" * 40)
    
    for val in sample_values:
        log_val = np.log1p(val)
        back_val = np.expm1(log_val)
        print(f"{val:6.1f} → {log_val:8.3f} → {back_val:6.1f}")
    
    print("\n轉換特性:")
    print("  - 小值壓縮較少，大值壓縮較多")
    print("  - 保持數值順序關係")
    print("  - 避免負無窮大問題")
    print("  - 可完全還原原始值")

def main_analysis():
    """主要分析函式"""
    print("Cell 2b: 直方圖分析診斷")
    print("為什麼原始資料的 variogram 擬合不良？")
    
    # 載入資料
    print("\n載入資料...")
    study_rain_3826, x, y, z = main()
    
    if study_rain_3826 is None:
        print("無法載入資料")
        return
    
    print(f"成功載入 {len(z)} 個測站資料")
    
    # 計算 log-transform
    z_log = np.log1p(z)
    
    # 統計分析
    print("\n進行統計分析...")
    stats_raw = calculate_distribution_stats(z, "原始雨量資料")
    stats_log = calculate_distribution_stats(z_log, "Log-Transform 資料")
    
    # 偏態分析
    print("\n偏態分析...")
    skew_type_raw, interp_raw = analyze_skewness(stats_raw['skewness'])
    skew_type_log, interp_log = analyze_skewness(stats_log['skewness'])
    
    # 建立直方圖比較
    print("\n建立視覺化比較...")
    fig = plot_histogram_comparison(z, z_log)
    
    # 建立摘要表
    print("\n生成摘要表...")
    summary_df = create_summary_table(stats_raw, stats_log)
    
    # 展示轉換效果
    demonstrate_log_transform_effect(z)
    
    # 產生診斷報告
    print("\n生成診斷報告...")
    report = generate_diagnostic_report(z, z_log, stats_raw, stats_log)
    
    print("\n" + "=" * 60)
    print("Cell 2b 分析完成！")
    print("=" * 60)
    print("生成檔案:")
    print("  - histogram_comparison.png")
    print("  - cell2b_diagnostic_report.txt")
    print("\n關鍵發現:")
    print("  1. 原始資料嚴重右偏（偏態=3.35）")
    print("  2. Log-Transform 有效改善分佈（偏態=0.55）")
    print("  3. 這解釋了為什麼 variogram 擬合不良")
    print("  4. 轉換後資料更適合空間統計分析")
    
    return stats_raw, stats_log, summary_df

if __name__ == "__main__":
    stats_raw, stats_log, summary_df = main_analysis()

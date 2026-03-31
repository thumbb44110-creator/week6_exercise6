#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Week 6 Cell 2: Variogram Analysis & Kriging Basics
Spatial Prediction Shootout - Variogram Analysis Functions

Author: thumbb44110-creator
Date: 2026-03-31
"""

import numpy as np
import matplotlib.pyplot as plt
import warnings
from pykrige.ok import OrdinaryKriging

# 匯入 Cell 1 的結果
from cell1_data_processing import main
warnings.filterwarnings('ignore')

def calculate_sse(ok_model):
    """計算 variogram 擬合的平方誤差和"""
    try:
        # 計算經驗 variogram 與擬合模型的差異
        empirical = ok_model.semivariance
        # 在對應的 lag 距離上計算模型值
        lags = ok_model.lags
        model_values = ok_model.variogram_function(lags, *ok_model.variogram_model_parameters)
        
        # 計算 SSE
        sse = np.sum((empirical - model_values) ** 2)
        return sse
    except:
        return np.inf

def run_naive_kriging(x, y, z):
    """Cell 2a: 原始資料 Kriging（預期會失敗）"""
    print("=" * 60)
    print("Cell 2a: Variogram — First Attempt (Naive)")
    print("=" * 60)
    
    try:
        # 計算初始參數
        initial_sill = float(z.var())
        initial_range = 50000.0  # 50km
        initial_nugget = float(z.var() * 0.1)
        
        print(f"初始參數:")
        print(f"  Sill:   {initial_sill:.2f}")
        print(f"  Range:  {initial_range/1000:.1f} km")
        print(f"  Nugget: {initial_nugget:.2f}")
        print()
        
        # 建立 Kriging 模型
        OK_naive = OrdinaryKriging(x, y, z, variogram_model='spherical',
                                  verbose=False, enable_plotting=True, nlags=15,
                                  variogram_parameters={'sill': initial_sill,
                                                        'range': initial_range,
                                                        'nugget': initial_nugget})
        
        # 獲取擬合參數
        params = OK_naive.variogram_model_parameters
        print(f"擬合後參數:")
        print(f"  Sill:   {params[0]:.2f}")
        print(f"  Range:  {params[1]/1000:.1f} km")
        print(f"  Nugget: {params[2]:.2f}")
        
        # 計算 SSE
        sse = calculate_sse(OK_naive)
        print(f"  SSE:    {sse:.2f}")
        print()
        print("觀察 variogram 圖：點是否遵循曲線？")
        print("   預期：擬合不良，點分散嚴重")
        
        # 儲存圖片
        plt.savefig('variogram_naive.png', dpi=150, bbox_inches='tight')
        print("已儲存: variogram_naive.png")
        
        return OK_naive
        
    except Exception as e:
        print(f"Naive Kriging 失敗: {e}")
        return None

def analyze_histogram(z):
    """Cell 2b: 直方圖分析 - 理解失敗原因"""
    print("\n" + "=" * 60)
    print("Cell 2b: Why Did It Fail? — Look at the Histogram")
    print("=" * 60)
    
    # 建立比較圖
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 左圖：原始降雨值
    axes[0].hist(z, bins=30, color='tomato', edgecolor='black', alpha=0.7)
    axes[0].set_title('Raw Rainfall (mm/hr)', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Rainfall (mm/hr)')
    axes[0].set_ylabel('Station Count')
    axes[0].axvline(z.mean(), color='red', linestyle='--', alpha=0.8, label=f'Mean: {z.mean():.1f}')
    axes[0].axvline(np.median(z), color='blue', linestyle='--', alpha=0.8, label=f'Median: {np.median(z):.1f}')
    axes[0].legend()
    
    # 右圖：log(1+z) 轉換後
    z_log = np.log1p(z)
    axes[1].hist(z_log, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    axes[1].set_title('After log(1+z)', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('log(1 + Rainfall)')
    axes[1].set_ylabel('Station Count')
    axes[1].axvline(z_log.mean(), color='red', linestyle='--', alpha=0.8, label=f'Mean: {z_log.mean():.2f}')
    axes[1].axvline(np.median(z_log), color='blue', linestyle='--', alpha=0.8, label=f'Median: {np.median(z_log):.2f}')
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig('histogram_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # 統計分析
    print("統計分析:")
    print(f"原始資料:")
    print(f"  平均值: {z.mean():.2f} mm/hr")
    print(f"  中位數: {np.median(z):.2f} mm/hr")
    print(f"  標準差: {z.std():.2f} mm/hr")
    print(f"  最大值: {z.max():.2f} mm/hr")
    print(f"  偏態係數: {calculate_skewness(z):.2f}")
    print()
    print(f"Log-transform 後:")
    print(f"  平均值: {z_log.mean():.2f}")
    print(f"  中位數: {np.median(z_log):.2f}")
    print(f"  標準差: {z_log.std():.2f}")
    print(f"  偏態係數: {calculate_skewness(z_log):.2f}")
    print()
    
    print("觀察結果:")
    print("左圖：大部分測站 < 10 mm，但少數測站 50-130 mm（長尾右偏）")
    print("右圖：log-transform 後數值更平衡，分佈更接近常態")
    print("結論：極端值干擾 variogram，需要 log transform")
    
    # 儲存圖片
    print("已儲存: histogram_comparison.png")
    
    return z_log

def calculate_skewness(data):
    """計算偏態係數"""
    n = len(data)
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0
    return np.sum(((data - mean) / std) ** 3) / n

def run_log_kriging(x, y, z_log):
    """Cell 2c: Log-Transform Kriging（改善版本）"""
    print("\n" + "=" * 60)
    print("Cell 2c: Variogram — Second Attempt (with Log-Transform)")
    print("=" * 60)
    
    try:
        # 計算基於 log-transform 資料的初始參數
        initial_sill = float(z_log.var())
        initial_range = 50000.0  # 50km
        initial_nugget = float(z_log.var() * 0.1)
        
        print(f"基於 log-transform 的初始參數:")
        print(f"  Sill:   {initial_sill:.3f}")
        print(f"  Range:  {initial_range/1000:.1f} km")
        print(f"  Nugget: {initial_nugget:.3f}")
        print()
        
        # 建立 Kriging 模型
        OK = OrdinaryKriging(x, y, z_log, variogram_model='spherical',
                            verbose=False, enable_plotting=True, nlags=15,
                            variogram_parameters={'sill': initial_sill,
                                                  'range': initial_range,
                                                  'nugget': initial_nugget})
        
        # 獲取擬合參數
        params = OK.variogram_model_parameters
        print(f"擬合後參數:")
        print(f"  Sill:   {params[0]:.3f}")
        print(f"  Range:  {params[1]/1000:.1f} km")
        print(f"  Nugget: {params[2]:.3f}")
        
        # 計算 SSE
        sse = calculate_sse(OK)
        print(f"  SSE:    {sse:.3f}")
        print()
        print("與 Cell 2a 比較：點現在應該更好地遵循曲線")
        
        # 儲存圖片
        plt.savefig('variogram_improved.png', dpi=150, bbox_inches='tight')
        print("已儲存: variogram_improved.png")
        
        return OK
        
    except Exception as e:
        print(f"Log Kriging 失敗: {e}")
        return None

def compare_variogram_models(x, y, z_log):
    """Cell 2d: 模型與參數比較"""
    print("\n" + "=" * 60)
    print("Cell 2d: Which Variogram Fits Best? — Range & Model Comparison")
    print("=" * 60)
    
    # 測試範圍（公尺）
    ranges_m = [50000, 25000, 15000]  # 50km, 25km, 15km
    ranges_km = [50, 25, 15]
    
    # 模型比較結果
    results = []
    
    # Figure 1: Spherical model
    print("Figure 1: Spherical Model × 3 Ranges")
    fig1, axes1 = plt.subplots(1, 3, figsize=(18, 5))
    
    for i, (ax, r_m, r_km) in enumerate(zip(axes1, ranges_m, ranges_km)):
        try:
            # 建立模型
            ok_test = OrdinaryKriging(x, y, z_log, variogram_model='spherical',
                                     verbose=False, enable_plotting=False, nlags=15,
                                     variogram_parameters={'sill': float(z_log.var()),
                                                           'range': r_m,
                                                           'nugget': float(z_log.var() * 0.1)})
            
            # 繪製經驗 variogram
            ax.scatter(ok_test.lags/1000, ok_test.semivariance, c='red', s=30, alpha=0.7, label='Empirical')
            
            # 繪製擬合曲線
            lags_smooth = np.linspace(0, max(ok_test.lags), 100)
            model_curve = ok_test.variogram_function(lags_smooth, *ok_test.variogram_model_parameters)
            ax.plot(lags_smooth/1000, model_curve, 'k-', linewidth=2, label='Fitted')
            
            # 計算 SSE
            sse = calculate_sse(ok_test)
            
            # 設定圖表
            ax.set_title(f'Spherical - Range {r_km}km', fontsize=12, fontweight='bold')
            ax.set_xlabel('Distance (km)')
            ax.set_ylabel('Semivariance')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # 記錄結果
            results.append({
                'model': 'Spherical',
                'range_km': r_km,
                'sill': ok_test.variogram_model_parameters[0],
                'nugget': ok_test.variogram_model_parameters[2],
                'sse': sse
            })
            
            print(f"  Range {r_km}km: SSE = {sse:.3f}")
            
        except Exception as e:
            print(f"  Range {r_km}km: 失敗 - {e}")
    
    plt.tight_layout()
    plt.savefig('model_comparison_spherical.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("已儲存: model_comparison_spherical.png")
    
    # Figure 2: Exponential model
    print("\nFigure 2: Exponential Model × 3 Ranges")
    fig2, axes2 = plt.subplots(1, 3, figsize=(18, 5))
    
    # Add a new line here to set the title for Figure 2
    fig2.suptitle('Exponential Model Comparison', fontsize=16, fontweight='bold')
        try:
            # 建立模型
            ok_test = OrdinaryKriging(x, y, z_log, variogram_model='exponential',
                                     verbose=False, enable_plotting=False, nlags=15,
                                     variogram_parameters={'sill': float(z_log.var()),
                                                           'range': r_m,
                                                           'nugget': float(z_log.var() * 0.1)})
            
            # 繪製經驗 variogram
            ax.scatter(ok_test.lags/1000, ok_test.semivariance, c='red', s=30, alpha=0.7, label='Empirical')
            
            # 繪製擬合曲線
            lags_smooth = np.linspace(0, max(ok_test.lags), 100)
            model_curve = ok_test.variogram_function(lags_smooth, *ok_test.variogram_model_parameters)
            ax.plot(lags_smooth/1000, model_curve, 'k-', linewidth=2, label='Fitted')
            
            # 計算 SSE
            sse = calculate_sse(ok_test)
            
            # 設定圖表
            ax.set_title(f'Exponential - Range {r_km}km', fontsize=12, fontweight='bold')
            ax.set_xlabel('Distance (km)')
            ax.set_ylabel('Semivariance')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # 記錄結果
            results.append({
                'model': 'Exponential',
                'range_km': r_km,
                'sill': ok_test.variogram_model_parameters[0],
                'nugget': ok_test.variogram_model_parameters[2],
                'sse': sse
            })
            
            print(f"  Range {r_km}km: SSE = {sse:.3f}")
            
        except Exception as e:
            print(f"  Range {r_km}km: 失敗 - {e}")
    
    plt.tight_layout()
    plt.savefig('model_comparison_exponential.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("📁 已儲存: model_comparison_exponential.png")
    
    # 分析結果
    print_parameter_summary(results)
    
    return results

def print_parameter_summary(results):
    """印出參數比較摘要"""
    print("\n" + "=" * 60)
    print("參數比較摘要")
    print("=" * 60)
    
    # 轉換為 DataFrame 便於分析
    import pandas as pd
    df = pd.DataFrame(results)
    
    print("\n完整結果表:")
    print(df.to_string(index=False))
    
    # 找出最佳擬合
    best_result = df.loc[df['sse'].idxmin()]
    print(f"\n最佳擬合: {best_result['model']} - Range {best_result['range_km']}km")
    print(f"最低 SSE: {best_result['sse']:.3f}")
    
    # 模型內比較
    print("\n各模型內最佳 Range:")
    for model in ['Spherical', 'Exponential']:
        model_data = df[df['model'] == model]
        best_in_model = model_data.loc[model_data['sse'].idxmin()]
        print(f"  {model}: Range {best_in_model['range_km']}km (SSE = {best_in_model['sse']:.3f})")
    
    # 相同 Range 下模型比較
    print("\n相同 Range 下模型比較:")
    for range_km in [50, 25, 15]:
        range_data = df[df['range_km'] == range_km]
        if len(range_data) == 2:
            spherical_sse = range_data[range_data['model'] == 'Spherical']['sse'].iloc[0]
            exponential_sse = range_data[range_data['model'] == 'Exponential']['sse'].iloc[0]
            better_model = 'Spherical' if spherical_sse < exponential_sse else 'Exponential'
            print(f"  Range {range_km}km: {better_model} 更佳 (Spherical: {spherical_sse:.3f}, Exponential: {exponential_sse:.3f})")
    
    print("\n💡 分析問題:")
    print("1. Spherical 內哪個 Range 擬合最好？")
    print("2. Exponential 內哪個 Range 擬合最好？")
    print("3. 相同 Range 下，模型選擇重要嗎？")

def main_analysis():
    """主要分析函式"""
    print("Week 6 Cell 2: Variogram Analysis & Kriging Basics")
    print("=" * 60)
    
    # 載入資料
    print("載入 Cell 1 的處理結果...")
    study_rain_3826, x, y, z = main()
    
    if study_rain_3826 is None:
        print("無法載入資料，終止分析")
        return
    
    print(f"載入 {len(z)} 個有效測站")
    print(f"座標範圍: X({x.min():.0f}-{x.max():.0f}m), Y({y.min():.0f}-{y.max():.0f}m)")
    print(f"雨量範圍: {z.min():.1f}-{z.max():.1f} mm/hr")
    print()
    
    # 執行四個階段分析
    print("開始 Variogram 分析...")
    
    # Cell 2a: Naive Kriging
    OK_naive = run_naive_kriging(x, y, z)
    
    # Cell 2b: Histogram Analysis
    z_log = analyze_histogram(z)
    
    # Cell 2c: Log-Transform Kriging
    OK_improved = run_log_kriging(x, y, z_log)
    
    # Cell 2d: Model Comparison
    comparison_results = compare_variogram_models(x, y, z_log)
    
    print("\n" + "=" * 60)
    print("Cell 2 分析完成！")
    print("=" * 60)
    print("生成的檔案:")
    print("  - variogram_naive.png")
    print("  - histogram_comparison.png")
    print("  - variogram_improved.png")
    print("已儲存: model_comparison_spherical.png")
    plt.show()
    print("已儲存: model_comparison_spherical.png")
    print()
    print("關鍵發現:")
    print("  1. 原始資料因極端值導致 variogram 擬合不良")
    print("  2. Log-transform 顯著改善擬合品質")
    print("  3. 不同 Range 和模型會產生不同的擬合結果")
    print("  4. SSE 可作為擬合優度的量化指標")
    
    return OK_improved, comparison_results

if __name__ == "__main__":
    OK_final, results = main_analysis()

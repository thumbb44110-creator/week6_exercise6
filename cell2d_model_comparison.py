#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 2d: Variogram 模型與範圍比較分析
Week 6 Spatial Prediction Shootout

Author: thumbb44110-creator
Date: 2026-03-31
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import warnings
from pykrige.ok import OrdinaryKriging
from cell1_data_processing import main

warnings.filterwarnings('ignore')

def setup_comparison_parameters():
    """設定比較參數"""
    print("設定模型比較參數...")
    
    # 比較參數
    models = ['spherical', 'exponential']
    ranges_m = [50000, 25000, 15000]  # 50km, 25km, 15km
    ranges_km = [50, 25, 15]
    
    print(f"模型: {models}")
    print(f"範圍: {ranges_km} km")
    
    return {
        'models': models,
        'ranges_m': ranges_m,
        'ranges_km': ranges_km
    }

def calculate_sse(lags, semivariance, fitted_curve):
    """計算擬合誤差 (Sum of Squared Errors)"""
    # 確保擬合曲線與經驗點對應
    if len(fitted_curve) != len(lags):
        # 插值擬合曲線到經驗點位置
        from scipy.interpolate import interp1d
        if len(fitted_curve) > 1:
            # 假設 fitted_curve 對應到某個距離範圍
            curve_range = np.linspace(0, lags[-1], len(fitted_curve))
            interp_func = interp1d(curve_range, fitted_curve, kind='linear', 
                                  fill_value='extrapolate')
            fitted_at_lags = interp_func(lags)
        else:
            fitted_at_lags = np.full_like(lags, fitted_curve[0])
    else:
        fitted_at_lags = fitted_curve
    
    # 計算 SSE
    sse = np.sum((semivariance - fitted_at_lags) ** 2)
    
    return sse

def extract_empirical_variogram(ok_model):
    """提取經驗 variogram 資料"""
    try:
        # 獲取經驗 variogram 點
        lags = ok_model.lags
        semivariance = ok_model.semivariance
        
        # 過濾有效點
        valid_mask = ~np.isnan(lags) & ~np.isnan(semivariance) & (lags > 0)
        lags_clean = lags[valid_mask]
        semivariance_clean = semivariance[valid_mask]
        
        return lags_clean, semivariance_clean
        
    except Exception as e:
        print(f"提取經驗 variogram 失敗: {e}")
        return None, None

def create_fitted_curve(ok_model, max_distance):
    """建立擬合曲線"""
    try:
        # 生成密集距離點
        distances = np.linspace(0, max_distance, 100)
        
        # 使用模型參數計算擬合值
        params = ok_model.variogram_model_parameters
        model_type = ok_model.variogram_model
        
        if model_type == 'spherical':
            # Spherical 模型
            sill = params[0]
            range_param = params[1]
            nugget = params[2]
            
            fitted_values = np.zeros_like(distances)
            for i, d in enumerate(distances):
                if d == 0:
                    fitted_values[i] = nugget
                elif d < range_param:
                    fitted_values[i] = nugget + sill * (1.5 * (d / range_param) - 0.5 * (d / range_param) ** 3)
                else:
                    fitted_values[i] = nugget + sill
                    
        elif model_type == 'exponential':
            # Exponential 模型
            sill = params[0]
            range_param = params[1]
            nugget = params[2]
            
            fitted_values = nugget + sill * (1 - np.exp(-3 * distances / range_param))
            
        else:
            print(f"不支援的模型類型: {model_type}")
            return distances, np.zeros_like(distances)
        
        return distances, fitted_values
        
    except Exception as e:
        print(f"建立擬合曲線失敗: {e}")
        return np.linspace(0, max_distance, 100), np.zeros(100)

def run_single_model(x, y, z_log, model_type, range_m):
    """執行單一模型設定"""
    try:
        # 建立模型
        ok_model = OrdinaryKriging(x, y, z_log, 
                                  variogram_model=model_type,
                                  verbose=False, 
                                  enable_plotting=False, 
                                  nlags=15,
                                  variogram_parameters={
                                      'sill': float(z_log.var()),
                                      'range': range_m,
                                      'nugget': float(z_log.var() * 0.1)
                                  })
        
        # 獲取擬合參數
        params = ok_model.variogram_model_parameters
        
        # 提取經驗 variogram
        lags, semivariance = extract_empirical_variogram(ok_model)
        
        # 建立擬合曲線
        if lags is not None and len(lags) > 0:
            max_distance = np.max(lags) * 1.1
            curve_distances, fitted_curve = create_fitted_curve(ok_model, max_distance)
            
            # 計算 SSE
            sse = calculate_sse(lags, semivariance, fitted_curve)
        else:
            sse = np.inf
            lags = np.array([])
            semivariance = np.array([])
            curve_distances = np.array([])
            fitted_curve = np.array([])
        
        return {
            'model': ok_model,
            'params': params,
            'lags': lags,
            'semivariance': semivariance,
            'curve_distances': curve_distances,
            'fitted_curve': fitted_curve,
            'sse': sse,
            'success': True
        }
        
    except Exception as e:
        print(f"模型 {model_type} (範圍 {range_m/1000:.0f}km) 執行失敗: {e}")
        return {
            'model': None,
            'params': None,
            'lags': np.array([]),
            'semivariance': np.array([]),
            'curve_distances': np.array([]),
            'fitted_curve': np.array([]),
            'sse': np.inf,
            'success': False
        }

def run_model_comparison(x, y, z_log, comparison_params):
    """執行完整的模型比較"""
    print("\n執行模型比較...")
    
    results = {}
    
    for model_type in comparison_params['models']:
        print(f"\n測試 {model_type} 模型:")
        model_results = []
        
        for range_m, range_km in zip(comparison_params['ranges_m'], 
                                   comparison_params['ranges_km']):
            print(f"  範圍 {range_km}km...", end=" ")
            
            result = run_single_model(x, y, z_log, model_type, range_m)
            
            if result['success']:
                params = result['params']
                print(f"成功 (Sill={params[0]:.3f}, Nugget={params[2]:.3f}, SSE={result['sse']:.2f})")
            else:
                print("失敗")
            
            result['range_km'] = range_km
            result['range_m'] = range_m
            model_results.append(result)
        
        results[model_type] = model_results
    
    return results

def plot_comparison_figures(results, save_figures=True):
    """生成比較圖表"""
    print("\n生成比較圖表...")
    
    # 建立兩個圖表
    fig1, axes1 = plt.subplots(1, 3, figsize=(18, 5))
    fig2, axes2 = plt.subplots(1, 3, figsize=(18, 5))
    
    figures = {
        'spherical': {'fig': fig1, 'axes': axes1},
        'exponential': {'fig': fig2, 'axes': axes2}
    }
    
    for model_type, model_results in results.items():
        fig = figures[model_type]['fig']
        axes = figures[model_type]['axes']
        
        for i, result in enumerate(model_results):
            ax = axes[i]
            
            if result['success'] and len(result['lags']) > 0:
                # 繪製經驗 variogram 點
                ax.scatter(result['lags'], result['semivariance'], 
                          color='red', s=30, alpha=0.7, zorder=5, label='經驗點')
                
                # 繪製擬合曲線
                if len(result['fitted_curve']) > 0:
                    ax.plot(result['curve_distances'], result['fitted_curve'], 
                           'k-', linewidth=2, label='擬合曲線')
                
                # 設定圖表
                ax.set_title(f'{model_type.capitalize()} - 範圍 {result["range_km"]}km', 
                           fontsize=12, fontweight='bold')
                ax.set_xlabel('距離 (m)')
                ax.set_ylabel('半變異數')
                ax.grid(True, alpha=0.3)
                ax.legend(loc='lower right')
                
                # 添加 SSE 註解
                ax.text(0.02, 0.98, f'SSE: {result["sse"]:.2f}', 
                       transform=ax.transAxes, fontsize=10,
                       verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            else:
                ax.text(0.5, 0.5, '模型執行失敗', 
                       transform=ax.transAxes, fontsize=12,
                       horizontalalignment='center',
                       verticalalignment='center')
                ax.set_title(f'{model_type.capitalize()} - 範圍 {result["range_km"]}km')
        
        # 總標題
        fig.suptitle(f'{model_type.capitalize()} 模型範圍比較', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        if save_figures:
            filename = f'{model_type}_comparison.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"已儲存: {filename}")
        
        plt.show()
    
    return figures

def analyze_range_effect(results):
    """分析範圍效應"""
    print("\n分析範圍效應:")
    
    range_analysis = {}
    
    for model_type, model_results in results.items():
        print(f"\n{model_type.capitalize()} 模型:")
        
        sse_values = []
        range_values = []
        
        for result in model_results:
            if result['success']:
                sse_values.append(result['sse'])
                range_values.append(result['range_km'])
                
                print(f"  範圍 {result['range_km']}km: SSE = {result['sse']:.2f}")
        
        if len(sse_values) > 1:
            # 找到最佳範圍
            min_sse_idx = np.argmin(sse_values)
            best_range = range_values[min_sse_idx]
            best_sse = sse_values[min_sse_idx]
            
            print(f"  最佳範圍: {best_range}km (SSE = {best_sse:.2f})")
            
            # 分析趨勢
            if len(sse_values) == 3:
                if sse_values[0] < sse_values[1] < sse_values[2]:
                    trend = "SSE 隨範圍減小而增加"
                elif sse_values[0] > sse_values[1] > sse_values[2]:
                    trend = "SSE 隨範圍減小而減少"
                else:
                    trend = "SSE 與範圍呈非單調關係"
                
                print(f"  趨勢: {trend}")
            
            range_analysis[model_type] = {
                'best_range': best_range,
                'best_sse': best_sse,
                'all_sse': sse_values,
                'all_ranges': range_values
            }
    
    return range_analysis

def analyze_model_effect(results):
    """分析模型效應"""
    print("\n分析模型效應:")
    
    # 比較相同範圍下不同模型的 SSE
    ranges_to_compare = [50, 25, 15]  # km
    
    for range_km in ranges_to_compare:
        print(f"\n範圍 {range_km}km 比較:")
        
        sse_by_model = {}
        
        for model_type, model_results in results.items():
            for result in model_results:
                if result['success'] and result['range_km'] == range_km:
                    sse_by_model[model_type] = result['sse']
                    print(f"  {model_type.capitalize()}: SSE = {result['sse']:.2f}")
                    break
        
        if len(sse_by_model) == 2:
            # 比較模型差異
            spherical_sse = sse_by_model.get('spherical', np.inf)
            exponential_sse = sse_by_model.get('exponential', np.inf)
            
            if spherical_sse < exponential_sse:
                better_model = 'Spherical'
                improvement = (exponential_sse - spherical_sse) / exponential_sse * 100
            else:
                better_model = 'Exponential'
                improvement = (spherical_sse - exponential_sse) / spherical_sse * 100
            
            print(f"  最佳模型: {better_model} (改善 {improvement:.1f}%)")
    
    return sse_by_model

def create_comparison_table(results):
    """建立比較表格"""
    print("\n建立比較表格:")
    
    table_data = []
    
    for model_type, model_results in results.items():
        for result in model_results:
            if result['success']:
                params = result['params']
                table_data.append({
                    '模型': model_type.capitalize(),
                    '範圍 (km)': result['range_km'],
                    'Sill': f"{params[0]:.3f}",
                    'Range (m)': f"{params[1]:.0f}",
                    'Nugget': f"{params[2]:.3f}",
                    'SSE': f"{result['sse']:.2f}",
                    'Nugget/Sill': f"{params[2]/params[0]:.3f}"
                })
    
    df = pd.DataFrame(table_data)
    print(df.to_string(index=False))
    
    # 儲存為 CSV
    df.to_csv('sse_comparison_table.csv', index=False, encoding='utf-8')
    print("\n已儲存: sse_comparison_table.csv")
    
    return df

def generate_comparison_report(results, range_analysis, model_effect, comparison_df):
    """產生比較報告"""
    print("\n生成比較報告...")
    
    report = []
    report.append("=" * 60)
    report.append("Cell 2d: Variogram 模型與範圍比較報告")
    report.append("=" * 60)
    
    report.append("\n執行摘要:")
    report.append("  - 比較模型: Spherical vs Exponential")
    report.append("  - 測試範圍: 50km, 25km, 15km")
    report.append("  - 評估指標: SSE (Sum of Squared Errors)")
    
    report.append("\n關鍵發現:")
    
    # 範圍效應總結
    for model_type, analysis in range_analysis.items():
        report.append(f"  {model_type.capitalize()} 最佳範圍: {analysis['best_range']}km")
    
    # 模型效應總結
    if len(model_effect) > 0:
        best_overall = min(model_effect.items(), key=lambda x: x[1])
        report.append(f"  整體最佳模型: {best_overall[0].capitalize()}")
    
    report.append("\n詳細分析:")
    
    # 每個模型的詳細分析
    for model_type, model_results in results.items():
        report.append(f"\n{model_type.capitalize()} 模型:")
        
        successful_results = [r for r in model_results if r['success']]
        if len(successful_results) > 0:
            best_result = min(successful_results, key=lambda x: x['sse'])
            report.append(f"  - 最佳設定: 範圍 {best_result['range_km']}km")
            report.append(f"  - 最佳 SSE: {best_result['sse']:.2f}")
            report.append(f"  - 參數: Sill={best_result['params'][0]:.3f}, Nugget={best_result['params'][2]:.3f}")
    
    report.append("\n實務建議:")
    report.append("  1. 選擇 SSE 最小的模型和範圍組合")
    report.append("  2. 考慮擬合穩定性和參數合理性")
    report.append("  3. 結合資料特性和解釋性需求")
    report.append("  4. 驗證結果在預測階段的表現")
    
    report.append("\n科學價值:")
    report.append("  - 展示系統性模型比較方法")
    report.append("  - 量化範圍和模型的影響")
    report.append("  - 提供客觀的模型選擇依據")
    report.append("  - 建立最佳實踐參考")
    
    report.append("\n" + "=" * 60)
    
    # 儲存報告
    report_text = "\n".join(report)
    with open('model_comparison_summary.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(report_text)
    print("\n報告已儲存: model_comparison_summary.txt")
    
    return report_text

def main_model_comparison():
    """主要比較分析函式"""
    print("Cell 2d: Variogram 模型與範圍比較分析")
    print("系統性比較不同模型和範圍的影響")
    
    # 載入資料
    print("\n載入資料...")
    study_rain_3826, x, y, z = main()
    
    if study_rain_3826 is None:
        print("無法載入資料")
        return
    
    print(f"成功載入 {len(z)} 個測站資料")
    
    # 計算 log-transform
    z_log = np.log1p(z)
    
    # Phase 1: 設定參數
    comparison_params = setup_comparison_parameters()
    
    # Phase 2: 執行比較
    results = run_model_comparison(x, y, z_log, comparison_params)
    
    # Phase 3: 生成圖表
    figures = plot_comparison_figures(results)
    
    # Phase 4: 分析效應
    range_analysis = analyze_range_effect(results)
    model_effect = analyze_model_effect(results)
    
    # Phase 5: 建立表格
    comparison_df = create_comparison_table(results)
    
    # Phase 6: 生成報告
    report = generate_comparison_report(results, range_analysis, model_effect, comparison_df)
    
    print("\n" + "=" * 60)
    print("Cell 2d 分析完成！")
    print("=" * 60)
    print("生成檔案:")
    print("  - spherical_comparison.png")
    print("  - exponential_comparison.png")
    print("  - sse_comparison_table.csv")
    print("  - model_comparison_summary.txt")
    print("\n關鍵成果:")
    print("  1. 系統性比較了 2 種模型 × 3 種範圍")
    print("  2. 量化了範圍和模型的影響")
    print("  3. 識別了最佳模型組合")
    print("  4. 提供了科學的選擇依據")
    
    return {
        'results': results,
        'range_analysis': range_analysis,
        'model_effect': model_effect,
        'comparison_df': comparison_df
    }

if __name__ == "__main__":
    comparison_results = main_model_comparison()

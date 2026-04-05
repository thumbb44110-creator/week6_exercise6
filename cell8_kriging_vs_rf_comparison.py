#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 8: Kriging vs RF — Direct Comparison
Lab 1: The Four-Way Interpolation Shootout

Create a 3-panel comparison: Kriging | Random Forest | Difference Map
The difference map reveals where the two methods disagree.

Author: thumbb44110-creator
Date: 2026-04-03
"""

import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def check_prerequisites():
    """檢查必要的前置變數"""
    print("Phase 1: 前置變數檢查")
    print("=" * 50)
    
    required_vars = {
        '插值結果': ['z_kriging', 'z_rf'],
        '網格座標': ['grid_x', 'grid_y'],
        '測站資料': ['x', 'y', 'z']
    }
    
    missing_vars = []
    
    for category, vars_list in required_vars.items():
        print(f"\n{category}:")
        for var in vars_list:
            if var in globals() or var in locals():
                # 獲取變數值進行檢查
                var_value = globals().get(var, locals().get(var))
                if var_value is not None:
                    if hasattr(var_value, 'shape'):
                        print(f"  ✅ {var}: {var_value.shape}")
                    else:
                        print(f"  ✅ {var}: {type(var_value).__name__}")
                else:
                    print(f"  ⚠️ {var}: 存在但為 None")
                    missing_vars.append(var)
            else:
                print(f"  ❌ {var}: 未定義")
                missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ 缺少必要變數: {missing_vars}")
        print("請確保已執行 Cell 1-7")
        return False
    
    # 檢查陣列形狀一致性
    print(f"\n陣列形狀檢查:")
    interpolation_vars = ['z_kriging', 'z_rf']
    shapes = []
    
    for var in interpolation_vars:
        var_value = globals().get(var, locals().get(var))
        if var_value is not None:
            shape = var_value.shape
            shapes.append(shape)
            print(f"  {var}: {shape}")
    
    # 檢查形狀是否一致
    if len(set(shapes)) <= 1:  # 所有形狀相同或只有一個形狀
        print(f"  ✅ 陣列形狀一致")
        return True
    else:
        print(f"  ❌ 陣列形狀不一致: {set(shapes)}")
        return False

def calculate_difference_analysis():
    """計算差異分析和統計指標"""
    print("\nPhase 2: 差異計算與分析")
    print("=" * 50)
    
    # 獲取插值結果
    z_kriging = globals().get('z_kriging', locals().get('z_kriging'))
    z_rf = globals().get('z_rf', locals().get('z_rf'))
    
    if z_kriging is None or z_rf is None:
        print("❌ 插值結果未找到")
        return None
    
    # 計算差異地圖
    diff = z_kriging - z_rf
    
    # 基本統計
    diff_stats = {
        'min': np.nanmin(diff),
        'max': np.nanmax(diff),
        'mean': np.nanmean(diff),
        'std': np.nanstd(diff),
        'range': np.nanmax(diff) - np.nanmin(diff)
    }
    
    # 相關性分析
    try:
        correlation = np.corrcoef(z_kriging.flatten(), z_rf.flatten())[0, 1]
        if np.isnan(correlation):
            correlation = 0.0
    except:
        correlation = 0.0
    
    # 一致性分析
    thresholds = [1.0, 2.5, 5.0, 10.0]  # mm/hr
    consistency = {}
    
    for threshold in thresholds:
        consistent_ratio = np.mean(np.abs(diff) < threshold)
        consistency[f'threshold_{threshold}'] = consistent_ratio
    
    # 高雨量區域差異分析
    z_original = globals().get('z', locals().get('z'))
    if z_original is not None:
        high_rain_threshold = np.percentile(z_original, 75)  # 75th percentile
        high_rain_mask = (z_kriging > high_rain_threshold) | (z_rf > high_rain_threshold)
        
        if np.any(high_rain_mask):
            high_rain_diff = diff[high_rain_mask]
            high_rain_stats = {
                'mean_diff': np.nanmean(high_rain_diff),
                'std_diff': np.nanstd(high_rain_diff),
                'max_diff': np.nanmax(np.abs(high_rain_diff))
            }
        else:
            high_rain_stats = {'mean_diff': 0, 'std_diff': 0, 'max_diff': 0}
    else:
        high_rain_stats = {'mean_diff': 0, 'std_diff': 0, 'max_diff': 0}
    
    # 顯示統計結果
    print(f"差異統計:")
    print(f"  範圍: {diff_stats['min']:.2f} - {diff_stats['max']:.2f} mm/hr")
    print(f"  平均: {diff_stats['mean']:.2f} mm/hr")
    print(f"  標準差: {diff_stats['std']:.2f} mm/hr")
    print(f"  相關係數: {correlation:.3f}")
    
    print(f"\n一致性分析 (|diff| < threshold):")
    for threshold, ratio in consistency.items():
        thresh_val = threshold.split('_')[1]
        print(f"  {thresh_val} mm/hr: {ratio*100:.1f}% 一致")
    
    print(f"\n高雨量區域差異 (>{high_rain_threshold:.1f} mm/hr):")
    print(f"  平均差異: {high_rain_stats['mean_diff']:.2f} mm/hr")
    print(f"  最大差異: {high_rain_stats['max_diff']:.2f} mm/hr")
    
    return {
        'diff': diff,
        'diff_stats': diff_stats,
        'correlation': correlation,
        'consistency': consistency,
        'high_rain_stats': high_rain_stats,
        'high_rain_threshold': high_rain_threshold
    }

def create_comparison_panel(analysis_results):
    """建立 3-panel 比較圖表"""
    print("\nPhase 3: 建立 3-Panel 比較圖表")
    print("=" * 50)
    
    # 獲取資料
    z_kriging = globals().get('z_kriging', locals().get('z_kriging'))
    z_rf = globals().get('z_rf', locals().get('z_rf'))
    diff = analysis_results['diff']
    
    # 獲取網格範圍
    grid_x = globals().get('grid_x', locals().get('grid_x'))
    grid_y = globals().get('grid_y', locals().get('grid_y'))
    x_min, x_max = grid_x.min(), grid_x.max()
    y_min, y_max = grid_y.min(), grid_y.max()
    
    # 獲取測站座標
    x_stations = globals().get('x', locals().get('x'))
    y_stations = globals().get('y', locals().get('y'))
    
    print(f"網格範圍: {x_min:.0f} - {x_max:.0f} m (Easting)")
    print(f"網格範圍: {y_min:.0f} - {y_max:.0f} m (Northing)")
    print(f"測站數量: {len(x_stations)}")
    
    # 建立 1×3 圖表
    fig, axes = plt.subplots(1, 3, figsize=(22, 7))
    fig.suptitle('Kriging vs Random Forest — Direct Comparison', 
                fontsize=18, fontweight='bold', y=0.95)
    
    # 統一色彩範圍 (Kriging & RF)
    vmax = max(np.nanmax(z_kriging), np.nanmax(z_rf))
    vmin = 0  # 雨量不能為負
    
    # 對稱差異範圍
    vmax_diff = max(abs(np.nanmin(diff)), abs(np.nanmax(diff)))
    
    # 面板 1: Kriging
    ax1 = axes[0]
    im1 = ax1.imshow(z_kriging, 
                    extent=[x_min, x_max, y_min, y_max],
                    origin='lower', 
                    cmap='YlOrRd', 
                    vmin=vmin, 
                    vmax=vmax,
                    aspect='auto')
    
    # 疊加測站點
    ax1.scatter(x_stations, y_stations, c='black', s=10, alpha=0.7, zorder=5)
    
    # 設定標題和標籤
    ax1.set_title('Ordinary Kriging', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Easting (m)', fontsize=12)
    ax1.set_ylabel('Northing (m)', fontsize=12)
    
    # 添加統計資訊
    kriging_stats = f"Range: {np.nanmin(z_kriging):.1f}-{np.nanmax(z_kriging):.1f}\nMean: {np.nanmean(z_kriging):.1f}"
    ax1.text(0.02, 0.98, kriging_stats, 
            transform=ax1.transAxes, fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 添加色彩條
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Rainfall (mm/hr)', fontsize=10)
    
    print("  ✅ Kriging 面板: 繪製完成")
    
    # 面板 2: Random Forest
    ax2 = axes[1]
    im2 = ax2.imshow(z_rf, 
                    extent=[x_min, x_max, y_min, y_max],
                    origin='lower', 
                    cmap='YlOrRd', 
                    vmin=vmin, 
                    vmax=vmax,
                    aspect='auto')
    
    # 疊加測站點
    ax2.scatter(x_stations, y_stations, c='black', s=10, alpha=0.7, zorder=5)
    
    # 設定標題和標籤
    ax2.set_title('Random Forest', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Easting (m)', fontsize=12)
    ax2.set_ylabel('Northing (m)', fontsize=12)
    
    # 添加統計資訊
    rf_stats = f"Range: {np.nanmin(z_rf):.1f}-{np.nanmax(z_rf):.1f}\nMean: {np.nanmean(z_rf):.1f}"
    ax2.text(0.02, 0.98, rf_stats, 
            transform=ax2.transAxes, fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 添加色彩條
    cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.8)
    cbar2.set_label('Rainfall (mm/hr)', fontsize=10)
    
    print("  ✅ Random Forest 面板: 繪製完成")
    
    # 面板 3: Difference Map
    ax3 = axes[2]
    im3 = ax3.imshow(diff, 
                    extent=[x_min, x_max, y_min, y_max],
                    origin='lower', 
                    cmap='RdBu_r',  # 紅-藍反轉
                    vmin=-vmax_diff, 
                    vmax=vmax_diff,
                    aspect='auto')
    
    # 疊加測站點
    ax3.scatter(x_stations, y_stations, c='black', s=10, alpha=0.7, zorder=5)
    
    # 設定標題和標籤
    ax3.set_title('Difference Map\n(Kriging - Random Forest)', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Easting (m)', fontsize=12)
    ax3.set_ylabel('Northing (m)', fontsize=12)
    
    # 添加統計資訊
    diff_stats_display = f"Range: {np.nanmin(diff):.1f} to {np.nanmax(diff):.1f}\nMean: {np.nanmean(diff):.1f}\nCorr: {analysis_results['correlation']:.3f}"
    ax3.text(0.02, 0.98, diff_stats_display, 
            transform=ax3.transAxes, fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 添加色彩條
    cbar3 = plt.colorbar(im3, ax=ax3, shrink=0.8)
    cbar3.set_label('Difference (mm/hr)', fontsize=10)
    
    print("  ✅ Difference Map 面板: 繪製完成")
    
    # 調整版面
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    return fig

def generate_decision_analysis(analysis_results):
    """生成決策分析報告"""
    print("\nPhase 4: 決策分析")
    print("=" * 50)
    
    diff_stats = analysis_results['diff_stats']
    correlation = analysis_results['correlation']
    consistency = analysis_results['consistency']
    high_rain_stats = analysis_results['high_rain_stats']
    high_rain_threshold = analysis_results['high_rain_threshold']
    
    print("📊 方法比較分析:")
    print(f"  相關係數: {correlation:.3f}", end="")
    if correlation > 0.8:
        print(" (高度相關)")
    elif correlation > 0.6:
        print(" (中度相關)")
    else:
        print(" (低度相關)")
    
    print(f"\n📈 差異程度:")
    abs_mean_diff = abs(diff_stats['mean'])
    if abs_mean_diff < 1:
        print(f"  平均差異: {abs_mean_diff:.2f} mm/hr (極小)")
    elif abs_mean_diff < 2.5:
        print(f"  平均差異: {abs_mean_diff:.2f} mm/hr (小)")
    elif abs_mean_diff < 5:
        print(f"  平均差異: {abs_mean_diff:.2f} mm/hr (中等)")
    else:
        print(f"  平均差異: {abs_mean_diff:.2f} mm/hr (顯著)")
    
    print(f"\n🎯 一致性評估:")
    for threshold, ratio in consistency.items():
        thresh_val = threshold.split('_')[1]
        if ratio > 0.9:
            level = "極高"
        elif ratio > 0.8:
            level = "高"
        elif ratio > 0.7:
            level = "中等"
        else:
            level = "低"
        print(f"  {thresh_val} mm/hr 內: {ratio*100:.1f}% ({level})")
    
    print(f"\n⚠️ 高雨量區域 (>{high_rain_threshold:.1f} mm/hr):")
    if high_rain_stats['max_diff'] > 5:
        print(f"  最大差異: {high_rain_stats['max_diff']:.1f} mm/hr (需要關注)")
    elif high_rain_stats['max_diff'] > 2.5:
        print(f"  最大差異: {high_rain_stats['max_diff']:.1f} mm/hr (注意)")
    else:
        print(f"  最大差異: {high_rain_stats['max_diff']:.1f} mm/hr (可接受)")
    
    # 決策建議
    print(f"\n💡 決策建議:")
    
    if correlation > 0.8 and consistency['threshold_2.5'] > 0.8:
        print("  ✅ 兩種方法高度一致，可任選一種使用")
        print("  📊 建議：Kriging (提供不確定性估計)")
    elif correlation > 0.6 and consistency['threshold_5.0'] > 0.7:
        print("  ⚖️ 兩種方法中度一致，建議交叉驗證")
        print("  📊 建議：差異較大區域使用兩種方法平均")
    else:
        print("  ❌ 兩種方法差異較大，需要額外分析")
        print("  📊 建議：檢查差異地圖，選擇適合區域的方法")
    
    if high_rain_stats['max_diff'] > 5:
        print("  🚨 高雨量區域差異顯著，指揮官需要額外注意")
    
    return True

def save_and_validate_figure(fig):
    """儲存並驗證圖表"""
    print("\nPhase 5: 儲存與驗證")
    print("=" * 50)
    
    # 儲存圖表
    filename = 'kriging_vs_rf.png'
    
    try:
        fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ 圖表已儲存: {filename}")
        
        # 檢查檔案大小
        import os
        file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
        print(f"  檔案大小: {file_size:.2f} MB")
        
        return True, filename
        
    except Exception as e:
        print(f"❌ 圖表儲存失敗: {e}")
        return False, None

def generate_summary_report(analysis_results, filename):
    """生成執行摘要報告"""
    print("\nPhase 6: 生成摘要報告")
    print("=" * 50)
    
    report_lines = [
        "Cell 8: Kriging vs RF — Direct Comparison - 執行報告",
        "=" * 60,
        f"執行時間: 2026-04-03",
        f"輸出檔案: {filename}",
        "",
        "比較方法:",
        "  1. Ordinary Kriging: 統計最佳插值方法",
        "  2. Random Forest: 機器學習預測方法",
        "  3. Difference Map: 揭示方法不一致區域",
        "",
        "關鍵發現:",
        f"  - 相關係數: {analysis_results['correlation']:.3f}",
        f"  - 平均差異: {analysis_results['diff_stats']['mean']:.2f} mm/hr",
        f"  - 差異範圍: {analysis_results['diff_stats']['min']:.2f} - {analysis_results['diff_stats']['max']:.2f} mm/hr",
        "",
        "決策支援:",
        "  - 紅色區域: Kriging 預測較高",
        "  - 藍色區域: Random Forest 預測較高",
        "  - 白色區域: 兩種方法一致",
        "  - 高差異區域: 需要指揮官額外注意",
        "",
        "應用價值:",
        "  - 識別插值不確定性高的區域",
        "  - 支援方法選擇決策",
        "  - 提供風險評估依據",
        "  - 增強決策信心"
    ]
    
    report_text = "\n".join(report_lines)
    
    # 儲存報告
    try:
        with open('cell8_execution_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        print("✅ 報告已儲存: cell8_execution_report.txt")
    except Exception as e:
        print(f"⚠️ 報告儲存失敗: {e}")
    
    return report_text

def main_cell8():
    """Cell 8 主要執行函數"""
    print("Lab 1 Cell 8: Kriging vs RF — Direct Comparison")
    print("三種面板比較：Kriging | Random Forest | Difference Map")
    print("=" * 60)
    
    try:
        # Phase 1: 前置檢查
        if not check_prerequisites():
            print("❌ 前置檢查失敗，終止執行")
            return False
        
        # Phase 2: 差異計算與分析
        analysis_results = calculate_difference_analysis()
        if analysis_results is None:
            print("❌ 差異分析失敗")
            return False
        
        # Phase 3: 建立比較圖表
        fig = create_comparison_panel(analysis_results)
        
        # Phase 4: 決策分析
        generate_decision_analysis(analysis_results)
        
        # Phase 5: 儲存與驗證
        success, filename = save_and_validate_figure(fig)
        
        if success:
            # Phase 6: 生成摘要報告
            report = generate_summary_report(analysis_results, filename)
            
            # 顯示圖表
            plt.show()
            
            print("\n" + "=" * 60)
            print("🎉 Cell 8 實作完成！")
            print("=" * 60)
            print("輸出成果:")
            print(f"  - 圖表檔案: {filename}")
            print("  - 執行報告: cell8_execution_report.txt")
            print("\nKriging vs Random Forest 比較完成")
            print("差異地圖揭示了需要額外注意的區域")
            
            return True
        else:
            print("❌ 圖表儲存失敗")
            return False
            
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

# Jupyter Notebook 執行版本
jupyter_code = '''
# Lab 1 Cell 8: Kriging vs RF — Direct Comparison
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 檢查必要變數
required_vars = ['z_kriging', 'z_rf', 'grid_x', 'grid_y', 'x', 'y']
missing_vars = [var for var in required_vars if var not in locals() and var not in globals()]

if missing_vars:
    raise NameError(f"缺少必要變數: {missing_vars}. 請先執行 Cell 1-7")

print(f"✅ 前置檢查通過: 所有必要變數可用")

# 計算差異地圖
diff = z_kriging - z_rf

# 統計分析
correlation = np.corrcoef(z_kriging.flatten(), z_rf.flatten())[0, 1]
diff_mean = np.mean(diff)
diff_std = np.std(diff)

print(f"差異統計:")
print(f"  範圍: {diff.min():.2f} - {diff.max():.2f} mm/hr")
print(f"  平均: {diff_mean:.2f} mm/hr")
print(f"  相關係數: {correlation:.3f}")

# 建立 1×3 比較圖表
fig, axes = plt.subplots(1, 3, figsize=(22, 7))
fig.suptitle('Kriging vs Random Forest — Direct Comparison', 
            fontsize=18, fontweight='bold', y=0.95)

# 網格範圍
x_min, x_max = grid_x.min(), grid_x.max()
y_min, y_max = grid_y.min(), grid_y.max()

# 統一色彩範圍
vmax = max(np.nanmax(z_kriging), np.nanmax(z_rf))
vmin = 0

# 對稱差異範圍
vmax_diff = max(abs(diff.min()), abs(diff.max()))

# 面板 1: Kriging
im1 = axes[0].imshow(z_kriging, 
                    extent=[x_min, x_max, y_min, y_max],
                    origin='lower', 
                    cmap='YlOrRd', 
                    vmin=vmin, 
                    vmax=vmax,
                    aspect='auto')
axes[0].scatter(x, y, c='black', s=10, alpha=0.7, zorder=5)
axes[0].set_title('Ordinary Kriging', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Easting (m)', fontsize=12)
axes[0].set_ylabel('Northing (m)', fontsize=12)
cbar1 = plt.colorbar(im1, ax=axes[0], shrink=0.8)
cbar1.set_label('Rainfall (mm/hr)', fontsize=10)

# 面板 2: Random Forest
im2 = axes[1].imshow(z_rf, 
                    extent=[x_min, x_max, y_min, y_max],
                    origin='lower', 
                    cmap='YlOrRd', 
                    vmin=vmin, 
                    vmax=vmax,
                    aspect='auto')
axes[1].scatter(x, y, c='black', s=10, alpha=0.7, zorder=5)
axes[1].set_title('Random Forest', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Easting (m)', fontsize=12)
axes[1].set_ylabel('Northing (m)', fontsize=12)
cbar2 = plt.colorbar(im2, ax=axes[1], shrink=0.8)
cbar2.set_label('Rainfall (mm/hr)', fontsize=10)

# 面板 3: Difference Map
im3 = axes[2].imshow(diff, 
                    extent=[x_min, x_max, y_min, y_max],
                    origin='lower', 
                    cmap='RdBu_r',  # 紅-藍反轉
                    vmin=-vmax_diff, 
                    vmax=vmax_diff,
                    aspect='auto')
axes[2].scatter(x, y, c='black', s=10, alpha=0.7, zorder=5)
axes[2].set_title('Difference Map\\n(Kriging - Random Forest)', fontsize=14, fontweight='bold')
axes[2].set_xlabel('Easting (m)', fontsize=12)
axes[2].set_ylabel('Northing (m)', fontsize=12)
cbar3 = plt.colorbar(im3, ax=axes[2], shrink=0.8)
cbar3.set_label('Difference (mm/hr)', fontsize=10)

# 調整版面
plt.tight_layout()
plt.subplots_adjust(top=0.92)

# 儲存圖表
plt.savefig('kriging_vs_rf.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✅ 圖表已儲存: kriging_vs_rf.png")

# 顯示圖表
plt.show()

print("\\n✅ Kriging vs Random Forest 直接比較完成!")
print("差異地圖揭示了需要額外注意的區域")
'''

if __name__ == "__main__":
    # 獨立執行模式（用於測試）
    print("Cell 8 獨立執行模式")
    print("注意：需要先載入所有必要變數")
    success = main_cell8()
else:
    print("Cell 8 模組已載入")
    print("使用 main_cell8() 函數執行完整比較流程")

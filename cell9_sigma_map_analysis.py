#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 9: The Sigma Map — Kriging's Unique Weapon
Lab 2: Confidence & Uncertainty Diagnosis

This is what makes Kriging special. No other method natively provides a confidence map.

Author: thumbb44110-creator
Date: 2026-04-04
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
        'Kriging 結果': ['z_kriging', 'ss_kriging'],
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
        print("請確保已執行 Cell 1-3 (Kriging 實作)")
        return False
    
    # 檢查陣列形狀一致性
    print(f"\n陣列形狀檢查:")
    kriging_vars = ['z_kriging', 'ss_kriging']
    shapes = []
    
    for var in kriging_vars:
        var_value = globals().get(var, locals().get(var))
        if var_value is not None:
            shape = var_value.shape
            shapes.append(shape)
            print(f"  {var}: {shape}")
    
    # 檢查形狀是否一致
    if len(set(shapes)) <= 1:
        print(f"  ✅ 陣列形狀一致")
        return True
    else:
        print(f"  ❌ 陣列形狀不一致: {set(shapes)}")
        return False

def analyze_sigma_map():
    """分析 Sigma Map (Kriging 不確定性)"""
    print("\nPhase 2: Sigma Map 分析")
    print("=" * 50)
    
    # 獲取資料
    z_kriging = globals().get('z_kriging', locals().get('z_kriging'))
    ss_kriging = globals().get('ss_kriging', locals().get('ss_kriging'))
    
    if z_kriging is None or ss_kriging is None:
        print("❌ Kriging 結果未找到")
        return None
    
    # Sigma Map 統計分析
    sigma_stats = {
        'min': np.nanmin(ss_kriging),
        'max': np.nanmax(ss_kriging),
        'mean': np.nanmean(ss_kriging),
        'median': np.nanmedian(ss_kriging),
        'std': np.nanstd(ss_kriging),
        'p25': np.nanpercentile(ss_kriging, 25),
        'p75': np.nanpercentile(ss_kriging, 75)
    }
    
    # 雨量統計
    rainfall_stats = {
        'min': np.nanmin(z_kriging),
        'max': np.nanmax(z_kriging),
        'mean': np.nanmean(z_kriging),
        'median': np.nanmedian(z_kriging),
        'p75': np.nanpercentile(z_kriging, 75)
    }
    
    print("Sigma Map (Kriging Variance) 統計:")
    print(f"  範圍: {sigma_stats['min']:.4f} - {sigma_stats['max']:.4f}")
    print(f"  平均: {sigma_stats['mean']:.4f}")
    print(f"  標準差: {sigma_stats['std']:.4f}")
    print(f"  25th percentile: {sigma_stats['p25']:.4f}")
    print(f"  75th percentile: {sigma_stats['p75']:.4f}")
    
    print(f"\n雨量統計:")
    print(f"  範圍: {rainfall_stats['min']:.2f} - {rainfall_stats['max']:.2f} mm/hr")
    print(f"  平均: {rainfall_stats['mean']:.2f} mm/hr")
    print(f"  75th percentile: {rainfall_stats['p75']:.2f} mm/hr")
    
    # 不確定性分類閾值
    low_sigma = sigma_stats['p25']
    high_sigma = sigma_stats['p75']
    high_rainfall = rainfall_stats['p75']
    
    print(f"\n分類閾值:")
    print(f"  低不確定性: ≤ {low_sigma:.4f}")
    print(f"  高不確定性: ≥ {high_sigma:.4f}")
    print(f"  高雨量: ≥ {high_rainfall:.2f} mm/hr")
    
    return {
        'sigma_stats': sigma_stats,
        'rainfall_stats': rainfall_stats,
        'thresholds': {
            'low_sigma': low_sigma,
            'high_sigma': high_sigma,
            'high_rainfall': high_rainfall
        },
        'z_kriging': z_kriging,
        'ss_kriging': ss_kriging
    }

def create_risk_classification(analysis_results):
    """建立風險分類系統"""
    print("\nPhase 3: 風險分類系統")
    print("=" * 50)
    
    z_kriging = analysis_results['z_kriging']
    ss_kriging = analysis_results['ss_kriging']
    thresholds = analysis_results['thresholds']
    
    # 初始化風險地圖 (0=UNKNOWN, 1=CONFIRMED, 2=UNCERTAIN, 3=SAFE)
    risk_map = np.zeros_like(z_kriging, dtype=int)
    
    # 風險分類邏輯
    # CONFIRMED: 高雨量 + 低不確定性 → 立即撤離
    confirmed_mask = (z_kriging >= thresholds['high_rainfall']) & (ss_kriging <= thresholds['low_sigma'])
    risk_map[confirmed_mask] = 1
    
    # UNCERTAIN: 高雨量 + 高不確定性 → 部署感測器
    uncertain_mask = (z_kriging >= thresholds['high_rainfall']) & (ss_kriging >= thresholds['high_sigma'])
    risk_map[uncertain_mask] = 2
    
    # SAFE: 低雨量 → 監控
    safe_mask = z_kriging < thresholds['high_rainfall']
    risk_map[safe_mask] = 3
    
    # 統計各類別
    total_points = np.prod(risk_map.shape)
    risk_counts = {
        'CONFIRMED': np.sum(risk_map == 1),
        'UNCERTAIN': np.sum(risk_map == 2),
        'SAFE': np.sum(risk_map == 3),
        'UNKNOWN': np.sum(risk_map == 0)
    }
    
    risk_percentages = {k: (v/total_points)*100 for k, v in risk_counts.items()}
    
    print("風險分類結果:")
    print(f"  CONFIRMED (立即撤離): {risk_counts['CONFIRMED']:,} 點 ({risk_percentages['CONFIRMED']:.1f}%)")
    print(f"  UNCERTAIN (部署感測器): {risk_counts['UNCERTAIN']:,} 點 ({risk_percentages['UNCERTAIN']:.1f}%)")
    print(f"  SAFE (監控): {risk_counts['SAFE']:,} 點 ({risk_percentages['SAFE']:.1f}%)")
    print(f"  UNKNOWN (警戒): {risk_counts['UNKNOWN']:,} 點 ({risk_percentages['UNKNOWN']:.1f}%)")
    
    # 決策建議
    print(f"\n決策建議:")
    if risk_percentages['CONFIRMED'] > 5:
        print(f"  🚨 高風險區域較多 ({risk_percentages['CONFIRMED']:.1f}%)，建議立即啟動撤離程序")
    elif risk_percentages['CONFIRMED'] > 1:
        print(f"  ⚠️ 存在風險區域 ({risk_percentages['CONFIRMED']:.1f}%)，需要密切監控")
    else:
        print(f"  ✅ 風險區域較少 ({risk_percentages['CONFIRMED']:.1f}%)，保持警戒")
    
    if risk_percentages['UNCERTAIN'] > 10:
        print(f"  📡 不確定性高區域較多 ({risk_percentages['UNCERTAIN']:.1f}%)，建議部署額外感測器")
    
    return {
        'risk_map': risk_map,
        'risk_counts': risk_counts,
        'risk_percentages': risk_percentages,
        'confirmed_mask': confirmed_mask,
        'uncertain_mask': uncertain_mask,
        'safe_mask': safe_mask
    }

def create_sigma_visualization(analysis_results, risk_classification):
    """建立 Sigma Map 視覺化"""
    print("\nPhase 4: 視覺化系統")
    print("=" * 50)
    
    # 獲取資料
    z_kriging = analysis_results['z_kriging']
    ss_kriging = analysis_results['ss_kriging']
    risk_map = risk_classification['risk_map']
    
    # 獲取網格範圍
    grid_x = globals().get('grid_x', locals().get('grid_x'))
    grid_y = globals().get('grid_y', locals().get('grid_y'))
    x_min, x_max = grid_x.min(), grid_x.max()
    y_min, y_max = grid_y.min(), grid_y.max()
    
    # 獲取測站座標
    x_stations = globals().get('x', locals().get('x'))
    y_stations = globals().get('y', locals().get('y'))
    
    print(f"建立 2×2 視覺化面板...")
    
    # 建立 2×2 圖表
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Sigma Map Analysis — Kriging Uncertainty & Risk Classification', 
                fontsize=18, fontweight='bold', y=0.95)
    
    # 面板 1: Sigma Map (不確定性地圖)
    ax1 = axes[0, 0]
    im1 = ax1.imshow(ss_kriging, 
                    extent=[x_min, x_max, y_min, y_max],
                    origin='lower', 
                    cmap='viridis', 
                    aspect='auto')
    
    # 疊加測站點
    ax1.scatter(x_stations, y_stations, c='red', s=30, alpha=0.8, zorder=5, 
               edgecolors='white', linewidths=1)
    
    ax1.set_title('Sigma Map (Kriging Variance)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Easting (m)', fontsize=12)
    ax1.set_ylabel('Northing (m)', fontsize=12)
    
    # 添加色彩條
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Variance (log-space)', fontsize=10)
    
    # 添加統計資訊
    sigma_stats = analysis_results['sigma_stats']
    stats_text = f"Range: {sigma_stats['min']:.4f}-{sigma_stats['max']:.4f}\nMean: {sigma_stats['mean']:.4f}"
    ax1.text(0.02, 0.98, stats_text, 
            transform=ax1.transAxes, fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    print("  ✅ Sigma Map 面板: 完成")
    
    # 面板 2: Rainfall Map (雨量地圖)
    ax2 = axes[0, 1]
    im2 = ax2.imshow(z_kriging, 
                    extent=[x_min, x_max, y_min, y_max],
                    origin='lower', 
                    cmap='YlOrRd', 
                    aspect='auto')
    
    # 疊加測站點
    ax2.scatter(x_stations, y_stations, c='black', s=30, alpha=0.8, zorder=5,
               edgecolors='white', linewidths=1)
    
    ax2.set_title('Rainfall Prediction (Kriging)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Easting (m)', fontsize=12)
    ax2.set_ylabel('Northing (m)', fontsize=12)
    
    # 添加色彩條
    cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.8)
    cbar2.set_label('Rainfall (mm/hr)', fontsize=10)
    
    # 添加統計資訊
    rainfall_stats = analysis_results['rainfall_stats']
    rain_text = f"Range: {rainfall_stats['min']:.1f}-{rainfall_stats['max']:.1f}\nMean: {rainfall_stats['mean']:.1f}"
    ax2.text(0.02, 0.98, rain_text, 
            transform=ax2.transAxes, fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    print("  ✅ Rainfall Map 面板: 完成")
    
    # 面板 3: Risk Classification Map (風險分類地圖)
    ax3 = axes[1, 0]
    
    # 定義色彩映射
    risk_colors = ['gray', 'red', 'orange', 'green']  # UNKNOWN, CONFIRMED, UNCERTAIN, SAFE
    risk_cmap = plt.matplotlib.colors.ListedColormap(risk_colors)
    
    im3 = ax3.imshow(risk_map, 
                    extent=[x_min, x_max, y_min, y_max],
                    origin='lower', 
                    cmap=risk_cmap, 
                    vmin=0, vmax=3,
                    aspect='auto')
    
    # 疊加測站點
    ax3.scatter(x_stations, y_stations, c='black', s=30, alpha=0.8, zorder=5,
               edgecolors='white', linewidths=1)
    
    ax3.set_title('Risk Classification Map', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Easting (m)', fontsize=12)
    ax3.set_ylabel('Northing (m)', fontsize=12)
    
    # 添加圖例
    legend_elements = [
        plt.Rectangle((0,0),1,1, facecolor='red', label='CONFIRMED (Evacuate)'),
        plt.Rectangle((0,0),1,1, facecolor='orange', label='UNCERTAIN (Deploy Sensors)'),
        plt.Rectangle((0,0),1,1, facecolor='green', label='SAFE (Monitor)'),
        plt.Rectangle((0,0),1,1, facecolor='gray', label='UNKNOWN (Alert)')
    ]
    ax3.legend(handles=legend_elements, loc='upper right', fontsize=9)
    
    # 添加統計資訊
    risk_pct = risk_classification['risk_percentages']
    risk_text = f"Confirmed: {risk_pct['CONFIRMED']:.1f}%\nUncertain: {risk_pct['UNCERTAIN']:.1f}%\nSafe: {risk_pct['SAFE']:.1f}%"
    ax3.text(0.02, 0.98, risk_text, 
            transform=ax3.transAxes, fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    print("  ✅ Risk Classification 面板: 完成")
    
    # 面板 4: Decision Support (決策支援)
    ax4 = axes[1, 1]
    
    # 創建組合視圖：雨量背景 + 不確定性等高線
    im4 = ax4.imshow(z_kriging, 
                    extent=[x_min, x_max, y_min, y_max],
                    origin='lower', 
                    cmap='YlOrRd', 
                    alpha=0.7,
                    aspect='auto')
    
    # 添加不確定性等高線
    contour_levels = np.percentile(ss_kriging[~np.isnan(ss_kriging)], [25, 50, 75])
    contour = ax4.contour(grid_x, grid_y, ss_kriging, levels=contour_levels, 
                         colors='black', linewidths=1.5, alpha=0.8)
    ax4.clabel(contour, inline=True, fontsize=8, fmt='%.3f')
    
    # 疊加測站點
    ax4.scatter(x_stations, y_stations, c='blue', s=50, alpha=0.9, zorder=5,
               edgecolors='white', linewidths=2, marker='^')
    
    # 標記關鍵區域
    confirmed_mask = risk_classification['confirmed_mask']
    if np.any(confirmed_mask):
        ax4.contour(grid_x, grid_y, confirmed_mask.astype(float), levels=[0.5], 
                   colors='red', linewidths=3, linestyles='--')
    
    ax4.set_title('Decision Support View\n(Rainfall + Uncertainty Contours)', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Easting (m)', fontsize=12)
    ax4.set_ylabel('Northing (m)', fontsize=12)
    
    # 添加色彩條
    cbar4 = plt.colorbar(im4, ax=ax4, shrink=0.8)
    cbar4.set_label('Rainfall (mm/hr)', fontsize=10)
    
    # 添加說明文字
    decision_text = "Black contours: Uncertainty levels\nRed dashed: CONFIRMED zones\nBlue triangles: Weather stations"
    ax4.text(0.02, 0.02, decision_text, 
            transform=ax4.transAxes, fontsize=9,
            verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    print("  ✅ Decision Support 面板: 完成")
    
    # 調整版面
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    
    return fig

def generate_decision_report(analysis_results, risk_classification):
    """生成決策支援報告"""
    print("\nPhase 5: 決策支援報告")
    print("=" * 50)
    
    risk_pct = risk_classification['risk_percentages']
    risk_counts = risk_classification['risk_counts']
    thresholds = analysis_results['thresholds']
    
    # 生成行動建議
    actions = []
    
    # CONFIRMED 區域行動
    if risk_pct['CONFIRMED'] > 0:
        actions.append(f"🚨 立即撤離: {risk_counts['CONFIRMED']:,} 個網格點需要立即撤離")
    
    # UNCERTAIN 區域行動
    if risk_pct['UNCERTAIN'] > 0:
        actions.append(f"📡 部署感測器: {risk_counts['UNCERTAIN']:,} 個網格點需要額外監測")
    
    # SAFE 區域行動
    if risk_pct['SAFE'] > 0:
        actions.append(f"👁️ 持續監控: {risk_counts['SAFE']:,} 個網格點保持監控")
    
    # UNKNOWN 區域行動
    if risk_pct['UNKNOWN'] > 0:
        actions.append(f"⚠️ 提高警戒: {risk_counts['UNKNOWN']:,} 個網格點需要警戒")
    
    print("指揮官決策支援:")
    print("-" * 40)
    for action in actions:
        print(f"  {action}")
    
    # 優先順序建議
    print(f"\n行動優先順序:")
    priority = []
    if risk_pct['CONFIRMED'] > 0:
        priority.append("1. 立即撤離高風險區域")
    if risk_pct['UNCERTAIN'] > 5:
        priority.append("2. 部署移動感測器到不確定性高區域")
    priority.append("3. 持續監控所有區域雨量變化")
    priority.append("4. 準備額外應變資源")
    
    for item in priority:
        print(f"  {item}")
    
    # 生成文字報告
    report_lines = [
        "Sigma Map Analysis - 決策支援報告",
        "=" * 50,
        f"分析時間: 2026-04-04",
        "",
        "關鍵發現:",
        f"  • 高雨量閾值: {thresholds['high_rainfall']:.2f} mm/hr",
        f"  • 低不確定性閾值: {thresholds['low_sigma']:.4f}",
        f"  • 高不確定性閾值: {thresholds['high_sigma']:.4f}",
        "",
        "風險分類結果:",
        f"  • CONFIRMED (立即撤離): {risk_pct['CONFIRMED']:.1f}% ({risk_counts['CONFIRMED']:,} 點)",
        f"  • UNCERTAIN (部署感測器): {risk_pct['UNCERTAIN']:.1f}% ({risk_counts['UNCERTAIN']:,} 點)",
        f"  • SAFE (監控): {risk_pct['SAFE']:.1f}% ({risk_counts['SAFE']:,} 點)",
        f"  • UNKNOWN (警戒): {risk_pct['UNKNOWN']:.1f}% ({risk_counts['UNKNOWN']:,} 點)",
        "",
        "決策建議:",
    ]
    
    report_lines.extend([f"  • {action}" for action in actions])
    
    report_lines.extend([
        "",
        "技術說明:",
        "  • Sigma Map 顯示 Kriging 預測的不確定性",
        "  • 低變異數表示測站密集，估計可靠",
        "  • 高變異數表示測站稀疏，估計不確定",
        "  • 這是 Kriging 獨有的優勢功能",
        "",
        "指揮官價值:",
        "  • 識別需要立即行動的區域",
        "  • 有效分配監測資源",
        "  • 降低決策風險",
        "  • 提升應變效率"
    ])
    
    report_text = "\n".join(report_lines)
    
    # 儲存報告
    try:
        with open('sigma_map_decision_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        print("✅ 決策報告已儲存: sigma_map_decision_report.txt")
    except Exception as e:
        print(f"⚠️ 報告儲存失敗: {e}")
    
    return report_text

def save_and_validate_figure(fig):
    """儲存並驗證圖表"""
    print("\nPhase 6: 儲存與驗證")
    print("=" * 50)
    
    # 儲存圖表
    filename = 'sigma_map_analysis.png'
    
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

def main_cell9():
    """Cell 9 主要執行函數"""
    print("Lab 2 Cell 9: The Sigma Map — Kriging's Unique Weapon")
    print("Kriging 不確定性分析與決策支援系統")
    print("=" * 60)
    
    try:
        # Phase 1: 前置檢查
        if not check_prerequisites():
            print("❌ 前置檢查失敗，終止執行")
            return False
        
        # Phase 2: Sigma Map 分析
        analysis_results = analyze_sigma_map()
        if analysis_results is None:
            print("❌ Sigma Map 分析失敗")
            return False
        
        # Phase 3: 風險分類
        risk_classification = create_risk_classification(analysis_results)
        
        # Phase 4: 視覺化
        fig = create_sigma_visualization(analysis_results, risk_classification)
        
        # Phase 5: 決策報告
        report = generate_decision_report(analysis_results, risk_classification)
        
        # Phase 6: 儲存與驗證
        success, filename = save_and_validate_figure(fig)
        
        if success:
            # 顯示圖表
            plt.show()
            
            print("\n" + "=" * 60)
            print("🎉 Cell 9 實作完成！")
            print("=" * 60)
            print("輸出成果:")
            print(f"  - 圖表檔案: {filename}")
            print("  - 決策報告: sigma_map_decision_report.txt")
            print("\nSigma Map 分析完成，為指揮官提供決策支援")
            print("這是 Kriging 獨有的不確定性估計功能！")
            
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
# Lab 2 Cell 9: The Sigma Map — Kriging's Unique Weapon
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 檢查必要變數
required_vars = ['z_kriging', 'ss_kriging', 'grid_x', 'grid_y', 'x', 'y']
missing_vars = [var for var in required_vars if var not in locals() and var not in globals()]

if missing_vars:
    raise NameError(f"缺少必要變數: {missing_vars}. 請先執行 Cell 1-3")

print(f"✅ 前置檢查通過: 所有必要變數可用")

# Sigma Map 分析
sigma_stats = {
    'min': np.nanmin(ss_kriging),
    'max': np.nanmax(ss_kriging),
    'mean': np.nanmean(ss_kriging),
    'p25': np.nanpercentile(ss_kriging, 25),
    'p75': np.nanpercentile(ss_kriging, 75)
}

rainfall_stats = {
    'min': np.nanmin(z_kriging),
    'max': np.nanmax(z_kriging),
    'p75': np.nanpercentile(z_kriging, 75)
}

print("Sigma Map 統計:")
print(f"  範圍: {sigma_stats['min']:.4f} - {sigma_stats['max']:.4f}")
print(f"  平均: {sigma_stats['mean']:.4f}")
print(f"  25th/75th percentile: {sigma_stats['p25']:.4f} / {sigma_stats['p75']:.4f}")

# 風險分類閾值
low_sigma = sigma_stats['p25']
high_sigma = sigma_stats['p75']
high_rainfall = rainfall_stats['p75']

print(f"\\n分類閾值:")
print(f"  高雨量: ≥ {high_rainfall:.2f} mm/hr")
print(f"  低不確定性: ≤ {low_sigma:.4f}")
print(f"  高不確定性: ≥ {high_sigma:.4f}")

# 建立風險分類
risk_map = np.zeros_like(z_kriging, dtype=int)
risk_map[(z_kriging >= high_rainfall) & (ss_kriging <= low_sigma)] = 1  # CONFIRMED
risk_map[(z_kriging >= high_rainfall) & (ss_kriging >= high_sigma)] = 2  # UNCERTAIN
risk_map[z_kriging < high_rainfall] = 3  # SAFE

# 統計結果
total_points = np.prod(risk_map.shape)
confirmed_pct = np.sum(risk_map == 1) / total_points * 100
uncertain_pct = np.sum(risk_map == 2) / total_points * 100
safe_pct = np.sum(risk_map == 3) / total_points * 100

print(f"\\n風險分類結果:")
print(f"  CONFIRMED (立即撤離): {confirmed_pct:.1f}%")
print(f"  UNCERTAIN (部署感測器): {uncertain_pct:.1f}%")
print(f"  SAFE (監控): {safe_pct:.1f}%")

# 建立視覺化
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Sigma Map Analysis — Kriging Uncertainty & Risk Classification', fontsize=16)

# 網格範圍
x_min, x_max = grid_x.min(), grid_x.max()
y_min, y_max = grid_y.min(), grid_y.max()

# 面板 1: Sigma Map
axes[0,0].imshow(ss_kriging, extent=[x_min, x_max, y_min, y_max], 
                origin='lower', cmap='viridis', aspect='auto')
axes[0,0].scatter(x, y, c='red', s=30, alpha=0.8, edgecolors='white', linewidths=1)
axes[0,0].set_title('Sigma Map (Kriging Variance)')
axes[0,0].set_xlabel('Easting (m)')
axes[0,0].set_ylabel('Northing (m)')
plt.colorbar(axes[0,0].images[0], ax=axes[0,0], label='Variance')

# 面板 2: Rainfall Map
axes[0,1].imshow(z_kriging, extent=[x_min, x_max, y_min, y_max], 
                origin='lower', cmap='YlOrRd', aspect='auto')
axes[0,1].scatter(x, y, c='black', s=30, alpha=0.8, edgecolors='white', linewidths=1)
axes[0,1].set_title('Rainfall Prediction')
axes[0,1].set_xlabel('Easting (m)')
axes[0,1].set_ylabel('Northing (m)')
plt.colorbar(axes[0,1].images[0], ax=axes[0,1], label='Rainfall (mm/hr)')

# 面板 3: Risk Classification
risk_colors = ['gray', 'red', 'orange', 'green']
risk_cmap = plt.matplotlib.colors.ListedColormap(risk_colors)
im3 = axes[1,0].imshow(risk_map, extent=[x_min, x_max, y_min, y_max], 
                      origin='lower', cmap=risk_cmap, vmin=0, vmax=3, aspect='auto')
axes[1,0].scatter(x, y, c='black', s=30, alpha=0.8, edgecolors='white', linewidths=1)
axes[1,0].set_title('Risk Classification Map')
axes[1,0].set_xlabel('Easting (m)')
axes[1,0].set_ylabel('Northing (m)')

# 風險圖例
legend_elements = [
    plt.Rectangle((0,0),1,1, facecolor='red', label='CONFIRMED (Evacuate)'),
    plt.Rectangle((0,0),1,1, facecolor='orange', label='UNCERTAIN (Sensors)'),
    plt.Rectangle((0,0),1,1, facecolor='green', label='SAFE (Monitor)'),
    plt.Rectangle((0,0),1,1, facecolor='gray', label='UNKNOWN')
]
axes[1,0].legend(handles=legend_elements, loc='upper right', fontsize=8)

# 面板 4: Decision Support
axes[1,1].imshow(z_kriging, extent=[x_min, x_max, y_min, y_max], 
                origin='lower', cmap='YlOrRd', alpha=0.7, aspect='auto')
axes[1,1].contour(grid_x, grid_y, ss_kriging, 
                 levels=[low_sigma, sigma_stats['mean'], high_sigma], 
                 colors='black', linewidths=1.5)
axes[1,1].scatter(x, y, c='blue', s=40, alpha=0.9, marker='^', 
                  edgecolors='white', linewidths=2)
axes[1,1].set_title('Decision Support View')
axes[1,1].set_xlabel('Easting (m)')
axes[1,1].set_ylabel('Northing (m)')
plt.colorbar(axes[1,1].images[0], ax=axes[1,1], label='Rainfall (mm/hr)')

plt.tight_layout()
plt.savefig('sigma_map_analysis.png', dpi=300, bbox_inches='tight')
print("✅ 圖表已儲存: sigma_map_analysis.png")

plt.show()

print("\\n🎯 指揮官決策支援:")
print("🔴 CONFIRMED: 高雨量 + 低不確定性 = 立即撤離")
print("🟠 UNCERTAIN: 高雨量 + 高不確定性 = 部署感測器")
print("🟢 SAFE: 低雨量 = 持續監控")
print("⚪ UNKNOWN: 警戒狀態")

print("\\n✅ Sigma Map 分析完成！")
print("這是 Kriging 獨有的不確定性估計功能！")
'''

if __name__ == "__main__":
    # 獨立執行模式（用於測試）
    print("Cell 9 獨立執行模式")
    print("注意：需要先載入所有必要變數")
    success = main_cell9()
else:
    print("Cell 9 模組已載入")
    print("使用 main_cell9() 函數執行完整 Sigma Map 分析")

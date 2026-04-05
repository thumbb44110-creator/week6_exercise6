#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 7: Four Methods Side by Side (Slide 13)
Lab 1: The Four-Way Interpolation Shootout

Create a 2×2 figure comparing all four interpolation methods.

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
        '插值結果': ['z_nn', 'z_idw', 'z_kriging', 'z_rf'],
        '網格座標': ['grid_x', 'grid_y', 'grid_xx', 'grid_yy'],
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
        print("請確保已執行 Cell 1-6")
        return False
    
    # 檢查陣列形狀一致性
    print(f"\n陣列形狀檢查:")
    interpolation_vars = ['z_nn', 'z_idw', 'z_kriging', 'z_rf']
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

def calculate_unified_range():
    """計算統一的色彩範圍"""
    print("\nPhase 2: 計算統一色彩範圍")
    print("=" * 50)
    
    interpolation_results = ['z_nn', 'z_idw', 'z_kriging', 'z_rf']
    ranges = {}
    
    for var in interpolation_results:
        var_value = globals().get(var, locals().get(var))
        if var_value is not None:
            var_min = np.nanmin(var_value)
            var_max = np.nanmax(var_value)
            var_mean = np.nanmean(var_value)
            ranges[var] = {'min': var_min, 'max': var_max, 'mean': var_mean}
            print(f"  {var}: {var_min:.2f} - {var_max:.2f} mm/hr (平均: {var_mean:.2f})")
    
    # 計算統一範圍
    all_mins = [r['min'] for r in ranges.values()]
    all_maxs = [r['max'] for r in ranges.values()]
    
    vmin = min(all_mins)
    vmax = max(all_maxs)
    
    print(f"\n統一色彩範圍: {vmin:.2f} - {vmax:.2f} mm/hr")
    
    return vmin, vmax, ranges

def create_comparison_figure(vmin, vmax, ranges):
    """建立四種方法的比較圖表"""
    print("\nPhase 3: 建立比較圖表")
    print("=" * 50)
    
    # 建立圖表
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle('Lab 1: Four-Way Interpolation Shootout', 
                fontsize=18, fontweight='bold', y=0.95)
    
    # 方法配置
    methods = [
        {'name': 'Nearest Neighbor', 'var': 'z_nn', 'title': 'Voronoi Patchwork'},
        {'name': 'IDW', 'var': 'z_idw', 'title': 'Bullseye Effect'},
        {'name': 'Kriging', 'var': 'z_kriging', 'title': 'Smooth + Sigma Map'},
        {'name': 'Random Forest', 'var': 'z_rf', 'title': 'ML Block Artifacts'}
    ]
    
    # 獲取網格範圍
    grid_x = globals().get('grid_x', locals().get('grid_x'))
    grid_y = globals().get('grid_y', locals().get('grid_y'))
    x_min, x_max = grid_x.min(), grid_x.max()
    y_min, y_max = grid_y.min(), grid_y.max()
    
    # 獲取測站座標
    x_stations = globals().get('x', locals().get('x'))
    y_stations = globals().get('y', locals().get('y'))
    z_stations = globals().get('z', locals().get('z'))
    
    print(f"網格範圍: {x_min:.0f} - {x_max:.0f} m (Easting)")
    print(f"網格範圍: {y_min:.0f} - {y_max:.0f} m (Northing)")
    print(f"測站數量: {len(x_stations)}")
    
    # 繪製每個方法
    for idx, method in enumerate(methods):
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]
        
        # 獲取插值結果
        result_var = globals().get(method['var'], locals().get(method['var']))
        
        if result_var is not None:
            # 繪製插值結果
            im = ax.imshow(result_var, 
                          extent=[x_min, x_max, y_min, y_max],
                          origin='lower', 
                          cmap='YlOrRd', 
                          vmin=vmin, 
                          vmax=vmax,
                          aspect='auto')
            
            # 疊加測站點
            scatter = ax.scatter(x_stations, y_stations, 
                               c=z_stations, 
                               s=40, 
                               cmap='YlOrRd', 
                               vmin=vmin, 
                               vmax=vmax,
                               edgecolors='black', 
                               linewidths=1,
                               alpha=0.8,
                               zorder=5)
            
            # 設定標題和標籤
            ax.set_title(f'{method["name"]}\n{method["title"]}', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Easting (m)', fontsize=12)
            ax.set_ylabel('Northing (m)', fontsize=12)
            
            # 添加色彩條
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('Rainfall (mm/hr)', fontsize=10)
            
            # 添加統計資訊
            stats = ranges[method['var']]
            info_text = f"Range: {stats['min']:.1f}-{stats['max']:.1f}\nMean: {stats['mean']:.1f}"
            ax.text(0.02, 0.98, info_text, 
                   transform=ax.transAxes, 
                   fontsize=9,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            print(f"  ✅ {method['name']}: 繪製完成")
        else:
            print(f"  ❌ {method['name']}: 變數 {method['var']} 未找到")
    
    # 調整版面
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    return fig

def save_and_validate_figure(fig):
    """儲存並驗證圖表"""
    print("\nPhase 4: 儲存與驗證")
    print("=" * 50)
    
    # 儲存圖表
    filename = 'interpolation_shootout.png'
    
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

def generate_summary_report(ranges, filename):
    """生成統計摘要報告"""
    print("\nPhase 5: 統計摘要")
    print("=" * 50)
    
    print("四種插值方法統計比較:")
    print("-" * 60)
    print(f"{'方法':<15} {'最小值':<10} {'最大值':<10} {'平均值':<10} {'範圍':<10}")
    print("-" * 60)
    
    for var_name, stats in ranges.items():
        method_name = var_name.replace('z_', '').title()
        range_val = stats['max'] - stats['min']
        print(f"{method_name:<15} {stats['min']:<10.2f} {stats['max']:<10.2f} "
              f"{stats['mean']:<10.2f} {range_val:<10.2f}")
    
    # 計算整體統計
    all_means = [s['mean'] for s in ranges.values()]
    all_ranges = [s['max'] - s['min'] for s in ranges.values()]
    
    print("-" * 60)
    print(f"整體平均: {np.mean(all_means):.2f} mm/hr")
    print(f"平均範圍: {np.mean(all_ranges):.2f} mm/hr")
    
    # 生成文字報告
    report_lines = [
        "Cell 7: Four Methods Side by Side - 執行報告",
        "=" * 50,
        f"執行時間: 2026-04-03",
        f"輸出檔案: {filename}",
        "",
        "方法比較:",
        "  1. Nearest Neighbor: Voronoi Patchwork - 塊狀分佈",
        "  2. IDW: Bullseye Effect - 距離加權平滑",  
        "  3. Kriging: Smooth + Sigma Map - 統計最佳插值",
        "  4. Random Forest: ML Block Artifacts - 機器學習預測",
        "",
        "關鍵觀察:",
        "  - 不同方法產生不同的空間模式",
        "  - 色彩範圍統一便於比較",
        "  - 測站點疊加顯示原始資料位置",
        "  - 各方法適用不同應用場景",
        "",
        "後續應用:",
        f"  - 圖表可用於 Lab 1 最終報告",
        f"  - 支援方法選擇決策",
        f"  - 可進行定量比較分析"
    ]
    
    report_text = "\n".join(report_lines)
    
    # 儲存報告
    try:
        with open('cell7_execution_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        print("✅ 報告已儲存: cell7_execution_report.txt")
    except Exception as e:
        print(f"⚠️ 報告儲存失敗: {e}")
    
    return report_text

def main_cell7():
    """Cell 7 主要執行函數"""
    print("Lab 1 Cell 7: Four Methods Side by Side")
    print("四種插值方法視覺化比較")
    print("=" * 60)
    
    try:
        # Phase 1: 前置檢查
        if not check_prerequisites():
            print("❌ 前置檢查失敗，終止執行")
            return False
        
        # Phase 2: 計算統一色彩範圍
        vmin, vmax, ranges = calculate_unified_range()
        
        # Phase 3: 建立比較圖表
        fig = create_comparison_figure(vmin, vmax, ranges)
        
        # Phase 4: 儲存與驗證
        success, filename = save_and_validate_figure(fig)
        
        if success:
            # Phase 5: 生成摘要報告
            report = generate_summary_report(ranges, filename)
            
            # 顯示圖表
            plt.show()
            
            print("\n" + "=" * 60)
            print("🎉 Cell 7 實作完成！")
            print("=" * 60)
            print("輸出成果:")
            print(f"  - 圖表檔案: {filename}")
            print("  - 執行報告: cell7_execution_report.txt")
            print("\n四種方法比較完成，可用於後續分析")
            
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
# Lab 1 Cell 7: Four Methods Side by Side
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 檢查必要變數
required_vars = ['z_nn', 'z_idw', 'z_kriging', 'z_rf', 'grid_x', 'grid_y', 'x', 'y', 'z']
missing_vars = [var for var in required_vars if var not in locals() and var not in globals()]

if missing_vars:
    raise NameError(f"缺少必要變數: {missing_vars}. 請先執行 Cell 1-6")

print(f"✅ 前置檢查通過: 所有必要變數可用")

# 計算統一色彩範圍
interpolation_results = [z_nn, z_idw, z_kriging, z_rf]
vmin = min([np.nanmin(result) for result in interpolation_results])
vmax = max([np.nanmax(result) for result in interpolation_results])

print(f"統一色彩範圍: {vmin:.2f} - {vmax:.2f} mm/hr")

# 建立 2×2 比較圖表
fig, axes = plt.subplots(2, 2, figsize=(16, 14))
fig.suptitle('Lab 1: Four-Way Interpolation Shootout', 
            fontsize=18, fontweight='bold', y=0.95)

# 方法配置
methods = [
    {'name': 'Nearest Neighbor', 'data': z_nn, 'title': 'Voronoi Patchwork'},
    {'name': 'IDW', 'data': z_idw, 'title': 'Bullseye Effect'},
    {'name': 'Kriging', 'data': z_kriging, 'title': 'Smooth + Sigma Map'},
    {'name': 'Random Forest', 'data': z_rf, 'title': 'ML Block Artifacts'}
]

# 網格範圍
x_min, x_max = grid_x.min(), grid_x.max()
y_min, y_max = grid_y.min(), grid_y.max()

# 繪製每個方法
for idx, method in enumerate(methods):
    row = idx // 2
    col = idx % 2
    ax = axes[row, col]
    
    # 繪製插值結果
    im = ax.imshow(method['data'], 
                  extent=[x_min, x_max, y_min, y_max],
                  origin='lower', 
                  cmap='YlOrRd', 
                  vmin=vmin, 
                  vmax=vmax,
                  aspect='auto')
    
    # 疊加測站點
    ax.scatter(x, y, c=z, s=40, cmap='YlOrRd', vmin=vmin, vmax=vmax,
              edgecolors='black', linewidths=1, alpha=0.8, zorder=5)
    
    # 設定標題和標籤
    ax.set_title(f'{method["name"]}\\n{method["title"]}', 
                fontsize=14, fontweight='bold')
    ax.set_xlabel('Easting (m)', fontsize=12)
    ax.set_ylabel('Northing (m)', fontsize=12)
    
    # 添加色彩條
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Rainfall (mm/hr)', fontsize=10)
    
    # 添加統計資訊
    stats_text = f"Range: {np.nanmin(method['data']):.1f}-{np.nanmax(method['data']):.1f}\\nMean: {np.nanmean(method['data']):.1f}"
    ax.text(0.02, 0.98, stats_text, 
           transform=ax.transAxes, fontsize=9,
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# 調整版面
plt.tight_layout()
plt.subplots_adjust(top=0.92)

# 儲存圖表
plt.savefig('interpolation_shootout.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✅ 圖表已儲存: interpolation_shootout.png")

# 顯示圖表
plt.show()

print("\\n✅ Four Methods Side by Side 完成!")
'''

if __name__ == "__main__":
    # 獨立執行模式（用於測試）
    print("Cell 7 獨立執行模式")
    print("注意：需要先載入所有必要變數")
    success = main_cell7()
else:
    print("Cell 7 模組已載入")
    print("使用 main_cell7() 函數執行完整比較流程")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 9b: Nugget Effect — Why Extreme Rain Gets Diluted
Lab 2: Confidence & Uncertainty Diagnosis

Compare Nugget=10% vs Nugget=1% on a zoomed-in map around Suao.
Which preserves the extreme rainfall better?

Author: thumbb44110-creator
Date: 2026-04-04
"""

import numpy as np
import matplotlib.pyplot as plt
from pykrige.ok import OrdinaryKriging
import warnings
warnings.filterwarnings('ignore')

def check_prerequisites():
    """檢查必要的前置變數"""
    print("Phase 1: 前置變數檢查")
    print("=" * 50)
    
    required_vars = {
        '測站資料': ['x', 'y', 'z'],
        '對數轉換': ['z_log']
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
        print("請確保已執行 Cell 1-3 (資料載入和 Kriging 實作)")
        return False
    
    return True

def identify_extreme_station():
    """識別極端雨量測站 (Suao)"""
    print("\nPhase 2: 識別極端雨量測站")
    print("=" * 50)
    
    # 獲取資料
    x = globals().get('x', locals().get('x'))
    y = globals().get('y', locals().get('y'))
    z = globals().get('z', locals().get('z'))
    
    if x is None or y is None or z is None:
        print("❌ 測站資料未找到")
        return None
    
    # 找到最大雨量測站
    suao_idx = np.argmax(z)
    suao_x, suao_y, suao_z = x[suao_idx], y[suao_idx], z[suao_idx]
    
    print(f"極端雨量測站分析:")
    print(f"  測站索引: {suao_idx}")
    print(f"  座標: ({suao_x:.0f}, {suao_y:.0f})")
    print(f"  雨量: {suao_z:.1f} mm/hr")
    
    # 驗證是否為 Suao (130.5 mm/hr)
    if abs(suao_z - 130.5) < 1.0:
        print(f"  ✅ 確認為 Suao 測站 (130.5 mm/hr)")
    else:
        print(f"  ⚠️ 雨量值 {suao_z:.1f} 與預期 130.5 mm/hr 有差異")
    
    # 計算基本統計
    print(f"\n所有測站雨量統計:")
    print(f"  範圍: {z.min():.1f} - {z.max():.1f} mm/hr")
    print(f"  平均: {z.mean():.1f} mm/hr")
    print(f"  最大值排名: 第1位 (共{len(z)}個測站)")
    
    return {
        'index': suao_idx,
        'x': suao_x,
        'y': suao_y,
        'z': suao_z,
        'is_suao': abs(suao_z - 130.5) < 1.0
    }

def create_local_grid(station_info):
    """建立以 Suao 為中心的局部網格"""
    print("\nPhase 3: 建立局部網格")
    print("=" * 50)
    
    suao_x, suao_y = station_info['x'], station_info['y']
    
    # 網格參數
    grid_size = 20000  # 20km × 20km
    resolution = 100   # 100m 解析度
    half_size = grid_size // 2
    
    print(f"局部網格參數:")
    print(f"  中心: ({suao_x:.0f}, {suao_y:.0f})")
    print(f"  尺寸: {grid_size/1000:.0f}km × {grid_size/1000:.0f}km")
    print(f"  解析度: {resolution}m")
    print(f"  網格點數: {(grid_size//resolution + 1)}×{(grid_size//resolution + 1)}")
    
    # 建立網格
    grid_extent = np.linspace(-half_size, half_size, grid_size//resolution + 1)
    local_grid_x = suao_x + grid_extent
    local_grid_y = suao_y + grid_extent
    local_xx, local_yy = np.meshgrid(local_grid_x, local_grid_y)
    
    print(f"網格範圍:")
    print(f"  X: {local_grid_x.min():.0f} - {local_grid_x.max():.0f}")
    print(f"  Y: {local_grid_y.min():.0f} - {local_grid_y.max():.0f}")
    
    return {
        'grid_x': local_grid_x,
        'grid_y': local_grid_y,
        'grid_xx': local_xx,
        'grid_yy': local_yy,
        'resolution': resolution,
        'size': grid_size
    }

def create_kriging_models():
    """建立兩種不同 Nugget 設定的 Kriging 模型"""
    print("\nPhase 4: 建立 Kriging 模型")
    print("=" * 50)
    
    # 獲取資料
    x = globals().get('x', locals().get('x'))
    y = globals().get('y', locals().get('y'))
    z_log = globals().get('z_log', locals().get('z_log'))
    
    if x is None or y is None or z_log is None:
        print("❌ 必要資料未找到")
        return None
    
    # 計算 sill
    sill_val = float(z_log.var())
    
    print(f"Kriging 參數設定:")
    print(f"  Sill: {sill_val:.4f}")
    print(f"  Range: 50000.0 m (50km)")
    print(f"  Model: Spherical")
    
    # 高 Nugget 模型 (10%)
    high_nugget = sill_val * 0.10
    print(f"\n高 Nugget 模型 (10%):")
    print(f"  Nugget: {high_nugget:.4f}")
    
    try:
        OK_high = OrdinaryKriging(x, y, z_log, variogram_model='spherical',
                                verbose=False, enable_plotting=False, nlags=15,
                                variogram_parameters={
                                    'sill': sill_val,
                                    'range': 50000.0,
                                    'nugget': high_nugget
                                })
        print(f"  ✅ 高 Nugget 模型建立成功")
    except Exception as e:
        print(f"  ❌ 高 Nugget 模型失敗: {e}")
        return None
    
    # 低 Nugget 模型 (1%)
    low_nugget = sill_val * 0.01
    print(f"\n低 Nugget 模型 (1%):")
    print(f"  Nugget: {low_nugget:.4f}")
    
    try:
        OK_low = OrdinaryKriging(x, y, z_log, variogram_model='spherical',
                               verbose=False, enable_plotting=False, nlags=15,
                               variogram_parameters={
                                   'sill': sill_val,
                                   'range': 50000.0,
                                   'nugget': low_nugget
                               })
        print(f"  ✅ 低 Nugget 模型建立成功")
    except Exception as e:
        print(f"  ❌ 低 Nugget 模型失敗: {e}")
        return None
    
    return {
        'OK_high': OK_high,
        'OK_low': OK_low,
        'sill': sill_val,
        'high_nugget': high_nugget,
        'low_nugget': low_nugget
    }

def predict_on_local_grid(models, local_grid):
    """在局部網格上進行預測"""
    print("\nPhase 5: 局部網格預測")
    print("=" * 50)
    
    OK_high = models['OK_high']
    OK_low = models['OK_low']
    local_xx = local_grid['grid_xx']
    local_yy = local_grid['grid_yy']
    
    print(f"執行 Kriging 預測...")
    
    try:
        # 高 Nugget 預測
        print("  高 Nugget 模型預測中...")
        z_high_log, ss_high_log = OK_high.execute('grid', 
                                                local_grid['grid_x'], 
                                                local_grid['grid_y'])
        z_high = np.expm1(z_high_log)
        z_high[z_high < 0] = 0
        
        print(f"    ✅ 高 Nugget 預測完成")
        print(f"    範圍: {z_high.min():.1f} - {z_high.max():.1f} mm/hr")
        
    except Exception as e:
        print(f"    ❌ 高 Nugget 預測失敗: {e}")
        return None
    
    try:
        # 低 Nugget 預測
        print("  低 Nugget 模型預測中...")
        z_low_log, ss_low_log = OK_low.execute('grid', 
                                              local_grid['grid_x'], 
                                              local_grid['grid_y'])
        z_low = np.expm1(z_low_log)
        z_low[z_low < 0] = 0
        
        print(f"    ✅ 低 Nugget 預測完成")
        print(f"    範圍: {z_low.min():.1f} - {z_low.max():.1f} mm/hr")
        
    except Exception as e:
        print(f"    ❌ 低 Nugget 預測失敗: {e}")
        return None
    
    return {
        'z_high': z_high,
        'z_low': z_low,
        'ss_high': ss_high_log,
        'ss_low': ss_low_log
    }

def predict_at_distances(models, station_info):
    """在特定距離進行預測"""
    print("\nPhase 6: 距離預測分析")
    print("=" * 50)
    
    OK_high = models['OK_high']
    OK_low = models['OK_low']
    suao_x, suao_y = station_info['x'], station_info['y']
    
    # 預測距離和方向
    distances = [0, 500, 1000, 2000]  # meters
    directions = ['east', 'west', 'north', 'south']
    
    print(f"距離預測分析:")
    print(f"  距離: {distances} m")
    print(f"  方向: {directions}")
    
    results = {}
    
    for dist in distances:
        results[dist] = {}
        
        for direction in directions:
            # 計算預測點座標
            if direction == 'east':
                pred_x, pred_y = suao_x + dist, suao_y
            elif direction == 'west':
                pred_x, pred_y = suao_x - dist, suao_y
            elif direction == 'north':
                pred_x, pred_y = suao_x, suao_y + dist
            else:  # south
                pred_x, pred_y = suao_x, suao_y - dist
            
            try:
                # 高 Nugget 預測
                pred_high_log = OK_high.execute('points', pred_x, pred_y)[0]
                pred_high = np.expm1(pred_high_log[0])
                pred_high = max(pred_high, 0)
                
                # 低 Nugget 預測
                pred_low_log = OK_low.execute('points', pred_x, pred_y)[0]
                pred_low = np.expm1(pred_low_log[0])
                pred_low = max(pred_low, 0)
                
                results[dist][direction] = {
                    'high': pred_high,
                    'low': pred_low,
                    'difference': pred_low - pred_high,
                    'high_preservation': pred_high / station_info['z'] * 100,
                    'low_preservation': pred_low / station_info['z'] * 100
                }
                
            except Exception as e:
                print(f"    ❌ 預測失敗 ({direction} {dist}m): {e}")
                results[dist][direction] = None
    
    # 顯示結果表格
    print(f"\n距離預測結果:")
    print(f"{'距離':<6} {'方向':<6} {'高Nugget':<10} {'低Nugget':<10} {'差異':<8} {'高保留%':<8} {'低保留%':<8}")
    print("-" * 70)
    
    for dist in distances:
        for direction in directions:
            result = results[dist][direction]
            if result:
                print(f"{dist:<6} {direction:<6} {result['high']:<10.1f} {result['low']:<10.1f} "
                      f"{result['difference']:<8.1f} {result['high_preservation']:<8.1f} "
                      f"{result['low_preservation']:<8.1f}")
    
    return results

def create_comparison_visualization(station_info, local_grid, predictions, distance_results):
    """建立並排比較視覺化"""
    print("\nPhase 7: 建立比較視覺化")
    print("=" * 50)
    
    suao_x, suao_y = station_info['x'], station_info['y']
    suao_z = station_info['z']
    local_xx = local_grid['grid_xx']
    local_yy = local_grid['grid_yy']
    z_high = predictions['z_high']
    z_low = predictions['z_low']
    
    print(f"建立並排比較圖表...")
    
    # 建立 1×2 圖表
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle('Nugget Effect on Extreme Rainfall Preservation\n(Suao Station: 130.5 mm/hr)', 
                fontsize=16, fontweight='bold')
    
    # 統一色彩範圍
    vmin, vmax = 0, 140  # 基於 Suao 的 130.5 mm/hr
    
    # 左側面板：高 Nugget (10%)
    ax1 = axes[0]
    im1 = ax1.imshow(z_high, extent=[local_grid['grid_x'].min(), local_grid['grid_x'].max(),
                                   local_grid['grid_y'].min(), local_grid['grid_y'].max()],
                    origin='lower', cmap='YlOrRd', vmin=vmin, vmax=vmax, aspect='auto')
    
    # 添加距離圓圈
    for radius in [500, 1000, 2000]:
        circle = plt.Circle((suao_x, suao_y), radius, fill=False, 
                           edgecolor='black', linewidth=1.5, linestyle='--', alpha=0.7)
        ax1.add_patch(circle)
    
    # 標記 Suao 測站
    ax1.plot(suao_x, suao_y, 'b^', markersize=15, markeredgecolor='white', 
            markeredgewidth=2, label=f'Suao ({suao_z:.1f} mm/hr)')
    
    ax1.set_title('High Nugget (10%)\nHeavy Smoothing', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Easting (m)', fontsize=12)
    ax1.set_ylabel('Northing (m)', fontsize=12)
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # 添加色彩條
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Rainfall (mm/hr)', fontsize=10)
    
    # 添加距離標籤
    for radius in [500, 1000, 2000]:
        ax1.text(suao_x + radius, suao_y, f'{radius}m', 
                ha='center', va='bottom', fontsize=8, color='black')
    
    print("  ✅ 高 Nugget 面板: 完成")
    
    # 右側面板：低 Nugget (1%)
    ax2 = axes[1]
    im2 = ax2.imshow(z_low, extent=[local_grid['grid_x'].min(), local_grid['grid_x'].max(),
                                  local_grid['grid_y'].min(), local_grid['grid_y'].max()],
                    origin='lower', cmap='YlOrRd', vmin=vmin, vmax=vmax, aspect='auto')
    
    # 添加距離圓圈
    for radius in [500, 1000, 2000]:
        circle = plt.Circle((suao_x, suao_y), radius, fill=False, 
                           edgecolor='black', linewidth=1.5, linestyle='--', alpha=0.7)
        ax2.add_patch(circle)
    
    # 標記 Suao 測站
    ax2.plot(suao_x, suao_y, 'b^', markersize=15, markeredgecolor='white', 
            markeredgewidth=2, label=f'Suao ({suao_z:.1f} mm/hr)')
    
    ax2.set_title('Low Nugget (1%)\nExtreme Preserved', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Easting (m)', fontsize=12)
    ax2.set_ylabel('Northing (m)', fontsize=12)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    # 添加色彩條
    cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.8)
    cbar2.set_label('Rainfall (mm/hr)', fontsize=10)
    
    # 添加距離標籤
    for radius in [500, 1000, 2000]:
        ax2.text(suao_x + radius, suao_y, f'{radius}m', 
                ha='center', va='bottom', fontsize=8, color='black')
    
    print("  ✅ 低 Nugget 面板: 完成")
    
    # 調整版面
    plt.tight_layout()
    
    return fig

def generate_analysis_report(station_info, models, distance_results):
    """生成分析報告"""
    print("\nPhase 8: 生成分析報告")
    print("=" * 50)
    
    suao_z = station_info['z']
    
    # 計算關鍵指標
    print("關鍵發現:")
    
    # 0m 處的預測值
    zero_m_high = distance_results[0]['east']['high']
    zero_m_low = distance_results[0]['east']['low']
    
    print(f"\n在測站位置 (0m):")
    print(f"  高 Nugget (10%): {zero_m_high:.1f} mm/hr ({zero_m_high/suao_z*100:.1f}% 保留)")
    print(f"  低 Nugget (1%): {zero_m_low:.1f} mm/hr ({zero_m_low/suao_z*100:.1f}% 保留)")
    print(f"  差異: {zero_m_low - zero_m_high:.1f} mm/hr")
    
    # 500m 處的預測值
    m500_high = distance_results[500]['east']['high']
    m500_low = distance_results[500]['east']['low']
    
    print(f"\n在 500m 處:")
    print(f"  高 Nugget (10%): {m500_high:.1f} mm/hr")
    print(f"  低 Nugget (1%): {m500_low:.1f} mm/hr")
    print(f"  差異: {m500_low - m500_high:.1f} mm/hr")
    
    # 衰減率分析
    print(f"\n衰減率分析:")
    high_decay = (zero_m_high - m500_high) / zero_m_high * 100
    low_decay = (zero_m_low - m500_low) / zero_m_low * 100
    print(f"  高 Nugget 衰減率: {high_decay:.1f}% (0m → 500m)")
    print(f"  低 Nugget 衰減率: {low_decay:.1f}% (0m → 500m)")
    
    # 結論
    print(f"\n🎯 結論:")
    if zero_m_low > zero_m_high:
        print(f"  ✅ 低 Nugget (1%) 更好保留極端值")
        print(f"  ✅ 在測站位置保留 {zero_m_low/suao_z*100:.1f}% 的原始雨量")
        print(f"  ✅ 在 500m 處仍保持 {m500_low:.1f} mm/hr")
    else:
        print(f"  ⚠️ 高 Nugget (10%) 意外保留更多極端值")
    
    print(f"\n💡 對指揮官的意義:")
    print(f"  • 低 Nugget 提供更準確的極端降雨預測")
    print(f"  • 高 Nugget 可能低估撤離風險")
    print(f"  • 建議使用低 Nugget 設定進行極端事件分析")
    
    # 生成文字報告
    report_lines = [
        "Nugget Effect Analysis - 極端雨量保留分析報告",
        "=" * 60,
        f"分析時間: 2026-04-04",
        f"目標測站: Suao ({suao_z:.1f} mm/hr)",
        "",
        "模型參數:",
        f"  • 高 Nugget: {models['high_nugget']:.4f} (10% of sill)",
        f"  • 低 Nugget: {models['low_nugget']:.4f} (1% of sill)",
        f"  • Sill: {models['sill']:.4f}",
        f"  • Range: 50km",
        f"  • Model: Spherical variogram",
        "",
        "關鍵發現:",
        f"  • 測站位置預測 (0m):",
        f"    - 高 Nugget: {zero_m_high:.1f} mm/hr ({zero_m_high/suao_z*100:.1f}%)",
        f"    - 低 Nugget: {zero_m_low:.1f} mm/hr ({zero_m_low/suao_z*100:.1f}%)",
        f"  • 500m 處預測:",
        f"    - 高 Nugget: {m500_high:.1f} mm/hr",
        f"    - 低 Nugget: {m500_low:.1f} mm/hr",
        "",
        "衰減分析:",
        f"  • 高 Nugget 衰減率: {high_decay:.1f}%",
        f"  • 低 Nugget 衰減率: {low_decay:.1f}%",
        "",
        "結論:",
        "  • 低 Nugget 更好保留極端雨量值",
        "  • 高 Nugget 過度平滑，可能低估風險",
        "  • 建議極端事件分析使用低 Nugget 設定",
        "",
        "實務意義:",
        "  • 撤離決策需要準確的極值預測",
        "  • 低 Nugget 提供更保守的安全邊界",
        "  • 參數選擇影響生命安全決策"
    ]
    
    report_text = "\n".join(report_lines)
    
    # 儲存報告
    try:
        with open('nugget_effect_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        print("✅ 分析報告已儲存: nugget_effect_analysis_report.txt")
    except Exception as e:
        print(f"⚠️ 報告儲存失敗: {e}")
    
    return report_text

def save_and_validate_figure(fig):
    """儲存並驗證圖表"""
    print("\nPhase 9: 儲存與驗證")
    print("=" * 50)
    
    # 儲存圖表
    filename = 'nugget_effect_comparison.png'
    
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

def main_cell9b():
    """Cell 9b 主要執行函數"""
    print("Lab 2 Cell 9b: Nugget Effect — Why Extreme Rain Gets Diluted")
    print("比較不同 Nugget 設定對極端雨量保留的影響")
    print("=" * 60)
    
    try:
        # Phase 1: 前置檢查
        if not check_prerequisites():
            print("❌ 前置檢查失敗，終止執行")
            return False
        
        # Phase 2: 識別極端測站
        station_info = identify_extreme_station()
        if station_info is None:
            print("❌ 極端測站識別失敗")
            return False
        
        # Phase 3: 建立局部網格
        local_grid = create_local_grid(station_info)
        
        # Phase 4: 建立 Kriging 模型
        models = create_kriging_models()
        if models is None:
            print("❌ Kriging 模型建立失敗")
            return False
        
        # Phase 5: 局部網格預測
        predictions = predict_on_local_grid(models, local_grid)
        if predictions is None:
            print("❌ 局部預測失敗")
            return False
        
        # Phase 6: 距離預測分析
        distance_results = predict_at_distances(models, station_info)
        
        # Phase 7: 視覺化
        fig = create_comparison_visualization(station_info, local_grid, predictions, distance_results)
        
        # Phase 8: 分析報告
        report = generate_analysis_report(station_info, models, distance_results)
        
        # Phase 9: 儲存與驗證
        success, filename = save_and_validate_figure(fig)
        
        if success:
            # 顯示圖表
            plt.show()
            
            print("\n" + "=" * 60)
            print("🎉 Cell 9b 實作完成！")
            print("=" * 60)
            print("輸出成果:")
            print(f"  - 圖表檔案: {filename}")
            print("  - 分析報告: nugget_effect_analysis_report.txt")
            print("\nNugget Effect 分析完成")
            print("低 Nugget (1%) 更好保留極端雨量值！")
            
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
# Lab 2 Cell 9b: Nugget Effect — Why Extreme Rain Gets Diluted
import numpy as np
import matplotlib.pyplot as plt
from pykrige.ok import OrdinaryKriging
import warnings
warnings.filterwarnings('ignore')

# 檢查必要變數
required_vars = ['x', 'y', 'z', 'z_log']
missing_vars = [var for var in required_vars if var not in locals() and var not in globals()]

if missing_vars:
    raise NameError(f"缺少必要變數: {missing_vars}. 請先執行 Cell 1-3")

print("✅ 前置檢查通過: 所有必要變數可用")

# Phase 1: 識別極端測站 (Suao)
suao_idx = np.argmax(z)
suao_x, suao_y, suao_z = x[suao_idx], y[suao_idx], z[suao_idx]
print(f"極端雨量測站: {suao_z:.1f} mm/hr @ ({suao_x:.0f}, {suao_y:.0f})")

# Phase 2: 建立局部網格 (20km × 20km)
grid_size = 20000  # 20km
resolution = 100   # 100m
half_size = grid_size // 2
grid_extent = np.linspace(-half_size, half_size, grid_size//resolution + 1)
local_grid_x = suao_x + grid_extent
local_grid_y = suao_y + grid_extent

print(f"局部網格: {grid_size/1000:.0f}km × {grid_size/1000:.0f}km @ {resolution}m 解析度")

# Phase 3: 建立兩種 Kriging 模型
sill_val = float(z_log.var())

# 高 Nugget 模型 (10%)
OK_high = OrdinaryKriging(x, y, z_log, variogram_model='spherical',
                         variogram_parameters={
                             'sill': sill_val,
                             'range': 50000.0,
                             'nugget': sill_val * 0.10
                         })

# 低 Nugget 模型 (1%)
OK_low = OrdinaryKriging(x, y, z_log, variogram_model='spherical',
                        variogram_parameters={
                            'sill': sill_val,
                            'range': 50000.0,
                            'nugget': sill_val * 0.01
                        })

print(f"✅ Kriging 模型建立完成")
print(f"  高 Nugget: {sill_val * 0.10:.4f} (10%)")
print(f"  低 Nugget: {sill_val * 0.01:.4f} (1%)")

# Phase 4: 局部網格預測
print("執行局部網格預測...")

# 高 Nugget 預測
z_high_log, _ = OK_high.execute('grid', local_grid_x, local_grid_y)
z_high = np.expm1(z_high_log)
z_high[z_high < 0] = 0

# 低 Nugget 預測
z_low_log, _ = OK_low.execute('grid', local_grid_x, local_grid_y)
z_low = np.expm1(z_low_log)
z_low[z_low < 0] = 0

print(f"  高 Nugget 範圍: {z_high.min():.1f} - {z_high.max():.1f} mm/hr")
print(f"  低 Nugget 範圍: {z_low.min():.1f} - {z_low.max():.1f} mm/hr")

# Phase 5: 距離預測分析
distances = [0, 500, 1000, 2000]
directions = ['east', 'west', 'north', 'south']

print(f"\\n距離預測結果:")
print(f"{'距離':<6} {'方向':<6} {'高Nugget':<10} {'低Nugget':<10} {'差異':<8} {'保留%':<8}")
print("-" * 60)

for dist in distances:
    for direction in directions:
        # 計算預測點
        if direction == 'east':
            pred_x, pred_y = suao_x + dist, suao_y
        elif direction == 'west':
            pred_x, pred_y = suao_x - dist, suao_y
        elif direction == 'north':
            pred_x, pred_y = suao_x, suao_y + dist
        else:  # south
            pred_x, pred_y = suao_x, suao_y - dist
        
        # 預測
        pred_high_log = OK_high.execute('points', pred_x, pred_y)[0]
        pred_high = max(np.expm1(pred_high_log[0]), 0)
        
        pred_low_log = OK_low.execute('points', pred_x, pred_y)[0]
        pred_low = max(np.expm1(pred_low_log[0]), 0)
        
        # 計算保留百分比
        preservation_low = pred_low / suao_z * 100
        
        print(f"{dist:<6} {direction:<6} {pred_high:<10.1f} {pred_low:<10.1f} "
              f"{pred_low-pred_high:<8.1f} {preservation_low:<8.1f}")

# Phase 6: 並排比較視覺化
fig, axes = plt.subplots(1, 2, figsize=(16, 8))
fig.suptitle('Nugget Effect on Extreme Rainfall Preservation\\n(Suao Station: 130.5 mm/hr)', 
            fontsize=16, fontweight='bold')

# 統一色彩範圍
vmin, vmax = 0, 140

# 左側：高 Nugget
im1 = axes[0].imshow(z_high, extent=[local_grid_x.min(), local_grid_x.max(),
                                   local_grid_y.min(), local_grid_y.max()],
                    origin='lower', cmap='YlOrRd', vmin=vmin, vmax=vmax, aspect='auto')

# 添加距離圓圈和測站標記
for radius in [500, 1000, 2000]:
    circle = plt.Circle((suao_x, suao_y), radius, fill=False, 
                       edgecolor='black', linewidth=1.5, linestyle='--', alpha=0.7)
    axes[0].add_patch(circle)

axes[0].plot(suao_x, suao_y, 'b^', markersize=15, markeredgecolor='white', 
            markeredgewidth=2, label=f'Suao ({suao_z:.1f})')

axes[0].set_title('High Nugget (10%)\\nHeavy Smoothing', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Easting (m)')
axes[0].set_ylabel('Northing (m)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 右側：低 Nugget
im2 = axes[1].imshow(z_low, extent=[local_grid_x.min(), local_grid_x.max(),
                                  local_grid_y.min(), local_grid_y.max()],
                    origin='lower', cmap='YlOrRd', vmin=vmin, vmax=vmax, aspect='auto')

# 添加距離圓圈和測站標記
for radius in [500, 1000, 2000]:
    circle = plt.Circle((suao_x, suao_y), radius, fill=False, 
                       edgecolor='black', linewidth=1.5, linestyle='--', alpha=0.7)
    axes[1].add_patch(circle)

axes[1].plot(suao_x, suao_y, 'b^', markersize=15, markeredgecolor='white', 
            markeredgewidth=2, label=f'Suao ({suao_z:.1f})')

axes[1].set_title('Low Nugget (1%)\\nExtreme Preserved', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Easting (m)')
axes[1].set_ylabel('Northing (m)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# 添加色彩條
plt.colorbar(im1, ax=axes[0], label='Rainfall (mm/hr)')
plt.colorbar(im2, ax=axes[1], label='Rainfall (mm/hr)')

plt.tight_layout()
plt.savefig('nugget_effect_comparison.png', dpi=300, bbox_inches='tight')
print("✅ 圖表已儲存: nugget_effect_comparison.png")

plt.show()

# 結論分析
zero_m_high = OK_high.execute('points', suao_x, suao_y)[0]
zero_m_low = OK_low.execute('points', suao_x, suao_y)[0]
zero_m_high_val = max(np.expm1(zero_m_high[0]), 0)
zero_m_low_val = max(np.expm1(zero_m_low[0]), 0)

print(f"\\n🎯 關鍵結論:")
print(f"在測站位置 (0m):")
print(f"  高 Nugget (10%): {zero_m_high_val:.1f} mm/hr ({zero_m_high_val/suao_z*100:.1f}% 保留)")
print(f"  低 Nugget (1%): {zero_m_low_val:.1f} mm/hr ({zero_m_low_val/suao_z*100:.1f}% 保留)")

if zero_m_low_val > zero_m_high_val:
    print(f"\\n✅ 低 Nugget (1%) 更好保留極端雨量值")
    print(f"✅ 建議極端事件分析使用低 Nugget 設定")
else:
    print(f"\\n⚠️ 需要進一步分析")

print("\\n🚨 對指揮官的意義:")
print("• 低 Nugget 提供更準確的極端降雨預測")
print("• 高 Nugget 可能低估撤離風險")
print("• 參數選擇直接影響生命安全決策")
'''

if __name__ == "__main__":
    # 獨立執行模式（用於測試）
    print("Cell 9b 獨立執行模式")
    print("注意：需要先載入所有必要變數")
    success = main_cell9b()
else:
    print("Cell 9b 模組已載入")
    print("使用 main_cell9b() 函數執行完整 Nugget Effect 分析")

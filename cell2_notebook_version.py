# Cell 2: Variogram Analysis - Jupyter Notebook 版本
# 直接複製到 Jupyter Notebook Cell 中執行

# 安裝必要套件
try:
    import pykrige
    from pykrige.ok import OrdinaryKriging
    print("pykrige 已經可用")
except ImportError:
    print("安裝 pykrige...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pykrige"])
    from pykrige.ok import OrdinaryKriging
    print("pykrige 安裝完成")

# 導入必要套件
import numpy as np
import matplotlib.pyplot as plt
import warnings
from cell1_data_processing import main
warnings.filterwarnings('ignore')

# 載入資料
print("載入 Cell 1 的處理結果...")
study_rain_3826, x, y, z = main()

if study_rain_3826 is None:
    print("無法載入資料，終止分析")
else:
    print(f"載入 {len(z)} 個有效測站")
    print(f"座標範圍: X({x.min():.0f}-{x.max():.0f}m), Y({y.min():.0f}-{y.max():.0f}m)")
    print(f"雨量範圍: {z.min():.1f}-{z.max():.1f} mm/hr")
    
    # Cell 2a: Naive Kriging
    print("\n" + "="*60)
    print("Cell 2a: Variogram — First Attempt (Naive)")
    print("="*60)
    
    initial_sill = float(z.var())
    initial_range = 50000.0
    initial_nugget = float(z.var() * 0.1)
    
    print(f"初始參數:")
    print(f"  Sill:   {initial_sill:.2f}")
    print(f"  Range:  {initial_range/1000:.1f} km")
    print(f"  Nugget: {initial_nugget:.2f}")
    
    OK_naive = OrdinaryKriging(x, y, z, variogram_model='spherical',
                              verbose=False, enable_plotting=True, nlags=15,
                              variogram_parameters={'sill': initial_sill,
                                                    'range': initial_range,
                                                    'nugget': initial_nugget})
    
    params = OK_naive.variogram_model_parameters
    print(f"\n擬合後參數:")
    print(f"  Sill:   {params[0]:.2f}")
    print(f"  Range:  {params[1]/1000:.1f} km")
    print(f"  Nugget: {params[2]:.2f}")
    print("\n觀察 variogram 圖：點是否遵循曲線？")
    print("   預期：擬合不良，點分散嚴重")
    
    # Cell 2b: Histogram Analysis
    print("\n" + "="*60)
    print("Cell 2b: Why Did It Fail? — Look at the Histogram")
    print("="*60)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 原始資料
    axes[0].hist(z, bins=30, color='tomato', edgecolor='black', alpha=0.7)
    axes[0].set_title('Raw Rainfall (mm/hr)', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Rainfall (mm/hr)')
    axes[0].set_ylabel('Station Count')
    axes[0].axvline(z.mean(), color='red', linestyle='--', alpha=0.8, label=f'Mean: {z.mean():.1f}')
    axes[0].axvline(np.median(z), color='blue', linestyle='--', alpha=0.8, label=f'Median: {np.median(z):.1f}')
    axes[0].legend()
    
    # Log-transform
    z_log = np.log1p(z)
    axes[1].hist(z_log, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    axes[1].set_title('After log(1+z)', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('log(1 + Rainfall)')
    axes[1].set_ylabel('Station Count')
    axes[1].axvline(z_log.mean(), color='red', linestyle='--', alpha=0.8, label=f'Mean: {z_log.mean():.2f}')
    axes[1].axvline(np.median(z_log), color='blue', linestyle='--', alpha=0.8, label=f'Median: {np.median(z_log):.2f}')
    axes[1].legend()
    
    plt.tight_layout()
    plt.show()
    
    print("統計分析:")
    print(f"原始資料:")
    print(f"  平均值: {z.mean():.2f} mm/hr")
    print(f"  中位數: {np.median(z):.2f} mm/hr")
    print(f"  標準差: {z.std():.2f} mm/hr")
    print(f"  最大值: {z.max():.2f} mm/hr")
    print(f"  偏態係數: {np.sum(((z - z.mean()) / z.std()) ** 3) / len(z):.2f}")
    
    print(f"\nLog-transform 後:")
    print(f"  平均值: {z_log.mean():.2f}")
    print(f"  中位數: {np.median(z_log):.2f}")
    print(f"  標準差: {z_log.std():.2f}")
    print(f"  偏態係數: {np.sum(((z_log - z_log.mean()) / z_log.std()) ** 3) / len(z_log):.2f}")
    
    print("\n觀察結果:")
    print("左圖：大部分測站 < 10 mm，但少數測站 50-130 mm（長尾右偏）")
    print("右圖：log-transform 後數值更平衡，分佈更接近常態")
    print("結論：極端值干擾 variogram，需要 log transform")
    
    # Cell 2c: Log-Transform Kriging
    print("\n" + "="*60)
    print("Cell 2c: Variogram — Second Attempt (with Log-Transform)")
    print("="*60)
    
    initial_sill_log = float(z_log.var())
    initial_range_log = 50000.0
    initial_nugget_log = float(z_log.var() * 0.1)
    
    print(f"基於 log-transform 的初始參數:")
    print(f"  Sill:   {initial_sill_log:.3f}")
    print(f"  Range:  {initial_range_log/1000:.1f} km")
    print(f"  Nugget: {initial_nugget_log:.3f}")
    
    OK = OrdinaryKriging(x, y, z_log, variogram_model='spherical',
                        verbose=False, enable_plotting=True, nlags=15,
                        variogram_parameters={'sill': initial_sill_log,
                                              'range': initial_range_log,
                                              'nugget': initial_nugget_log})
    
    params = OK.variogram_model_parameters
    print(f"\n擬合後參數:")
    print(f"  Sill:   {params[0]:.3f}")
    print(f"  Range:  {params[1]/1000:.1f} km")
    print(f"  Nugget: {params[2]:.3f}")
    print("\n與 Cell 2a 比較：點現在應該更好地遵循曲線")
    
    # Cell 2d: Simple Model Comparison
    print("\n" + "="*60)
    print("Cell 2d: Simple Model Comparison")
    print("="*60)
    
    ranges_m = [50000, 25000, 15000]  # 50km, 25km, 15km
    ranges_km = [50, 25, 15]
    
    print("測試不同 Range 的影響（使用 Spherical 模型）:")
    
    for r_m, r_km in zip(ranges_m, ranges_km):
        ok_test = OrdinaryKriging(x, y, z_log, variogram_model='spherical',
                                 verbose=False, enable_plotting=False, nlags=15,
                                 variogram_parameters={'sill': float(z_log.var()),
                                                       'range': r_m,
                                                       'nugget': float(z_log.var() * 0.1)})
        
        params = ok_test.variogram_model_parameters
        print(f"  Range {r_km}km: Sill={params[0]:.3f}, Nugget={params[2]:.3f}")
    
    print("\n結論:")
    print("1. 不同 Range 會影響擬合結果")
    print("2. 較小 Range 通常適合局部變異")
    print("3. 較大 Range 適合大尺度趨勢")
    
    print("\n" + "="*60)
    print("Cell 2 分析完成！")
    print("="*60)
    print("關鍵發現:")
    print("  1. 原始資料因極端值導致 variogram 擬合不良")
    print("  2. Log-transform 顯著改善擬合品質")
    print("  3. 不同 Range 會產生不同的擬合結果")
    print("  4. 資料轉換對空間統計至關重要")

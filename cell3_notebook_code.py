# Cell 3: Define the Interpolation Grid & Run Kriging (Slide 8)

import time

# YOUR CODE HERE:
# 1. Calculate grid extent from x, y arrays (with 5km buffer)
# 2. Create grid_x and grid_y using np.arange with 1000m step
# 3. Execute Kriging in log-space: z_kriging_log, ss_kriging_log = OK.execute('grid', grid_x, grid_y)
# 4. Back-transform: z_kriging = np.expm1(z_kriging_log)

# 設置網格參數
buffer_m = 5000
resolution = 1000  # meters — use 500 for finer resolution (slower)

# 計算網格範圍（加入緩衝區）
x_min = x.min() - buffer_m
x_max = x.max() + buffer_m
y_min = y.min() - buffer_m
y_max = y.max() + buffer_m

# 建立網格座標
grid_x = np.arange(x_min, x_max, resolution)
grid_y = np.arange(y_min, y_max, resolution)

print(f"Grid: {len(grid_x)}×{len(grid_y)} = {len(grid_x)*len(grid_y):,} points @ {resolution}m")

# 執行 Kriging 預測（在對數空間）
t0 = time.time()
z_kriging_log, ss_kriging_log = OK.execute('grid', grid_x, grid_y)
print(f"* Kriging (log-space) done in {time.time()-t0:.1f}s")

# 轉換回原始雨量單位 (mm/hr)
z_kriging = np.expm1(z_kriging_log)
z_kriging[z_kriging < 0] = 0  # 處理負值，設為 0
ss_kriging = ss_kriging_log  # 保留對數空間變異數用於不確定性分析

print(f"  z range (mm/hr): {np.nanmin(z_kriging):.1f} - {np.nanmax(z_kriging):.1f}")
print(f"  Average rainfall: {np.nanmean(z_kriging):.1f} mm/hr")
print(f"  Grid coverage: {(x_max-x_min)/1000:.1f} × {(y_max-y_min)/1000:.1f} km")

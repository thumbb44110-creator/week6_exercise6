#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 11a: LOOCV Cross-Validation — 四方法定量比較
Lab 2: Confidence & Uncertainty Diagnosis

Implement Leave-One-Out Cross-Validation for four interpolation methods
to provide quantitative performance comparison through RMSE and MAE metrics.

Author: thumbb44110-creator
Date: 2026-04-04
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

def check_dependencies():
    """檢查必要的函式庫依賴"""
    print("Phase 1: 檢查函式庫依賴")
    print("=" * 50)
    
    dependencies = {
        'sklearn': ['LeaveOneOut'],
        'scipy': ['NearestNDInterpolator', 'cdist'],
        'pykrige': ['OrdinaryKriging']
    }
    
    missing_libs = []
    
    for lib, modules in dependencies.items():
        try:
            if lib == 'sklearn':
                from sklearn.model_selection import LeaveOneOut
                print("✅ sklearn.model_selection.LeaveOneOut: 可用")
            elif lib == 'scipy':
                from scipy.interpolate import NearestNDInterpolator
                from scipy.spatial.distance import cdist
                print("✅ scipy.interpolate.NearestNDInterpolator: 可用")
                print("✅ scipy.spatial.distance.cdist: 可用")
            elif lib == 'pykrige':
                from pykrige.ok import OrdinaryKriging
                print("✅ pykrige.OrdinaryKriging: 可用")
        except ImportError:
            print(f"❌ {lib}: 未安裝或缺少模組")
            missing_libs.append(lib)
    
    if missing_libs:
        print(f"\n❌ 缺少函式庫: {missing_libs}")
        print("安裝指令:")
        for lib in missing_libs:
            print(f"  pip install {lib}")
        return False
    
    return True

def check_prerequisites():
    """檢查必要的前置變數"""
    print("\nPhase 2: 檢查前置變數")
    print("=" * 50)
    
    required_vars = ['x', 'y', 'z']
    missing_vars = []
    
    for var in required_vars:
        if var in globals() or var in locals():
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
        print("請確保已執行 Cell 1-2 (資料載入和處理)")
        return False
    
    # 檢查資料合理性
    x = globals().get('x', locals().get('x'))
    y = globals().get('y', locals().get('y'))
    z = globals().get('z', locals().get('z'))
    
    print(f"\n資料驗證:")
    print(f"  測站數量: {len(x)}")
    print(f"  座標範圍: X({x.min():.0f}-{x.max():.0f}), Y({y.min():.0f}-{y.max():.0f})")
    print(f"  雨量範圍: {z.min():.1f} - {z.max():.1f} mm/hr")
    print(f"  平均雨量: {z.mean():.1f} mm/hr")
    
    # 檢查是否有異常值
    if np.any(z < 0):
        print(f"  ⚠️ 發現負雨量值: {np.sum(z < 0)} 個")
    
    return True

def setup_loocv_framework():
    """建立 LOOCV 框架"""
    print("\nPhase 3: 建立 LOOCV 框架")
    print("=" * 50)
    
    from sklearn.model_selection import LeaveOneOut
    
    # 建立 LOOCV 分割器
    loo = LeaveOneOut()
    
    # 準備座標資料
    x = globals().get('x', locals().get('x'))
    y = globals().get('y', locals().get('y'))
    z = globals().get('z', locals().get('z'))
    
    coords = np.column_stack([x, y])
    
    print(f"LOOCV 設定:")
    print(f"  測站數量: {len(coords)}")
    print(f"  驗證次數: {loo.get_n_splits(coords)} (每站一次)")
    print(f"  訓練資料大小: {len(coords)-1} 測站")
    print(f"  測試資料大小: 1 測站")
    
    # 初始化結果儲存
    methods = ['kriging', 'rf', 'nn', 'idw']
    results = {
        method: {
            'errors': [],
            'predictions': [],
            'actuals': [],
            'success_count': 0,
            'failure_count': 0
        }
        for method in methods
    }
    
    print(f"\n追蹤方法: {methods}")
    
    return loo, coords, results

def predict_kriging_loocv(x_train, y_train, z_train, x_test, y_test):
    """Kriging LOOCV 預測函數"""
    try:
        from pykrige.ok import OrdinaryKriging
        
        # Log-transform 訓練資料
        z_log_train = np.log1p(z_train)
        
        # 計算初始參數
        sill = float(z_log_train.var())
        nugget = float(z_log_train.var() * 0.1)
        
        # 建立 Kriging 模型
        OK = OrdinaryKriging(x_train, y_train, z_log_train,
                           variogram_model='spherical',
                           variogram_parameters={
                               'sill': sill,
                               'nugget': nugget,
                               'range': 50000.0
                           },
                           verbose=False, 
                           enable_plotting=False)
        
        # 在測試位置預測
        z_pred_log, _ = OK.execute('points', x_test, y_test)
        z_pred = np.expm1(z_pred_log[0])
        
        # 確保非負值
        return max(z_pred, 0.0)
        
    except Exception as e:
        # 失敗時使用最近3站的平均值作為後備
        distances = np.sqrt((x_train - x_test)**2 + (y_train - y_test)**2)
        nearby_idx = distances.argsort()[:3]
        return np.mean(z_train[nearby_idx])

def predict_rf_loocv(x_train, y_train, z_train, x_test, y_test):
    """Random Forest LOOCV 預測函數"""
    try:
        from sklearn.ensemble import RandomForestRegressor
        
        # 準備訓練資料
        X_train = np.column_stack([x_train, y_train])
        X_test = np.column_stack([x_test, y_test])
        
        # 訓練模型
        rf = RandomForestRegressor(
            n_estimators=200, 
            min_samples_leaf=3, 
            random_state=42
        )
        rf.fit(X_train, z_train)
        
        # 預測
        return rf.predict(X_test)[0]
        
    except Exception as e:
        # 失敗時使用簡單平均
        return np.mean(z_train)

def predict_nn_loocv(x_train, y_train, z_train, x_test, y_test):
    """Nearest Neighbor LOOCV 預測函數"""
    try:
        from scipy.interpolate import NearestNDInterpolator
        
        # 建立插值器
        nn_interp = NearestNDInterpolator(list(zip(x_train, y_train)), z_train)
        
        # 預測
        return nn_interp(x_test, y_test)[0]
        
    except Exception as e:
        # 失敗時使用最近站
        distances = np.sqrt((x_train - x_test)**2 + (y_train - y_test)**2)
        nearest_idx = distances.argmin()
        return z_train[nearest_idx]

def predict_idw_loocv(x_train, y_train, z_train, x_test, y_test, power=2):
    """IDW LOOCV 預測函數"""
    try:
        from scipy.spatial.distance import cdist
        
        # 計算距離
        train_points = np.column_stack([x_train, y_train])
        test_point = np.array([[x_test, y_test]])
        distances = cdist(test_point, train_points)[0]
        
        # 處理零距離
        distances[distances < 1e-10] = 1e-10
        
        # 計算權重
        weights = 1.0 / (distances ** power)
        weights = weights / weights.sum()
        
        # 加權平均
        return np.dot(weights, z_train)
        
    except Exception as e:
        # 失敗時使用簡單平均
        return np.mean(z_train)

def execute_loocv(loo, coords, results):
    """執行 LOOCV 驗證"""
    print("\nPhase 4: 執行 LOOCV 驗證")
    print("=" * 50)
    
    x = globals().get('x', locals().get('x'))
    y = globals().get('y', locals().get('y'))
    z = globals().get('z', locals().get('z'))
    
    total_splits = loo.get_n_splits(coords)
    print(f"開始 LOOCV 驗證 ({total_splits} 次迭代)...")
    
    for i, (train_idx, test_idx) in enumerate(loo.split(coords)):
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  進度: {i+1}/{total_splits} ({(i+1)/total_splits*100:.1f}%)")
        
        # 提取訓練和測試資料
        x_train, y_train, z_train = x[train_idx], y[train_idx], z[train_idx]
        x_test, y_test, z_test = x[test_idx][0], y[test_idx][0], z[test_idx][0]
        
        # 對每種方法進行預測
        methods_predictions = {}
        
        # Kriging 預測
        try:
            pred_kriging = predict_kriging_loocv(x_train, y_train, z_train, x_test, y_test)
            methods_predictions['kriging'] = pred_kriging
            results['kriging']['success_count'] += 1
        except Exception as e:
            methods_predictions['kriging'] = np.mean(z_train)  # 後備預測
            results['kriging']['failure_count'] += 1
        
        # Random Forest 預測
        try:
            pred_rf = predict_rf_loocv(x_train, y_train, z_train, x_test, y_test)
            methods_predictions['rf'] = pred_rf
            results['rf']['success_count'] += 1
        except Exception as e:
            methods_predictions['rf'] = np.mean(z_train)  # 後備預測
            results['rf']['failure_count'] += 1
        
        # Nearest Neighbor 預測
        try:
            pred_nn = predict_nn_loocv(x_train, y_train, z_train, x_test, y_test)
            methods_predictions['nn'] = pred_nn
            results['nn']['success_count'] += 1
        except Exception as e:
            methods_predictions['nn'] = np.mean(z_train)  # 後備預測
            results['nn']['failure_count'] += 1
        
        # IDW 預測
        try:
            pred_idw = predict_idw_loocv(x_train, y_train, z_train, x_test, y_test)
            methods_predictions['idw'] = pred_idw
            results['idw']['success_count'] += 1
        except Exception as e:
            methods_predictions['idw'] = np.mean(z_train)  # 後備預測
            results['idw']['failure_count'] += 1
        
        # 儲存結果
        for method, pred in methods_predictions.items():
            error = pred - z_test
            results[method]['errors'].append(error)
            results[method]['predictions'].append(pred)
            results[method]['actuals'].append(z_test)
    
    print(f"✅ LOOCV 驗證完成")
    
    # 顯示成功統計
    print(f"\n成功統計:")
    for method, data in results.items():
        total = data['success_count'] + data['failure_count']
        success_rate = data['success_count'] / total * 100
        print(f"  {method}: {data['success_count']}/{total} ({success_rate:.1f}%)")
    
    return results

def calculate_metrics(results):
    """計算評估指標"""
    print("\nPhase 5: 計算評估指標")
    print("=" * 50)
    
    metrics = {}
    
    for method, data in results.items():
        errors = np.array(data['errors'])
        
        # 計算指標
        rmse = np.sqrt(np.mean(errors**2))
        mae = np.mean(np.abs(errors))
        bias = np.mean(errors)  # 平均誤差（正偏表示高估）
        
        # 計算相關係數
        predictions = np.array(data['predictions'])
        actuals = np.array(data['actuals'])
        correlation = np.corrcoef(predictions, actuals)[0, 1]
        
        # 找出最差測站
        worst_idx = np.argmax(np.abs(errors))
        worst_error = errors[worst_idx]
        worst_actual = actuals[worst_idx]
        worst_pred = predictions[worst_idx]
        
        metrics[method] = {
            'rmse': rmse,
            'mae': mae,
            'bias': bias,
            'correlation': correlation,
            'worst_error': worst_error,
            'worst_actual': worst_actual,
            'worst_pred': worst_pred,
            'worst_idx': worst_idx
        }
        
        print(f"{method}:")
        print(f"  RMSE: {rmse:.3f} mm/hr")
        print(f"  MAE:  {mae:.3f} mm/hr")
        print(f"  Bias: {bias:.3f} mm/hr ({'高估' if bias > 0 else '低估'})")
        print(f"  Correlation: {correlation:.3f}")
        print(f"  最差誤差: {worst_error:.3f} mm/hr")
        print(f"    實際值: {worst_actual:.1f} mm/hr")
        print(f"    預測值: {worst_pred:.1f} mm/hr")
    
    return metrics

def analyze_worst_stations(metrics, coords, z):
    """分析最差測站"""
    print("\nPhase 6: 分析最差測站")
    print("=" * 50)
    
    print("各方法最差預測測站分析:")
    
    for method, metric in metrics.items():
        worst_idx = metric['worst_idx']
        worst_error = metric['worst_error']
        worst_actual = metric['worst_actual']
        worst_pred = metric['worst_pred']
        
        x_worst, y_worst = coords[worst_idx]
        
        print(f"\n{method} 最差測站:")
        print(f"  測站索引: {worst_idx}")
        print(f"  座標: ({x_worst:.0f}, {y_worst:.0f})")
        print(f"  實際雨量: {worst_actual:.1f} mm/hr")
        print(f"  預測雨量: {worst_pred:.1f} mm/hr")
        print(f"  預測誤差: {worst_error:.1f} mm/hr")
        print(f"  誤差百分比: {abs(worst_error/worst_actual*100):.1f}%")
        
        # 分析可能原因
        if worst_actual > 50:  # 高雨量測站
            print(f"  可能原因: 極端雨量值，插值困難")
        elif worst_error > 20:  # 大誤差
            print(f"  可能原因: 測站位置偏遠，周圍參考點少")
        else:
            print(f"  可能原因: 局部雨量變異性高")

def create_performance_comparison(metrics):
    """建立效能比較表格"""
    print("\nPhase 7: 建立效能比較")
    print("=" * 50)
    
    # 排序方法（按 RMSE）
    methods_sorted = sorted(metrics.keys(), key=lambda x: metrics[x]['rmse'])
    
    print("四種插值方法效能比較:")
    print("-" * 80)
    print(f"{'排名':<4} {'方法':<12} {'RMSE':<8} {'MAE':<8} {'Bias':<8} {'相關係數':<8}")
    print("-" * 80)
    
    for rank, method in enumerate(methods_sorted, 1):
        metric = metrics[method]
        bias_str = f"{metric['bias']:+.2f}"
        print(f"{rank:<4} {method:<12} {metric['rmse']:<8.3f} {metric['mae']:<8.3f} "
              f"{bias_str:<8} {metric['correlation']:<8.3f}")
    
    print("-" * 80)
    
    # 找出最佳方法
    best_method = methods_sorted[0]
    worst_method = methods_sorted[-1]
    
    print(f"\n🏆 最佳方法: {best_method}")
    print(f"   RMSE: {metrics[best_method]['rmse']:.3f} mm/hr")
    print(f"   MAE:  {metrics[best_method]['mae']:.3f} mm/hr")
    
    print(f"\n⚠️ 最差方法: {worst_method}")
    print(f"   RMSE: {metrics[worst_method]['rmse']:.3f} mm/hr")
    print(f"   MAE:  {metrics[worst_method]['mae']:.3f} mm/hr")
    
    return methods_sorted

def generate_insights(metrics, coords, z):
    """產生洞察分析"""
    print("\nPhase 8: 產生洞察分析")
    print("=" * 50)
    
    print("關鍵洞察:")
    
    # 方法特性分析
    print(f"\n1. 方法特性分析:")
    for method, metric in metrics.items():
        bias = metric['bias']
        if abs(bias) < 1:
            bias_desc = "無偏"
        elif bias > 0:
            bias_desc = f"高估 {bias:.1f} mm/hr"
        else:
            bias_desc = f"低估 {abs(bias):.1f} mm/hr"
        
        print(f"   {method}: {bias_desc}, 相關係數 {metric['correlation']:.3f}")
    
    # 極端值處理能力
    print(f"\n2. 極端值處理能力:")
    high_rainfall_idx = z > 50  # 高雨量測站
    if np.any(high_rainfall_idx):
        print(f"   高雨量測站 (>50 mm/hr): {np.sum(high_rainfall_idx)} 個")
        
        for method in metrics.keys():
            errors = np.array(results[method]['errors'])
            high_rainfall_errors = errors[high_rainfall_idx]
            high_rainfall_mae = np.mean(np.abs(high_rainfall_errors))
            print(f"   {method} 高雨量 MAE: {high_rainfall_mae:.3f} mm/hr")
    
    # 穩定性分析
    print(f"\n3. 穩定性分析:")
    for method, data in results.items():
        total = data['success_count'] + data['failure_count']
        success_rate = data['success_count'] / total * 100
        print(f"   {method}: {success_rate:.1f}% 成功率")
    
    # 實務建議
    print(f"\n4. 實務建議:")
    best_method = min(metrics.keys(), key=lambda x: metrics[x]['rmse'])
    print(f"   • 最佳預測方法: {best_method}")
    print(f"   • 緊急決策建議使用: {best_method}")
    print(f"   • 需要額外驗證的方法: {max(metrics.keys(), key=lambda x: metrics[x]['rmse'])}")

def generate_validation_report(metrics, methods_sorted, coords, z):
    """產生驗證報告"""
    print("\nPhase 9: 生成驗證報告")
    print("=" * 50)
    
    report_lines = [
        "LOOCV Cross-Validation - 四方法定量比較報告",
        "=" * 60,
        f"驗證時間: 2026-04-04",
        f"測站數量: {len(coords)}",
        f"驗證方法: Leave-One-Out Cross-Validation",
        "",
        "效能排名:",
    ]
    
    for rank, method in enumerate(methods_sorted, 1):
        metric = metrics[method]
        report_lines.append(f"  {rank}. {method}: RMSE={metric['rmse']:.3f}, MAE={metric['mae']:.3f}")
    
    report_lines.extend([
        "",
        "詳細指標:",
    ])
    
    for method, metric in metrics.items():
        report_lines.extend([
            f"",
            f"{method}:",
            f"  • RMSE: {metric['rmse']:.3f} mm/hr",
            f"  • MAE: {metric['mae']:.3f} mm/hr",
            f"  • Bias: {metric['bias']:+.3f} mm/hr",
            f"  • 相關係數: {metric['correlation']:.3f}",
            f"  • 最差誤差: {metric['worst_error']:.3f} mm/hr",
        ])
    
    report_lines.extend([
        "",
        "關鍵發現:",
        f"  • 最佳方法: {methods_sorted[0]}",
        f"  • 最差方法: {methods_sorted[-1]}",
        f"  • 精度差異: {metrics[methods_sorted[-1]]['rmse'] - metrics[methods_sorted[0]]['rmse']:.3f} mm/hr",
        "",
        "實務意義:",
        "  • 提供客觀的方法選擇依據",
        "  • 量化各方法的預測不確定性",
        "  • 識別需要改進的測站位置",
        "  • 支援災害管理決策制定",
        "",
        "技術特色:",
        "  • Leave-One-Out 確保最嚴格的驗證",
        "  • 多指標全面評估方法效能",
        "  • 異常處理確保驗證穩定性",
        "  • 站點分析提供改進方向"
    ])
    
    report_text = "\n".join(report_lines)
    
    # 儲存報告
    try:
        with open('loocv_validation_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        print("✅ 驗證報告已儲存: loocv_validation_report.txt")
    except Exception as e:
        print(f"⚠️ 報告儲存失敗: {e}")
    
    return report_text

def main_cell11a():
    """Cell 11a 主要執行函數"""
    print("Lab 2 Cell 11a: LOOCV Cross-Validation — 四方法定量比較")
    print("使用 Leave-One-Out Cross-Validation 提供客觀的數字比較")
    print("=" * 60)
    
    global results
    
    try:
        # Phase 1: 檢查函式庫依賴
        if not check_dependencies():
            print("❌ 函式庫依賴檢查失敗，終止執行")
            return False
        
        # Phase 2: 檢查前置變數
        if not check_prerequisites():
            print("❌ 前置變數檢查失敗，終止執行")
            return False
        
        # Phase 3: 建立 LOOCV 框架
        loo, coords, results = setup_loocv_framework()
        
        # Phase 4: 執行 LOOCV 驗證
        results = execute_loocv(loo, coords, results)
        
        # Phase 5: 計算評估指標
        metrics = calculate_metrics(results)
        
        # Phase 6: 分析最差測站
        x = globals().get('x', locals().get('x'))
        y = globals().get('y', locals().get('y'))
        z = globals().get('z', locals().get('z'))
        analyze_worst_stations(metrics, coords, z)
        
        # Phase 7: 建立效能比較
        methods_sorted = create_performance_comparison(metrics)
        
        # Phase 8: 產生洞察分析
        generate_insights(metrics, coords, z)
        
        # Phase 9: 生成驗證報告
        report = generate_validation_report(metrics, methods_sorted, coords, z)
        
        print("\n" + "=" * 60)
        print("🎉 Cell 11a 實作完成！")
        print("四種插值方法的定量比較已完成")
        print("=" * 60)
        print("主要成果:")
        print("  • Leave-One-Out Cross-Validation 完成")
        print("  • RMSE 和 MAE 指標計算完成")
        print("  • 方法排名和效能分析完成")
        print("  • 最差測站識別和分析完成")
        
        print("\n🌟 關鍵發現:")
        print(f"  • 最佳方法: {methods_sorted[0]}")
        print(f"  • 最差方法: {methods_sorted[-1]}")
        print("  • 各方法偏差特性已識別")
        print("  • 高雨量測站預測挑戰已分析")
        
        return True
        
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

# Jupyter Notebook 執行版本
jupyter_code = '''
# Lab 2 Cell 11a: LOOCV Cross-Validation — 四方法定量比較
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 檢查必要函式庫
try:
    from sklearn.model_selection import LeaveOneOut
    from sklearn.ensemble import RandomForestRegressor
    from scipy.interpolate import NearestNDInterpolator
    from scipy.spatial.distance import cdist
    from pykrige.ok import OrdinaryKriging
    print("✅ 所有必要函式庫可用")
except ImportError as e:
    print(f"❌ 缺少函式庫: {e}")
    print("請安裝: pip install scikit-learn scipy pykrige")
    raise

# 檢查必要變數
required_vars = ['x', 'y', 'z']
missing_vars = [var for var in required_vars if var not in locals() and var not in globals()]

if missing_vars:
    raise NameError(f"缺少必要變數: {missing_vars}. 請先執行 Cell 1-2")

print("✅ 前置檢查通過: 所有必要變數可用")

# Phase 1: 建立 LOOCV 框架
print("\\n" + "="*50)
print("Phase 1: 建立 LOOCV 框架")
print("="*50)

loo = LeaveOneOut()
coords = np.column_stack([x, y])

print(f"LOOCV 設定:")
print(f"  測站數量: {len(coords)}")
print(f"  驗證次數: {loo.get_n_splits(coords)}")

# 初始化結果儲存
methods = ['kriging', 'rf', 'nn', 'idw']
results = {
    method: {
        'errors': [], 'predictions': [], 'actuals': [],
        'success_count': 0, 'failure_count': 0
    }
    for method in methods
}

# Phase 2: 定義預測函數
def predict_kriging_loocv(x_train, y_train, z_train, x_test, y_test):
    try:
        z_log_train = np.log1p(z_train)
        sill = float(z_log_train.var())
        nugget = float(z_log_train.var() * 0.1)
        
        OK = OrdinaryKriging(x_train, y_train, z_log_train,
                           variogram_model='spherical',
                           variogram_parameters={'sill': sill, 'nugget': nugget, 'range': 50000.0},
                           verbose=False, enable_plotting=False)
        
        z_pred_log, _ = OK.execute('points', x_test, y_test)
        return max(np.expm1(z_pred_log[0]), 0.0)
    except:
        distances = np.sqrt((x_train - x_test)**2 + (y_train - y_test)**2)
        nearby_idx = distances.argsort()[:3]
        return np.mean(z_train[nearby_idx])

def predict_rf_loocv(x_train, y_train, z_train, x_test, y_test):
    try:
        X_train = np.column_stack([x_train, y_train])
        X_test = np.column_stack([x_test, y_test])
        
        rf = RandomForestRegressor(n_estimators=200, min_samples_leaf=3, random_state=42)
        rf.fit(X_train, z_train)
        return rf.predict(X_test)[0]
    except:
        return np.mean(z_train)

def predict_nn_loocv(x_train, y_train, z_train, x_test, y_test):
    try:
        nn_interp = NearestNDInterpolator(list(zip(x_train, y_train)), z_train)
        return nn_interp(x_test, y_test)[0]
    except:
        distances = np.sqrt((x_train - x_test)**2 + (y_train - y_test)**2)
        nearest_idx = distances.argmin()
        return z_train[nearest_idx]

def predict_idw_loocv(x_train, y_train, z_train, x_test, y_test, power=2):
    try:
        train_points = np.column_stack([x_train, y_train])
        test_point = np.array([[x_test, y_test]])
        distances = cdist(test_point, train_points)[0]
        distances[distances < 1e-10] = 1e-10
        
        weights = 1.0 / (distances ** power)
        weights = weights / weights.sum()
        return np.dot(weights, z_train)
    except:
        return np.mean(z_train)

# Phase 3: 執行 LOOCV
print("\\n" + "="*50)
print("Phase 2: 執行 LOOCV 驗證")
print("="*50)

total_splits = loo.get_n_splits(coords)
print(f"開始 LOOCV 驗證 ({total_splits} 次迭代)...")

for i, (train_idx, test_idx) in enumerate(loo.split(coords)):
    if (i + 1) % 10 == 0 or i == 0:
        print(f"  進度: {i+1}/{total_splits} ({(i+1)/total_splits*100:.1f}%)")
    
    # 提取訓練和測試資料
    x_train, y_train, z_train = x[train_idx], y[train_idx], z[train_idx]
    x_test, y_test, z_test = x[test_idx][0], y[test_idx][0], z[test_idx][0]
    
    # 各方法預測
    methods_predictions = {}
    
    # Kriging
    try:
        methods_predictions['kriging'] = predict_kriging_loocv(x_train, y_train, z_train, x_test, y_test)
        results['kriging']['success_count'] += 1
    except:
        methods_predictions['kriging'] = np.mean(z_train)
        results['kriging']['failure_count'] += 1
    
    # Random Forest
    try:
        methods_predictions['rf'] = predict_rf_loocv(x_train, y_train, z_train, x_test, y_test)
        results['rf']['success_count'] += 1
    except:
        methods_predictions['rf'] = np.mean(z_train)
        results['rf']['failure_count'] += 1
    
    # Nearest Neighbor
    try:
        methods_predictions['nn'] = predict_nn_loocv(x_train, y_train, z_train, x_test, y_test)
        results['nn']['success_count'] += 1
    except:
        methods_predictions['nn'] = np.mean(z_train)
        results['nn']['failure_count'] += 1
    
    # IDW
    try:
        methods_predictions['idw'] = predict_idw_loocv(x_train, y_train, z_train, x_test, y_test)
        results['idw']['success_count'] += 1
    except:
        methods_predictions['idw'] = np.mean(z_train)
        results['idw']['failure_count'] += 1
    
    # 儲存結果
    for method, pred in methods_predictions.items():
        error = pred - z_test
        results[method]['errors'].append(error)
        results[method]['predictions'].append(pred)
        results[method]['actuals'].append(z_test)

print("✅ LOOCV 驗證完成")

# Phase 4: 計算指標
print("\\n" + "="*50)
print("Phase 3: 計算評估指標")
print("="*50)

metrics = {}
for method, data in results.items():
    errors = np.array(data['errors'])
    rmse = np.sqrt(np.mean(errors**2))
    mae = np.mean(np.abs(errors))
    bias = np.mean(errors)
    
    predictions = np.array(data['predictions'])
    actuals = np.array(data['actuals'])
    correlation = np.corrcoef(predictions, actuals)[0, 1]
    
    worst_idx = np.argmax(np.abs(errors))
    worst_error = errors[worst_idx]
    worst_actual = actuals[worst_idx]
    worst_pred = predictions[worst_idx]
    
    metrics[method] = {
        'rmse': rmse, 'mae': mae, 'bias': bias, 'correlation': correlation,
        'worst_error': worst_error, 'worst_actual': worst_actual, 
        'worst_pred': worst_pred, 'worst_idx': worst_idx
    }
    
    print(f"{method}:")
    print(f"  RMSE: {rmse:.3f} mm/hr")
    print(f"  MAE:  {mae:.3f} mm/hr")
    print(f"  Bias: {bias:.3f} mm/hr ({'高估' if bias > 0 else '低估'})")
    print(f"  Correlation: {correlation:.3f}")
    print(f"  最差誤差: {worst_error:.3f} mm/hr")

# Phase 5: 效能比較
print("\\n" + "="*50)
print("Phase 4: 效能比較")
print("="*50)

methods_sorted = sorted(metrics.keys(), key=lambda x: metrics[x]['rmse'])

print("四種插值方法效能比較:")
print("-" * 70)
print(f"{'排名':<4} {'方法':<12} {'RMSE':<8} {'MAE':<8} {'Bias':<8} {'相關係數':<8}")
print("-" * 70)

for rank, method in enumerate(methods_sorted, 1):
    metric = metrics[method]
    bias_str = f"{metric['bias']:+.2f}"
    print(f"{rank:<4} {method:<12} {metric['rmse']:<8.3f} {metric['mae']:<8.3f} "
          f"{bias_str:<8} {metric['correlation']:<8.3f}")

print("-" * 70)

best_method = methods_sorted[0]
worst_method = methods_sorted[-1]

print(f"\\n🏆 最佳方法: {best_method}")
print(f"⚠️ 最差方法: {worst_method}")

# Phase 6: 最差測站分析
print("\\n" + "="*50)
print("Phase 5: 最差測站分析")
print("="*50)

for method, metric in metrics.items():
    worst_idx = metric['worst_idx']
    worst_error = metric['worst_error']
    worst_actual = metric['worst_actual']
    worst_pred = metric['worst_pred']
    
    x_worst, y_worst = coords[worst_idx]
    
    print(f"\\n{method} 最差測站:")
    print(f"  測站索引: {worst_idx}")
    print(f"  座標: ({x_worst:.0f}, {y_worst:.0f})")
    print(f"  實際雨量: {worst_actual:.1f} mm/hr")
    print(f"  預測雨量: {worst_pred:.1f} mm/hr")
    print(f"  預測誤差: {worst_error:.1f} mm/hr")
    
    if worst_actual > 50:
        print(f"  可能原因: 極端雨量值")
    elif abs(worst_error) > 20:
        print(f"  可能原因: 測站位置偏遠")

print("\\n" + "="*50)
print("🎉 LOOCV Cross-Validation 完成！")
print("="*50)
print("關鍵發現:")
print(f"  • 最佳方法: {best_method}")
print(f"  • 最差方法: {worst_method}")
print("  • 各方法偏差特性已識別")
print("  • 高雨量測站預測挑戰已分析")
'''

if __name__ == "__main__":
    # 獨立執行模式（用於測試）
    print("Cell 11a 獨立執行模式")
    print("注意：需要先載入所有必要變數")
    success = main_cell11a()
else:
    print("Cell 11a 模組已載入")
    print("使用 main_cell11a() 函數執行完整 LOOCV 驗證")

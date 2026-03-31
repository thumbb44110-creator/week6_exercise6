#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell 4: Random Forest Prediction - Simplified Version
Week 6 Spatial Prediction Shootout
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
import time
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load required data from previous cells"""
    try:
        # Load Cell 1 data
        from cell1_data_processing import main
        study_rain_3826, x, y, z = main()
        print("Loaded Cell 1 data successfully")
        
        # Create grid (same as Cell 3)
        buffer_m = 5000
        resolution = 1000
        x_min = x.min() - buffer_m
        x_max = x.max() + buffer_m
        y_min = y.min() - buffer_m
        y_max = y.max() + buffer_m
        grid_x = np.arange(x_min, x_max, resolution)
        grid_y = np.arange(y_min, y_max, resolution)
        
        print(f"Created grid: {len(grid_x)}x{len(grid_y)} points")
        return study_rain_3826, x, y, z, grid_x, grid_y
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None, None, None, None

def main():
    """Main execution function"""
    print("="*60)
    print("Cell 4: Random Forest Prediction")
    print("="*60)
    
    # Load data
    study_rain_3826, x, y, z, grid_x, grid_y = load_data()
    
    if any(v is None for v in [x, y, z, grid_x, grid_y]):
        print("Cannot load required data")
        return None
    
    print(f"Data loaded: {len(z)} stations")
    print(f"Coordinate range: X({x.min():.0f}-{x.max():.0f}), Y({y.min():.0f}-{y.max():.0f})")
    print(f"Rainfall range: {z.min():.1f} - {z.max():.1f} mm/hr")
    
    # Phase 1: Prepare training data
    print("\n=== Phase 1: Data Preparation ===")
    X_train = np.column_stack([x, y])
    y_train = z
    print(f"Training data: X_train{X_train.shape}, y_train{y_train.shape}")
    
    # Phase 2: Train Random Forest
    print("\n=== Phase 2: Model Training ===")
    rf = RandomForestRegressor(n_estimators=200, min_samples_leaf=3, random_state=42)
    
    start_time = time.time()
    rf.fit(X_train, y_train)
    training_time = time.time() - start_time
    
    train_r2 = rf.score(X_train, y_train)
    print(f"Training time: {training_time:.2f} seconds")
    print(f"Training R^2 score: {train_r2:.4f}")
    
    # Feature importance
    feature_names = ['Easting', 'Northing']
    importances = rf.feature_importances_
    print("Feature importance:")
    for name, importance in zip(feature_names, importances):
        print(f"  {name}: {importance:.3f}")
    
    # Phase 3: Grid prediction
    print("\n=== Phase 3: Grid Prediction ===")
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)
    X_pred = np.column_stack([grid_xx.ravel(), grid_yy.ravel()])
    
    print(f"Prediction grid: {X_pred.shape}")
    
    start_time = time.time()
    z_pred = rf.predict(X_pred)
    prediction_time = time.time() - start_time
    
    z_rf = z_pred.reshape(grid_xx.shape)
    print(f"Prediction time: {prediction_time:.2f} seconds")
    print(f"Prediction range: {z_rf.min():.1f} - {z_rf.max():.1f} mm/hr")
    print(f"Prediction mean: {z_rf.mean():.1f} mm/hr")
    
    # Phase 4: Validation
    print("\n=== Phase 4: Validation ===")
    print(f"Original rainfall range: {z.min():.1f} - {z.max():.1f} mm/hr")
    print(f"Predicted rainfall range: {z_rf.min():.1f} - {z_rf.max():.1f} mm/hr")
    
    # Handle negative values
    if z_rf.min() < 0:
        print(f"Correcting negative values: {z_rf.min():.1f} -> 0")
        z_rf[z_rf < 0] = 0
    
    # Check NaN
    nan_count = np.isnan(z_rf).sum()
    print(f"NaN values: {nan_count}")
    
    # Save results
    try:
        np.savez('cell4_random_forest_results.npz',
                z_rf=z_rf,
                grid_x=grid_x,
                grid_y=grid_y)
        print("\nResults saved to cell4_random_forest_results.npz")
    except Exception as e:
        print(f"Error saving results: {e}")
    
    # Create visualization
    try:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Left: Random Forest prediction
        im1 = axes[0].imshow(z_rf, extent=[grid_x.min(), grid_x.max(), grid_y.min(), grid_y.max()],
                           origin='lower', cmap='YlOrRd', aspect='auto')
        axes[0].scatter(x, y, c=z, s=50, cmap='YlOrRd', edgecolors='black', linewidths=1)
        axes[0].set_title('Random Forest Prediction', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Easting (m)')
        axes[0].set_ylabel('Northing (m)')
        plt.colorbar(im1, ax=axes[0], label='Rainfall (mm/hr)')
        
        # Right: Prediction histogram
        axes[1].hist(z_rf.ravel(), bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        axes[1].axvline(z_rf.mean(), color='red', linestyle='--', label=f'Mean: {z_rf.mean():.1f}')
        axes[1].set_title('Prediction Distribution', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Rainfall (mm/hr)')
        axes[1].set_ylabel('Grid points')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('cell4_random_forest_results.png', dpi=300, bbox_inches='tight')
        print("Visualization saved to cell4_random_forest_results.png")
        plt.show()
        
    except Exception as e:
        print(f"Error creating visualization: {e}")
    
    print("\n" + "="*60)
    print("Cell 4 Random Forest Implementation Complete!")
    print("="*60)
    print(f"Training time: {training_time:.2f} seconds")
    print(f"Prediction time: {prediction_time:.2f} seconds")
    print(f"Training R^2: {train_r2:.4f}")
    print(f"Prediction grid: {z_rf.shape}")
    print(f"Prediction range: {z_rf.min():.1f} - {z_rf.max():.1f} mm/hr")
    print("Output variable: z_rf (ready for comparison)")
    
    return z_rf, rf, grid_x, grid_y

if __name__ == "__main__":
    results = main()

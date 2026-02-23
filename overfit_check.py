"""
Check for overfitting gap in the trained Random Forest model
"""
import pandas as pd
import numpy as np
import joblib
import json
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("Analyzing Model for Overfitting...")
print("=" * 70)

# 1. Load the trained model
print("\n1. Loading trained model...")
model = joblib.load('models/random_forest_phone_price_model.pkl')
print("   ✓ Model loaded successfully")

# 2. Load feature names and metadata
with open('models/feature_names.json', 'r') as f:
    feature_names = json.load(f)
with open('models/model_metadata.json', 'r') as f:
    metadata = json.load(f)
print(f"   ✓ Model training date: {metadata.get('trained_date')}")

# 3. Load and prepare data
print("\n2. Loading and preparing data...")
df = pd.read_csv('data/phone-details/cleaned_my_dataset.csv')
X = df.drop(columns=['Price'], errors='ignore')
y = df['Price']
X = pd.get_dummies(X, columns=['model'], drop_first=True)
print(f"   ✓ Total samples: {len(df)}")

# 4. Recreate the same train-test split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"   ✓ Training samples: {len(X_train)}")
print(f"   ✓ Testing samples: {len(X_test)}")

# 5. Evaluate on TRAINING data
print("\n3. Evaluating on TRAINING data...")
y_train_pred = model.predict(X_train)
train_r2 = r2_score(y_train, y_train_pred)
train_mae = mean_absolute_error(y_train, y_train_pred)
train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))

print(f"   Training R² Score: {train_r2:.4f} ({train_r2*100:.2f}%)")
print(f"   Training MAE:      Rs. {train_mae:,.2f}")
print(f"   Training RMSE:     Rs. {train_rmse:,.2f}")

# 6. Evaluate on TEST data
print("\n4. Evaluating on TEST data...")
y_test_pred = model.predict(X_test)
test_r2 = r2_score(y_test, y_test_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)
test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))

print(f"   Test R² Score:     {test_r2:.4f} ({test_r2*100:.2f}%)")
print(f"   Test MAE:          Rs. {test_mae:,.2f}")
print(f"   Test RMSE:         Rs. {test_rmse:,.2f}")

# 7. Calculate Overfitting Gap
print("\n5. Overfitting Gap Analysis")
print("=" * 70)

r2_gap = train_r2 - test_r2
r2_gap_percent = (r2_gap / train_r2) * 100 if train_r2 != 0 else 0

mae_gap = test_mae - train_mae
mae_gap_percent = (mae_gap / train_mae) * 100 if train_mae != 0 else 0

rmse_gap = test_rmse - train_rmse
rmse_gap_percent = (rmse_gap / train_rmse) * 100 if train_rmse != 0 else 0

print(f"\nR² Score Gap:")
print(f"   Training: {train_r2:.4f}  |  Test: {test_r2:.4f}")
print(f"   Gap: {r2_gap:.4f} ({r2_gap_percent:.2f}% drop)")

print(f"\nMAE Gap:")
print(f"   Training: Rs. {train_mae:,.2f}  |  Test: Rs. {test_mae:,.2f}")
print(f"   Gap: Rs. {mae_gap:,.2f} ({mae_gap_percent:.2f}% increase)")

print(f"\nRMSE Gap:")
print(f"   Training: Rs. {train_rmse:,.2f}  |  Test: Rs. {test_rmse:,.2f}")
print(f"   Gap: Rs. {rmse_gap:,.2f} ({rmse_gap_percent:.2f}% increase)")

# 8. Overfitting Assessment
print("\n" + "=" * 70)
print("OVERFITTING ASSESSMENT")
print("=" * 70)

# Common thresholds for overfitting:
# - R² gap > 10% is concerning
# - R² gap > 5% is moderate
# - R² gap < 5% is good

if r2_gap_percent < 5:
    assessment = "✅ EXCELLENT - Minimal overfitting"
    color = "GREEN"
elif r2_gap_percent < 10:
    assessment = "⚠️  MODERATE - Some overfitting present"
    color = "YELLOW"
else:
    assessment = "❌ HIGH - Significant overfitting detected"
    color = "RED"

print(f"\nOverall Assessment: {assessment}")
print(f"\nR² Gap: {r2_gap_percent:.2f}%")

if r2_gap_percent < 5:
    print("\n📊 Interpretation:")
    print("   - The model generalizes well to unseen data")
    print("   - Training and test performance are very close")
    print("   - Pruning parameters (max_depth=15, min_samples_split=5) are effective")
    print("   - Random Forest ensemble is preventing overfitting")
elif r2_gap_percent < 10:
    print("\n📊 Interpretation:")
    print("   - The model shows moderate overfitting")
    print("   - Consider:")
    print("     * Reducing max_depth further")
    print("     * Increasing min_samples_split")
    print("     * Reducing number of features")
    print("     * Collecting more training data")
else:
    print("\n📊 Interpretation:")
    print("   - The model memorizes training data too much")
    print("   - Action required:")
    print("     * Stronger regularization needed")
    print("     * Reduce model complexity")
    print("     * Review feature engineering")
    print("     * Increase dataset size")

# 9. Feature-wise analysis
print("\n" + "=" * 70)
print("ADDITIONAL INSIGHTS")
print("=" * 70)

# Calculate residuals
train_residuals = np.abs(y_train - y_train_pred)
test_residuals = np.abs(y_test - y_test_pred)

print(f"\nResidual Statistics:")
print(f"   Training - Mean Residual: Rs. {train_residuals.mean():,.2f}")
print(f"   Training - Median Residual: Rs. {train_residuals.median():,.2f}")
print(f"   Training - Std Dev: Rs. {train_residuals.std():,.2f}")
print(f"\n   Test - Mean Residual: Rs. {test_residuals.mean():,.2f}")
print(f"   Test - Median Residual: Rs. {test_residuals.median():,.2f}")
print(f"   Test - Std Dev: Rs. {test_residuals.std():,.2f}")

# Model complexity
print(f"\nModel Complexity:")
print(f"   Number of Trees: {model.n_estimators}")
print(f"   Max Depth: {model.max_depth}")
print(f"   Min Samples Split: {model.min_samples_split}")
print(f"   Number of Features: {len(feature_names)}")

print("\n" + "=" * 70)
"""
EVMitra ML Training Script
===========================
Target: Predict EV Range (km) from vehicle specifications

Dataset: Built from EVMitra's own structured EV database
         (curated from manufacturer specifications)

Features used:
    - battery_kwh       : Battery capacity in kWh
    - motor_power_kw    : Motor power in kW
    - wh_per_km         : Energy consumption in Wh/km
    - vehicle_type_enc  : Encoded vehicle type (Car=0, Scooter=1, Motorcycle=2, E-Rickshaw=3)

Target:
    - range_km          : Claimed range in km

Models tested:
    1. Linear Regression
    2. Random Forest Regressor
    3. Gradient Boosting Regressor

Evaluation metrics:
    - MAE (Mean Absolute Error)
    - RMSE (Root Mean Squared Error)
    - R² (Coefficient of Determination)

Author: EVMitra Project
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "evmitra.db")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "ev_range_model.pkl")
META_PATH = os.path.join(MODEL_DIR, "model_metadata.json")

os.makedirs(MODEL_DIR, exist_ok=True)


def load_data_from_db():
    """Load EV data from the SQLite database."""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT battery_kwh, motor_power_kw, wh_per_km, vehicle_type, range_km
        FROM ev_vehicles
        WHERE battery_kwh IS NOT NULL
          AND motor_power_kw IS NOT NULL
          AND wh_per_km IS NOT NULL
          AND range_km IS NOT NULL
    """, conn)
    conn.close()
    return df


def augment_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Augment small dataset with physically plausible synthetic data points
    for a more robust ML model.
    
    These synthetic rows are generated based on physics:
        range_km = (battery_kwh * 1000) / wh_per_km
    with small noise added.

    NOTE: Clearly documented as synthetic augmentation for academic ML training.
    """
    np.random.seed(42)
    synthetic_rows = []

    # Augment each real EV with 3 nearby synthetic variants
    for _, row in df.iterrows():
        for _ in range(3):
            bat_noise = row["battery_kwh"] * np.random.uniform(0.90, 1.10)
            pwr_noise = row["motor_power_kw"] * np.random.uniform(0.90, 1.10)
            wh_noise = row["wh_per_km"] * np.random.uniform(0.92, 1.08)
            # Range follows physics with small noise
            range_est = (bat_noise * 1000 / wh_noise) * np.random.uniform(0.95, 1.05)
            synthetic_rows.append({
                "battery_kwh": round(bat_noise, 2),
                "motor_power_kw": round(pwr_noise, 2),
                "wh_per_km": round(wh_noise, 2),
                "vehicle_type": row["vehicle_type"],
                "range_km": round(range_est, 1),
            })

    aug_df = pd.concat([df, pd.DataFrame(synthetic_rows)], ignore_index=True)
    return aug_df


def train_models(X_train, X_test, y_train, y_test):
    """Train and evaluate multiple regression models."""
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        results[name] = {
            "model": model,
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2": round(r2, 4),
        }
        print(f"  {name}: MAE={mae:.1f} km, RMSE={rmse:.1f} km, R²={r2:.4f}")

    return results


def select_best_model(results: dict):
    """Select model with highest R² score."""
    best_name = max(results, key=lambda k: results[k]["r2"])
    print(f"\n✅ Best model: {best_name} (R²={results[best_name]['r2']})")
    return best_name, results[best_name]


def main():
    print("=" * 60)
    print("EVMitra ML Training – EV Range Prediction")
    print("=" * 60)

    # 1. Load data
    print("\n📥 Loading data from database...")
    df = load_data_from_db()
    print(f"   Raw records: {len(df)}")

    if len(df) < 5:
        print("❌ Not enough data in database. Please run init_db.py first.")
        sys.exit(1)

    # 2. Augment data
    print("📊 Augmenting dataset for robust training...")
    df = augment_data(df)
    print(f"   After augmentation: {len(df)} records")

    # 3. Encode vehicle type
    le = LabelEncoder()
    df["vehicle_type_enc"] = le.fit_transform(df["vehicle_type"])

    # 4. Features & target
    FEATURES = ["battery_kwh", "motor_power_kw", "wh_per_km", "vehicle_type_enc"]
    TARGET = "range_km"

    X = df[FEATURES].values
    y = df[TARGET].values

    # 5. Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\n📂 Train size: {len(X_train)}, Test size: {len(X_test)}")

    # 6. Train models
    print("\n🤖 Training models...")
    results = train_models(X_train, X_test, y_train, y_test)

    # 7. Select best
    best_name, best_result = select_best_model(results)

    # 8. Save model
    save_package = {
        "model": best_result["model"],
        "feature_names": FEATURES,
        "label_encoder": le,
        "label_encoder_classes": list(le.classes_),
    }
    joblib.dump(save_package, MODEL_PATH)
    print(f"\n💾 Model saved: {MODEL_PATH}")

    # 9. Save metadata
    metadata = {
        "model_name": best_name,
        "target": TARGET,
        "features": FEATURES,
        "vehicle_type_classes": list(le.classes_),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "metrics": {
            name: {k: v for k, v in res.items() if k != "model"}
            for name, res in results.items()
        },
        "best_model_metrics": {
            "mae": best_result["mae"],
            "rmse": best_result["rmse"],
            "r2": best_result["r2"],
        },
        "dataset_note": (
            "Training data: EVMitra curated EV specs database (manufacturer data) "
            "+ physically-plausible synthetic augmentation. "
            "range_km = (battery_kwh × 1000) / wh_per_km ± noise."
        ),
        "trained_on": str(pd.Timestamp.now().date()),
    }
    with open(META_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"📋 Metadata saved: {META_PATH}")

    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print(f"   Model: {best_name}")
    print(f"   MAE : {best_result['mae']} km")
    print(f"   RMSE: {best_result['rmse']} km")
    print(f"   R²  : {best_result['r2']}")
    print("=" * 60)

    return metadata


if __name__ == "__main__":
    main()

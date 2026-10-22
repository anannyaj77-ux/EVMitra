"""
EVMitra ML Prediction Module
Loads trained model and provides range prediction interface
"""

import os
import json
import joblib
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "ev_range_model.pkl")
META_PATH = os.path.join(MODEL_DIR, "model_metadata.json")


def load_model():
    """Load the trained model package. Returns (package, error_message)."""
    if not os.path.exists(MODEL_PATH):
        return None, "Model file not found. Please run ml/train_model.py first."
    try:
        package = joblib.load(MODEL_PATH)
        return package, None
    except Exception as e:
        return None, f"Error loading model: {e}"


def load_metadata():
    """Load model metadata. Returns dict or None."""
    if not os.path.exists(META_PATH):
        return None
    with open(META_PATH, "r") as f:
        return json.load(f)


def predict_range(battery_kwh: float, motor_power_kw: float,
                  wh_per_km: float, vehicle_type: str) -> dict:
    """
    Predict EV range using the trained ML model.

    Args:
        battery_kwh     : Battery capacity in kWh
        motor_power_kw  : Motor power in kW
        wh_per_km       : Energy consumption in Wh/km
        vehicle_type    : One of ['Car', 'E-Rickshaw', 'Motorcycle', 'Scooter']

    Returns:
        dict with keys: predicted_range_km, physics_range_km, model_name, error
    """
    package, err = load_model()
    if err:
        # Fall back to physics-based estimate
        physics_range = round((battery_kwh * 1000) / wh_per_km, 1) if wh_per_km > 0 else 0
        return {
            "predicted_range_km": physics_range,
            "physics_range_km": physics_range,
            "model_name": "Physics Estimate (model not available)",
            "error": err,
        }

    try:
        le = package["label_encoder"]
        classes = list(le.classes_)

        # Handle unknown vehicle type gracefully
        if vehicle_type not in classes:
            vehicle_type = "Car"  # default fallback

        vt_enc = le.transform([vehicle_type])[0]
        features = np.array([[battery_kwh, motor_power_kw, wh_per_km, vt_enc]])
        predicted = float(package["model"].predict(features)[0])
        physics_range = round((battery_kwh * 1000) / wh_per_km, 1) if wh_per_km > 0 else 0

        metadata = load_metadata()
        model_name = metadata["model_name"] if metadata else "Trained ML Model"

        return {
            "predicted_range_km": round(max(predicted, 0), 1),
            "physics_range_km": physics_range,
            "model_name": model_name,
            "error": None,
        }
    except Exception as e:
        physics_range = round((battery_kwh * 1000) / wh_per_km, 1) if wh_per_km > 0 else 0
        return {
            "predicted_range_km": physics_range,
            "physics_range_km": physics_range,
            "model_name": "Physics Estimate (prediction error)",
            "error": str(e),
        }

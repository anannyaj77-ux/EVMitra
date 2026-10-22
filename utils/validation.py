"""
EVMitra Input Validation Utility
"""
import pandas as pd


def validate_positive_number(value, field_name: str) -> tuple:
    """Returns (is_valid: bool, error_message: str)"""
    try:
        v = float(value)
        if v <= 0:
            return False, f"{field_name} must be greater than zero."
        return True, ""
    except (TypeError, ValueError):
        return False, f"{field_name} must be a valid number."


def validate_owner_csv(df: pd.DataFrame) -> tuple:
    """
    Validate an uploaded owner analytics CSV.
    
    Required columns: date, distance_km, energy_consumed_kwh
    Optional columns: charging_cost_inr, temperature_c, notes
    
    Returns:
        (is_valid: bool, error_message: str, cleaned_df or None)
    """
    REQUIRED_COLS = {"date", "distance_km", "energy_consumed_kwh"}
    
    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        return False, f"Missing required columns: {', '.join(sorted(missing))}", None
    
    # Check for empty dataframe
    if df.empty:
        return False, "The uploaded file contains no data rows.", None
    
    # Convert types
    try:
        df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce")
        df["energy_consumed_kwh"] = pd.to_numeric(df["energy_consumed_kwh"], errors="coerce")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    except Exception as e:
        return False, f"Data type conversion error: {e}", None
    
    # Drop rows where critical values are missing
    before = len(df)
    df = df.dropna(subset=["date", "distance_km", "energy_consumed_kwh"])
    dropped = before - len(df)
    
    if df.empty:
        return False, "No valid rows after removing missing/invalid values.", None
    
    # Remove physically impossible values
    df = df[(df["distance_km"] > 0) & (df["energy_consumed_kwh"] > 0)]
    
    if df.empty:
        return False, "No rows with valid positive distance and energy values.", None
    
    msg = ""
    if dropped > 0:
        msg = f"Note: {dropped} rows with missing/invalid data were skipped."
    
    return True, msg, df.reset_index(drop=True)

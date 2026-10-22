"""
EVMitra Test Script
Run with: python test_all.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  [PASS] {name}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        failed += 1

print("=" * 55)
print("  EVMitra Automated Test Suite")
print("=" * 55)

# ── Database tests ────────────────────────────────────
print("\n[1] Database Tests")

def test_ev_count():
    from utils.db_helper import execute_query
    evs = execute_query("SELECT COUNT(*) as c FROM ev_vehicles")
    assert evs[0]["c"] >= 20, f"Expected 20+ EVs, got {evs[0]['c']}"

def test_scheme_count():
    from utils.db_helper import execute_query
    schemes = execute_query("SELECT COUNT(*) as c FROM govt_schemes")
    assert schemes[0]["c"] >= 5, f"Expected 5+ schemes"

def test_showroom_count():
    from utils.db_helper import execute_query
    rows = execute_query("SELECT COUNT(*) as c FROM showrooms")
    assert rows[0]["c"] >= 10

def test_charging_count():
    from utils.db_helper import execute_query
    rows = execute_query("SELECT COUNT(*) as c FROM charging_stations")
    assert rows[0]["c"] >= 10

def test_ev_search():
    from utils.db_helper import execute_query
    rows = execute_query("SELECT * FROM ev_vehicles WHERE brand = 'Tata'")
    assert len(rows) >= 3, "Expected Tata EVs"

test("EV vehicle count (>=20)", test_ev_count)
test("Govt scheme count (>=5)", test_scheme_count)
test("Showroom count (>=10)", test_showroom_count)
test("Charging station count (>=10)", test_charging_count)
test("EV search by brand", test_ev_search)

# ── Calculation tests ─────────────────────────────────
print("\n[2] Calculation Tests")

def test_ev_cost():
    from utils.calculations import calculate_ev_cost
    r = calculate_ev_cost(1000, 120, 8.0)
    assert r["energy_kwh"] == 120.0
    assert r["cost_inr"] == 960.0

def test_petrol_cost():
    from utils.calculations import calculate_petrol_cost
    r = calculate_petrol_cost(1000, 15, 105)
    assert abs(r["litres_used"] - 66.67) < 0.1
    assert abs(r["cost_inr"] - 7000.0) < 1.0

def test_savings():
    from utils.calculations import calculate_savings
    s = calculate_savings(960, 7000)
    assert s == 6040.0

def test_co2():
    from utils.calculations import calculate_co2_avoided
    co2 = calculate_co2_avoided(66.67)
    assert co2 > 100  # expect about 154 kg

def test_recommendation_score():
    from utils.calculations import recommendation_score
    ev = {"brand": "Tata", "model": "Nexon EV", "vehicle_type": "Car",
          "price_inr": 1399000, "range_km": 465, "battery_kwh": 40.5, "charge_time_hrs": 8.6}
    prefs = {"budget": 1500000, "daily_km": 40, "required_range_km": 100,
             "vehicle_type": "Car", "brand_preference": "Any", "fast_charge_preference": False}
    score = recommendation_score(ev, prefs)
    assert score > 50, f"Expected score >50, got {score}"

def test_recommendation_reasons():
    from utils.calculations import generate_recommendation_reasons
    ev = {"brand": "Tata", "model": "Nexon EV", "vehicle_type": "Car",
          "price_inr": 1399000, "range_km": 465, "battery_kwh": 40.5, "charge_time_hrs": 8.6}
    prefs = {"budget": 1500000, "daily_km": 40, "required_range_km": 100,
             "vehicle_type": "Car", "brand_preference": "Any"}
    reasons = generate_recommendation_reasons(ev, prefs)
    assert len(reasons) > 0

test("EV cost calculation", test_ev_cost)
test("Petrol cost calculation", test_petrol_cost)
test("Savings calculation", test_savings)
test("CO2 avoided calculation", test_co2)
test("Recommendation scoring", test_recommendation_score)
test("Recommendation reasons", test_recommendation_reasons)

# ── CSV Validation tests ──────────────────────────────
print("\n[3] CSV Validation Tests")

def test_valid_csv():
    import pandas as pd
    from utils.validation import validate_owner_csv
    df = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "distance_km": [40, 50],
        "energy_consumed_kwh": [3.5, 4.2]
    })
    is_valid, msg, clean = validate_owner_csv(df)
    assert is_valid, f"Valid CSV rejected: {msg}"
    assert len(clean) == 2

def test_missing_columns():
    import pandas as pd
    from utils.validation import validate_owner_csv
    bad_df = pd.DataFrame({"wrong_col": [1, 2]})
    is_valid, msg, clean = validate_owner_csv(bad_df)
    assert not is_valid, "Should reject CSV with missing columns"
    assert "Missing required columns" in msg

def test_empty_csv():
    import pandas as pd
    from utils.validation import validate_owner_csv
    empty_df = pd.DataFrame(columns=["date", "distance_km", "energy_consumed_kwh"])
    is_valid, msg, clean = validate_owner_csv(empty_df)
    assert not is_valid, "Should reject empty CSV"

def test_negative_values_filtered():
    import pandas as pd
    from utils.validation import validate_owner_csv
    df = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "distance_km": [40, -5, 50],  # -5 should be filtered
        "energy_consumed_kwh": [3.5, 0.5, 4.2]
    })
    is_valid, msg, clean = validate_owner_csv(df)
    assert is_valid
    assert len(clean) == 2  # row with -5 dropped

test("Valid CSV accepted", test_valid_csv)
test("Missing columns rejected", test_missing_columns)
test("Empty CSV rejected", test_empty_csv)
test("Negative values filtered", test_negative_values_filtered)

# ── ML tests ─────────────────────────────────────────
print("\n[4] ML Model Tests")

def test_model_load():
    from ml.predict import load_model
    pkg, err = load_model()
    assert err is None, f"Model load error: {err}"
    assert pkg is not None

def test_model_predict():
    from ml.predict import predict_range
    r = predict_range(40.5, 127, 87, "Car")
    assert r["error"] is None, f"Prediction error: {r['error']}"
    assert r["predicted_range_km"] > 0

def test_model_metadata():
    from ml.predict import load_metadata
    meta = load_metadata()
    assert meta is not None
    assert "model_name" in meta
    assert meta["best_model_metrics"]["r2"] > 0.9

def test_unknown_vehicle_type():
    from ml.predict import predict_range
    r = predict_range(30, 80, 100, "UnknownType")
    assert r["predicted_range_km"] > 0  # should fallback gracefully

def test_physics_estimate():
    from ml.predict import predict_range
    r = predict_range(40, 100, 100, "Car")
    # physics: (40*1000)/100 = 400 km
    assert abs(r["physics_range_km"] - 400) < 5

test("Model loads successfully", test_model_load)
test("Prediction returns valid result", test_model_predict)
test("Model R2 >= 0.9", test_model_metadata)
test("Unknown vehicle type handled", test_unknown_vehicle_type)
test("Physics estimate correct", test_physics_estimate)

# ── Explorer / Filter tests ───────────────────────────
print("\n[5] EV Explorer Filter Tests")

def test_brand_filter():
    from modules.ev_explorer import load_vehicles
    df = load_vehicles({"brand": "Tata", "vehicle_type": "All"})
    assert not df.empty
    assert all(df["brand"] == "Tata")

def test_price_filter():
    from modules.ev_explorer import load_vehicles
    df = load_vehicles({"min_price": 0, "max_price": 1000000})
    assert not df.empty
    assert all(df["price_inr"] <= 1000000)

def test_search():
    from modules.ev_explorer import load_vehicles
    df = load_vehicles({"search_term": "Nexon"})
    assert not df.empty

def test_fast_charge_filter():
    from modules.ev_explorer import load_vehicles
    df = load_vehicles({"fast_charge_only": True})
    assert not df.empty
    assert all(df["fast_charge_supported"] == 1)

def test_no_results():
    from modules.ev_explorer import load_vehicles
    df = load_vehicles({"brand": "NonExistentBrand12345"})
    assert df.empty

test("Brand filter", test_brand_filter)
test("Price filter", test_price_filter)
test("Search filter", test_search)
test("Fast charge filter", test_fast_charge_filter)
test("Empty result handled", test_no_results)

# ── Recommendation tests ──────────────────────────────
print("\n[6] Recommendation Engine Tests")

def test_top3_recommendations():
    from modules.recommendation import get_recommendations
    prefs = {"budget": 1500000, "daily_km": 40, "required_range_km": 100,
             "vehicle_type": "Car", "brand_preference": "Any", "fast_charge_preference": False}
    recs = get_recommendations(prefs)
    assert len(recs) >= 1
    assert len(recs) <= 3
    assert all(r["score"] > 0 for r in recs)
    assert all(len(r["reasons"]) > 0 for r in recs)

def test_no_match_fallback():
    from modules.recommendation import get_recommendations
    prefs = {"budget": 10000, "daily_km": 1000, "required_range_km": 2000,
             "vehicle_type": "Car", "brand_preference": "Any"}
    recs = get_recommendations(prefs)
    # Should return empty list (not crash)
    assert isinstance(recs, list)

test("Top 3 recommendations returned", test_top3_recommendations)
test("No-match handled gracefully", test_no_match_fallback)

# ── Charging / Showroom / Schemes tests ──────────────
print("\n[7] Data Module Tests")

def test_schemes_load():
    from modules.schemes import load_schemes
    schemes = load_schemes()
    assert len(schemes) >= 5

def test_schemes_filter():
    from modules.schemes import load_schemes
    active = load_schemes({"status": "Active"})
    assert len(active) >= 1

def test_showrooms_by_city():
    from modules.showrooms import load_showrooms
    rows = load_showrooms("Mumbai")
    assert len(rows) >= 2

def test_charging_by_city():
    from modules.charging import load_stations
    rows = load_stations("Mumbai")
    assert len(rows) >= 2

def test_charging_by_type():
    from modules.charging import load_stations
    rows = load_stations(charger_type="CCS2")
    assert len(rows) >= 1

test("Government schemes load", test_schemes_load)
test("Schemes filter by status", test_schemes_filter)
test("Showrooms by city (Mumbai)", test_showrooms_by_city)
test("Charging stations by city (Mumbai)", test_charging_by_city)
test("Charging filter by type (CCS2)", test_charging_by_type)

# ── Summary ───────────────────────────────────────────
print()
print("=" * 55)
print(f"  Results: {passed} PASSED  |  {failed} FAILED")
print("=" * 55)
if failed > 0:
    print("  Some tests failed — check errors above.")
    sys.exit(1)
else:
    print("  All tests passed! EVMitra is ready for demo.")

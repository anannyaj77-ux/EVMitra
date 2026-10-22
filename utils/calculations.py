"""
EVMitra Calculations Utility
All financial and environmental calculation formulas
"""


def calculate_ev_cost(distance_km: float, wh_per_km: float, tariff_per_kwh: float) -> dict:
    """
    Calculate EV running cost.
    
    Args:
        distance_km: Total distance in km
        wh_per_km: EV energy consumption in Wh/km
        tariff_per_kwh: Electricity tariff in ₹/kWh
    
    Returns:
        dict with energy_kwh and cost_inr
    """
    energy_kwh = distance_km * wh_per_km / 1000.0
    cost_inr = energy_kwh * tariff_per_kwh
    return {"energy_kwh": round(energy_kwh, 2), "cost_inr": round(cost_inr, 2)}


def calculate_petrol_cost(distance_km: float, mileage_kmpl: float, petrol_price_per_litre: float) -> dict:
    """
    Calculate petrol vehicle running cost.
    
    Args:
        distance_km: Total distance in km
        mileage_kmpl: Petrol vehicle mileage in km/litre
        petrol_price_per_litre: Petrol price in ₹/litre
    
    Returns:
        dict with litres_used and cost_inr
    """
    litres = distance_km / mileage_kmpl
    cost_inr = litres * petrol_price_per_litre
    return {"litres_used": round(litres, 2), "cost_inr": round(cost_inr, 2)}


def calculate_savings(ev_cost: float, petrol_cost: float) -> float:
    """Calculate savings (positive means EV is cheaper)."""
    return round(petrol_cost - ev_cost, 2)


def calculate_co2_avoided(petrol_litres: float, co2_factor_kg_per_litre: float = 2.31) -> float:
    """
    Estimate CO2 emissions avoided by using EV instead of petrol.
    
    co2_factor: ~2.31 kg CO2 per litre of petrol burned
    Source: IPCC / Central Pollution Control Board estimates (approx.)
    
    Returns:
        CO2 avoided in kg (estimate)
    """
    return round(petrol_litres * co2_factor_kg_per_litre, 2)


def calculate_ev_range(battery_kwh: float, wh_per_km: float) -> float:
    """Estimate EV range from battery and efficiency."""
    if wh_per_km <= 0:
        return 0.0
    return round((battery_kwh * 1000) / wh_per_km, 1)


def recommendation_score(ev: dict, prefs: dict) -> float:
    """
    Weighted recommendation score for a single EV against user preferences.
    
    Weights (must sum to 1.0):
        price       : 0.30
        range       : 0.30
        vehicle_type: 0.20
        charging    : 0.10
        brand       : 0.10
    
    Returns:
        float score between 0 and 100
    """
    score = 0.0
    max_score = 100.0

    # --- Price (30 points) ---
    budget = prefs.get("budget", 0)
    price = ev.get("price_inr", float("inf"))
    if budget > 0 and price <= budget:
        price_ratio = price / budget  # lower is better within budget
        score += 30 * (1 - price_ratio * 0.5)  # small bonus for being cheaper
    elif budget > 0 and price > budget:
        overshoot = (price - budget) / budget
        score += max(0, 30 * (1 - overshoot * 2))  # penalty

    # --- Range (30 points) ---
    daily_km = prefs.get("daily_km", 0)
    ev_range = ev.get("range_km", 0)
    required_range = prefs.get("required_range_km", daily_km * 2)  # safety buffer
    if ev_range >= required_range:
        score += 30
    elif ev_range > 0:
        score += 30 * (ev_range / required_range)

    # --- Vehicle type (20 points) ---
    preferred_type = prefs.get("vehicle_type", "Any")
    ev_type = ev.get("vehicle_type", "")
    if preferred_type == "Any" or preferred_type.lower() == ev_type.lower():
        score += 20

    # --- Charging preference (10 points) ---
    home_charging = prefs.get("home_charging", True)
    fast_charge = prefs.get("fast_charge_preference", False)
    charge_time = ev.get("charge_time_hrs", 10)
    if fast_charge and charge_time < 2:
        score += 10
    elif not fast_charge or charge_time < 8:
        score += 7

    # --- Brand preference (10 points) ---
    preferred_brand = prefs.get("brand_preference", "Any")
    ev_brand = ev.get("brand", "")
    if preferred_brand == "Any" or preferred_brand.lower() == ev_brand.lower():
        score += 10

    return round(min(score, max_score), 2)


def generate_recommendation_reasons(ev: dict, prefs: dict) -> list:
    """
    Generate human-readable reasons why this EV was recommended.
    
    Returns:
        list of reason strings
    """
    reasons = []

    budget = prefs.get("budget", 0)
    price = ev.get("price_inr", 0)
    if budget > 0 and price <= budget:
        reasons.append(f"Price ₹{price:,.0f} is within your budget of ₹{budget:,.0f}.")

    daily_km = prefs.get("daily_km", 0)
    ev_range = ev.get("range_km", 0)
    required_range = prefs.get("required_range_km", daily_km * 2)
    if ev_range >= required_range:
        reasons.append(f"Range of {ev_range} km comfortably covers your daily {daily_km} km with buffer.")

    preferred_type = prefs.get("vehicle_type", "Any")
    ev_type = ev.get("vehicle_type", "")
    if preferred_type == "Any" or preferred_type.lower() == ev_type.lower():
        reasons.append(f"Matches your preferred vehicle type: {ev_type}.")

    preferred_brand = prefs.get("brand_preference", "Any")
    ev_brand = ev.get("brand", "")
    if preferred_brand != "Any" and preferred_brand.lower() == ev_brand.lower():
        reasons.append(f"Matches your preferred brand: {ev_brand}.")

    charge_time = ev.get("charge_time_hrs", 10)
    if charge_time < 2:
        reasons.append(f"Supports fast charging (≈{charge_time}h to full).")
    elif charge_time <= 6:
        reasons.append(f"Reasonable charging time of ≈{charge_time}h.")

    if not reasons:
        reasons.append("Closest available match based on your requirements.")

    return reasons

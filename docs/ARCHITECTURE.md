# EVMitra – System Architecture & Documentation

## 1. Project Overview

**EVMitra** is a Python + Streamlit EV information and analytics platform.

### Problem Statement
EV buyers and owners in India lack a unified platform to explore EVs, compare models, calculate running costs, understand government incentives, and analyze their own EV usage.

### Proposed Solution
A web-based EV companion application with:
- EV database with search/filter/comparison
- Rule-based recommendation engine (Find My EV)
- Cost calculator with real formulas
- Owner analytics via CSV upload
- ML-powered range prediction
- Government scheme directory
- Charging station & showroom locator

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────┐
│              User (Browser)                      │
└─────────────────┬───────────────────────────────┘
                  │ HTTP (localhost:8501)
┌─────────────────▼───────────────────────────────┐
│           Streamlit Application (app.py)         │
│  ┌──────────────────────────────────────────┐   │
│  │            Navigation & Routing           │   │
│  └──────┬───────────────────────────────────┘   │
│         │                                        │
│  ┌──────▼──────────────────────────────────┐    │
│  │           Feature Modules               │    │
│  │  ev_explorer │ recommendation │ compare  │    │
│  │  analytics   │ cost_calculator│ environ  │    │
│  │  schemes     │ charging       │ showrooms│    │
│  │  ml_insights │ history        │ admin    │    │
│  └──────┬──────────────────────────────────┘    │
│         │                                        │
│  ┌──────▼──────────────────────────────────┐    │
│  │         Utilities Layer                 │    │
│  │  db_helper │ calculations │ validation  │    │
│  └──────┬──────────────────────────────────┘    │
│         │                                        │
│  ┌──────▼──────────────────────────────────┐    │
│  │         Data Layer                      │    │
│  │  SQLite DB │ ML Models │ CSV Files      │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

---

## 3. Database Schema (ER Diagram Description)

### Tables

#### ev_vehicles
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| brand | TEXT | Manufacturer name |
| model | TEXT | Model name |
| vehicle_type | TEXT | Car/Scooter/Motorcycle/E-Rickshaw |
| price_inr | REAL | Ex-showroom price |
| battery_kwh | REAL | Battery capacity |
| range_km | REAL | Claimed range |
| charge_time_hrs | REAL | Full charge time |
| motor_power_kw | REAL | Peak motor power |
| top_speed_kmh | REAL | Top speed |
| wh_per_km | REAL | Energy efficiency |
| fast_charge_supported | INTEGER | 0/1 boolean |
| fast_charge_time_mins | REAL | Fast charge duration |
| seating_capacity | INTEGER | Number of seats |
| warranty_years | REAL | Battery/vehicle warranty |
| features | TEXT | Comma-separated feature list |
| source | TEXT | Data source |
| last_updated | TEXT | Date last updated |

#### govt_schemes
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| scheme_name | TEXT | Full scheme name |
| scheme_type | TEXT | Central/State |
| state | TEXT | Applicable state |
| vehicle_types | TEXT | Applicable vehicle types |
| eligibility | TEXT | Who can apply |
| benefits | TEXT | Scheme benefits |
| subsidy_amount | REAL | Per unit subsidy |
| max_subsidy | REAL | Maximum subsidy cap |
| scheme_status | TEXT | Active/Closed/Upcoming |
| valid_from | TEXT | Start date |
| valid_until | TEXT | End date |
| official_url | TEXT | Government website URL |
| source | TEXT | Data source |
| last_updated | TEXT | Last verified |

#### showrooms
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| brand | TEXT | EV brand |
| showroom_name | TEXT | Full showroom name |
| city | TEXT | City |
| state | TEXT | State |
| address | TEXT | Street address |
| phone | TEXT | Contact number |
| google_maps_url | TEXT | Direct maps link |
| lat, lng | REAL | Coordinates |
| working_hours | TEXT | Opening hours |

#### charging_stations
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| station_name | TEXT | Station name |
| operator | TEXT | Operating company |
| city, state | TEXT | Location |
| charger_types | TEXT | CCS2/CHAdeMO/Type2/AC |
| max_power_kw | REAL | Maximum charging power |
| num_connectors | INTEGER | Number of charging points |
| is_24x7 | INTEGER | Round-the-clock availability |
| pricing_info | TEXT | Cost per kWh |

#### notifications
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| category | TEXT | scheme/charging/general |
| title | TEXT | Alert title |
| message | TEXT | Alert message |
| severity | TEXT | info/success/warning |
| is_active | INTEGER | 0/1 active flag |

---

## 4. Data Flow (DFD Level 1)

```
User Input
    │
    ▼
[Streamlit UI] ──filters──► [db_helper.py] ──SQL──► [SQLite DB]
    │                                                      │
    │                              EV Data ◄───────────────┘
    │
    ├──► [calculations.py] ──► Cost / CO2 / Score results
    │
    ├──► [validation.py] ──► CSV validation ──► [analytics.py]
    │
    └──► [ml/predict.py] ──► [model.pkl] ──► Range prediction
```

---

## 5. Recommendation Engine Methodology

**Algorithm:** Weighted Scoring (Rule-Based, NOT Machine Learning)

```
Score = Σ(weight_i × component_i)    [Max = 100 points]

Weight Distribution:
  Price Match     : 30 points
  Range Adequacy  : 30 points  
  Vehicle Type    : 20 points
  Charging Pref   : 10 points
  Brand Pref      : 10 points

Hard Filters (applied before scoring):
  - Price must be ≤ 120% of budget
  - Range must be ≥ 50% of required range

Output: Top 3 EVs ranked by score + human-readable reasons
```

**Why rule-based?** The dataset (manufacturer specs) does not contain behavioral user data needed for collaborative filtering or content-based ML recommendation. A transparent scoring system is more defensible and explainable for an academic project.

---

## 6. ML Methodology

**Target:** EV Range (km) prediction  
**Why Range?** It is the most practically useful metric, directly calculable from available features (battery, efficiency), and allows model validation against physics.

**Features:**
1. battery_kwh – Battery capacity (most important predictor)
2. motor_power_kw – Motor output
3. wh_per_km – Energy efficiency (second most important)
4. vehicle_type – Encoded category

**Models Compared:**
1. Linear Regression – Baseline
2. Random Forest Regressor – Ensemble method
3. Gradient Boosting Regressor – Boosting method

**Evaluation:**
- MAE: Mean Absolute Error (average prediction error in km)
- RMSE: Root Mean Squared Error (penalizes large errors more)
- R²: Coefficient of Determination (1.0 = perfect)

**Data:** EVMitra curated EV specs + physics-based synthetic augmentation  
(`range = battery_kWh × 1000 / wh_per_km ± 5% noise`)

---

## 7. Cost Calculation Formulas

```
EV Running Cost:
  energy_kWh = distance_km × wh_per_km ÷ 1000
  ev_cost_₹  = energy_kWh × electricity_tariff_₹_per_kWh

Petrol Vehicle Running Cost:
  petrol_litres = distance_km ÷ mileage_km_per_litre
  petrol_cost_₹ = petrol_litres × petrol_price_₹_per_litre

Savings:
  savings_₹ = petrol_cost_₹ − ev_cost_₹

All results labeled as ESTIMATES.
```

---

## 8. Environmental Calculation

```
CO₂ Avoided (kg) = Petrol Avoided (L) × 2.31 kg/L

CO₂ factor: 2.31 kg CO₂ per litre of petrol combusted
Source: IPCC 2006 Guidelines / CPCB approximation

Note: Estimates tailpipe/direct emissions ONLY.
      NOT official carbon credits.
      EVs have upstream manufacturing & grid emissions (not calculated here).
```

---

## 9. API Design & Fallbacks

| Service | Integration Method | Fallback |
|---------|-------------------|----------|
| Maps | Google Maps URL links | Direct links work without API key |
| Charging data | Reference database | Static SQLite data |
| Govt schemes | Manual curation | SQLite with official source URLs |
| EV specs | Manufacturer websites | SQLite with source metadata |

**No API key is required** for core functionality.

---

## 10. Security Notes

- Admin credentials stored in `.env` (never hardcoded)
- `.env` excluded from Git via `.gitignore`
- SQLite uses parameterized queries (no SQL injection risk)
- No user passwords stored (no user login system)
- Session state used for browser-local history only

---

## 11. Limitations

1. EV data is curated manually — may not reflect latest models/prices
2. Government scheme validity must be re-verified before decisions
3. ML model trained on small dataset with synthetic augmentation
4. Charging station availability is NOT live
5. Cost calculations are estimates based on input values
6. Environmental estimates are tailpipe only (not lifecycle)
7. No mobile app; Streamlit optimized for desktop/laptop

---

## 12. Future Scope

- IoT / Battery Management System integration for real-time telemetry
- Live charging station availability via OCPP / third-party APIs
- Fleet management for commercial EV operators
- Mobile application (React Native / Flutter)
- Advanced AI chatbot for EV guidance
- Predictive battery degradation maintenance alerts
- Real-time fuel/electricity price API integration
- Route planning with charging stop optimization
- Community reviews and ratings for EVs and showrooms
- Gamification for eco-friendly driving achievements

---

## 13. Viva Q&A

**Q: What is EVMitra?**
A: EVMitra is a Python-Streamlit web application that helps users explore, compare, and analyze Electric Vehicles. It includes an EV database, recommendation engine, cost calculator, government scheme directory, and ML range prediction.

**Q: Why did you choose Streamlit?**
A: Streamlit allows rapid development of data-driven web apps in pure Python without needing separate frontend code. It's ideal for an MCA academic project focused on data and ML.

**Q: Explain the recommendation algorithm.**
A: It's a transparent weighted scoring system (NOT ML). Each EV gets a score out of 100 based on: price (30%), range (30%), vehicle type (20%), charging (10%), brand (10%). Hard filters remove clearly unsuitable EVs first. Top 3 scorers are returned with reasons.

**Q: What ML model did you use and why?**
A: We tested Linear Regression, Random Forest, and Gradient Boosting for EV range prediction. The best model (by R²) is automatically selected. Range was chosen as the target because it's directly supported by available features (battery, efficiency) and verifiable against physics.

**Q: What is the CO₂ calculation?**
A: CO₂ Avoided = Petrol Litres Saved × 2.31 kg/L. The factor 2.31 kg CO₂ per litre is from IPCC guidelines. This estimates only tailpipe emissions avoided—it's not official carbon credits.

**Q: How is the database structured?**
A: SQLite with 5 tables: ev_vehicles, govt_schemes, showrooms, charging_stations, notifications. All use parameterized queries. Source and last_updated fields track data freshness.

**Q: How does Admin work?**
A: Admin login uses credentials from the .env file (never hardcoded). Admins can add/edit/delete EVs, schemes, and notifications through a Streamlit form UI.

**Q: What happens if no EV matches recommendation criteria?**
A: A friendly message suggests adjusting budget, range requirements, or vehicle type. The app never crashes—hard filters still return partial matches when possible.

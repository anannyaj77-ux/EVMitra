# EVMitra Smart Electric Vehicle Platform

> "MCA Semester 3 Mini Project"
> A Python based intelligent EV platform acting as a digital companion for EV buyers and owners.

 Quick Start

 Prerequisites
 Python 3.10 or higher
 Windows / macOS / Linux

1 Clone / Download the Project

```bash
# If using Git:
git clone <your-repo-url>
cd EVMitra

# Or simply extract the project ZIP and open the folder
```

2 Create a Virtual Environment (Recommended)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

 3 Install Dependencies

```bash
pip install -r requirements.txt
```

4 Configure Environment

```bash
# Copy the example env file
copy .env.example .env        # Windows
cp .env.example .env          # macOS/Linux

# Edit .env to set your admin password (optional — defaults work for demo)
notepad .env                  # Windows
```

5 Initialize Database

```bash
python database/init_db.py
```

This creates `database/evmitra.db` with all sample data.

 6 Train ML Model

```bash
python ml/train_model.py
```

This trains the EV range prediction model and saves it to `ml/models/`.

7 Run the Application

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

One Command Setup (Windows)

```bash
setup.bat
```

Or manually run:
```bash
python -m pip install -r requirements.txt
python database/init_db.py
python ml/train_model.py
streamlit run app.py
```

---

 Project Structure

```
EVMitra/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .gitignore
├── README.md
│
├── database/
│   ├── init_db.py              # Database initialization + seed data
│   └── evmitra.db              # SQLite database (auto-created)
│
├── modules/                    # Feature modules
│   ├── ev_explorer.py          # EV browsing with search & filters
│   ├── recommendation.py       # Find My EV (weighted scoring)
│   ├── comparison.py           # Side-by-side EV comparison
│   ├── analytics.py            # Owner analytics (CSV upload)
│   ├── cost_calculator.py      # EV vs Petrol cost calculator
│   ├── environmental.py        # CO₂ & environmental impact
│   ├── schemes.py              # Government EV schemes
│   ├── charging.py             # Charging station finder
│   ├── showrooms.py            # Showroom locator
│   ├── ml_insights.py          # ML range prediction
│   ├── history.py              # Session history
│   └── admin.py                # Admin panel
│
├── ml/
│   ├── train_model.py          # ML training script
│   ├── predict.py              # Prediction interface
│   └── models/                 # Saved model files (auto-created)
│
├── utils/
│   ├── db_helper.py            # Database operations
│   ├── calculations.py         # All financial/scientific formulas
│   └── validation.py           # Input & CSV validation
│
├── data/
│   └── sample_owner_analytics.csv  # Sample CSV for Owner Analytics demo
│
├── assets/
│   └── VIDEO_INSTRUCTIONS.txt  # Instructions for adding EV video
│
└── docs/
    └── (documentation files)
```



 Admin Access

Default admin credentials (set in `.env`):
- **Username:** `admin`
- **Password:** `evmitra2024`

>  **Change the password in your `.env` file before demo!**

Navigate to **Admin** in the sidebar → Enter credentials → Manage EVs, Schemes, Notifications.


 EV Video

To display an EV video on the Home page:
1. Download a free EV video from [Pexels](https://pexels.com) or [Pixabay](https://pixabay.com)
2. Rename it to `ev_showcase.mp4`
3. Place it in `assets/ev_showcase.mp4`
4. Restart the app

If no video file is present, a YouTube embed is shown as fallback (requires internet).

---

 Sample CSV for Owner Analytics

Use `data/sample_owner_analytics.csv` to demo the Owner Analytics module.

**Required columns:**
| Column | Required | Description |
|--------|----------|-------------|
| `date` | ✅ | Date (YYYY-MM-DD) |
| `distance_km` | ✅ | Distance driven |
| `energy_consumed_kwh` | ✅ | Energy consumed |
| `charging_cost_inr` | Optional | Charging cost |
| `temperature_c` | Optional | Temperature |

---

 ML Model

- **Target:** EV Range (km) prediction
- **Features:** Battery (kWh), Motor Power (kW), Efficiency (Wh/km), Vehicle Type
- **Models tested:** Linear Regression, Random Forest, Gradient Boosting
- **Best model:** Selected automatically by highest R²
- **Metrics shown:** MAE, RMSE, R² (actual values from training)

---

 API Keys (Optional)

EVMitra works **without any API keys**. All features have local fallbacks.

| Feature | Without API Key | With API Key |
|---------|----------------|--------------|
| Maps | Google Maps links | (no additional key needed — links work) |
| Charging | Reference database | Reference database |
| Showrooms | Reference database | Reference database |


 Features

| Module | Status |
|--------|--------|
| Home / Landing Page | ✅ Complete |
| EV Explorer (25+ EVs, search, filter, sort) | ✅ Complete |
| Find My EV (Top 3 recommendations) | ✅ Complete |
| Compare EVs (side-by-side) | ✅ Complete |
| Owner Analytics (CSV upload) | ✅ Complete |
| EV vs Petrol Cost Calculator | ✅ Complete |
| Environmental Impact | ✅ Complete |
| Government Schemes (11 schemes) | ✅ Complete |
| Charging Stations (15 stations) | ✅ Complete |
| Showrooms (17 showrooms) | ✅ Complete |
| ML Insights (Range Prediction) | ✅ Complete |
| Session History | ✅ Complete |
| Admin Panel | ✅ Complete |
| EV Video Section | ✅ Complete (with fallback) |


 Technology Stack

| Layer | Technology |
|-------|-----------|
| UI Framework | Streamlit |
| Language | Python 3.10+ |
| Database | SQLite |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Visualization | Plotly |
| Environment | python-dotenv |



 Disclaimer

EVMitra is an **MCA academic mini-project**. All data is for educational purposes only.
- EV specifications: From manufacturer websites and public sources
- Government schemes: From official government sources (may change)
- Cost calculations: Estimates based on input values
- ML predictions: Based on training data with documented methodology
- Environmental estimates: Tailpipe CO₂ only (not lifecycle)


 Author

MCA Semester 3 Mini Project  
Academic Year 2024–25

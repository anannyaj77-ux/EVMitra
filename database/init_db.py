"""
EVMitra Database Initialization & Seed Data
Run this script once to create the SQLite database and populate it with sample data.
"""

import sqlite3
import os
import sys

DB_DIR = os.path.join(os.path.dirname(__file__))
DB_PATH = os.path.join(DB_DIR, "evmitra.db")


def create_tables(conn):
    """Create all database tables."""
    conn.executescript("""
        -- EV Vehicles table
        CREATE TABLE IF NOT EXISTS ev_vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,        -- Car, Scooter, Motorcycle, Bus, Rickshaw
            price_inr REAL NOT NULL,
            battery_kwh REAL,
            range_km REAL,
            charge_time_hrs REAL,
            motor_power_kw REAL,
            top_speed_kmh REAL,
            wh_per_km REAL,                    -- energy consumption
            fast_charge_supported INTEGER DEFAULT 0,
            fast_charge_time_mins REAL,
            seating_capacity INTEGER,
            warranty_years REAL,
            features TEXT,                     -- comma-separated
            color_options TEXT,
            source TEXT,
            last_updated TEXT,
            UNIQUE(brand, model)
        );

        -- Government Schemes table
        CREATE TABLE IF NOT EXISTS govt_schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scheme_name TEXT NOT NULL,
            scheme_type TEXT,                  -- Central, State
            state TEXT,                        -- 'All India' or specific state
            vehicle_types TEXT,                -- comma-separated
            eligibility TEXT,
            benefits TEXT NOT NULL,
            subsidy_amount REAL,
            max_subsidy REAL,
            scheme_status TEXT DEFAULT 'Active',
            valid_from TEXT,
            valid_until TEXT,
            official_url TEXT,
            source TEXT,
            last_updated TEXT
        );

        -- Showrooms table
        CREATE TABLE IF NOT EXISTS showrooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            showroom_name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            google_maps_url TEXT,
            lat REAL,
            lng REAL,
            working_hours TEXT,
            source TEXT,
            last_updated TEXT
        );

        -- Charging Stations table
        CREATE TABLE IF NOT EXISTS charging_stations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT NOT NULL,
            operator TEXT,
            city TEXT NOT NULL,
            state TEXT,
            address TEXT,
            charger_types TEXT,                -- AC Slow, DC Fast, CCS2, CHAdeMO, Type2
            max_power_kw REAL,
            num_connectors INTEGER,
            phone TEXT,
            google_maps_url TEXT,
            lat REAL,
            lng REAL,
            is_24x7 INTEGER DEFAULT 0,
            pricing_info TEXT,
            data_source TEXT,
            last_updated TEXT
        );

        -- Admin configuration (non-sensitive)
        CREATE TABLE IF NOT EXISTS admin_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key TEXT UNIQUE NOT NULL,
            config_value TEXT,
            description TEXT,
            last_updated TEXT
        );

        -- Notifications/Alerts
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,            -- 'scheme', 'charging', 'general'
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT DEFAULT 'info',      -- info, warning, success
            is_active INTEGER DEFAULT 1,
            created_at TEXT,
            expires_at TEXT
        );
    """)
    conn.commit()
    print("✅ Tables created.")


def seed_ev_vehicles(conn):
    """Insert realistic Indian EV market data."""
    vehicles = [
        # (brand, model, vehicle_type, price_inr, battery_kwh, range_km, charge_time_hrs,
        #  motor_power_kw, top_speed_kmh, wh_per_km, fast_charge_supported, fast_charge_time_mins,
        #  seating_capacity, warranty_years, features, color_options, source, last_updated)

        # --- CARS ---
        ("Tata", "Nexon EV", "Car", 1399000, 40.5, 465, 8.6,
         127, 120, 87, 1, 56, 5, 8,
         "360-degree camera,Electric sunroof,Ventilated seats,Auto AC,Cruise control,Connected car tech",
         "Pristine White,Fearless Purple,Flame Red,Daytona Grey,Midnight Black",
         "Tata Motors Official Website", "2024-06-01"),

        ("Tata", "Tiago EV", "Car", 799000, 24, 315, 8.7,
         55, 120, 76, 1, 65, 5, 8,
         "Leatherette seats,Auto AC,Touchscreen infotainment,Rear camera,Electric sunroof",
         "Daytona Grey,Midnight Black,Pristine White,Tropical Mist",
         "Tata Motors Official Website", "2024-06-01"),

        ("Tata", "Punch EV", "Car", 999000, 35, 421, 9.4,
         90, 120, 83, 1, 56, 5, 8,
         "Panoramic sunroof,360-degree camera,Ventilated seats,Auto AC,Wireless charging",
         "Seaweed,Starlight,Pristine White,Fearless Purple,Atomic Orange",
         "Tata Motors Official Website", "2024-06-01"),

        ("Tata", "Tigor EV", "Car", 1299000, 26, 306, 8.5,
         55, 120, 85, 1, 65, 5, 8,
         "Touchscreen infotainment,Rear camera,Auto AC,Cruise control",
         "Pristine White,Daytona Grey,Midnight Black,Arizona Blue",
         "Tata Motors Official Website", "2024-06-01"),

        ("MG", "ZS EV", "Car", 2199000, 50.3, 461, 8.5,
         130, 140, 109, 1, 50, 5, 5,
         "Panoramic sunroof,360-degree camera,Heated seats,Wireless charging,10.1-inch infotainment",
         "Glaze Red,Starry Black,Pearl White,Marble White",
         "MG Motor India Website", "2024-06-01"),

        ("MG", "Comet EV", "Car", 699000, 17.3, 230, 7,
         42, 100, 75, 0, None, 4, 3,
         "7-inch touchscreen,Auto AC,Rear camera,Fast charging port",
         "Bubblegum Blue,Candy White,Aurora Silver,Starry Black",
         "MG Motor India Website", "2024-06-01"),

        ("Hyundai", "Ioniq 5", "Car", 4599000, 72.6, 631, 18,
         168, 185, 115, 1, 18, 5, 5,
         "Augmented reality HUD,V2L technology,12.3-inch infotainment,Heated/ventilated seats",
         "Gravity Gold,Phantom Black,Lucid Blue,Cyber Grey,Atlas White",
         "Hyundai India Website", "2024-06-01"),

        ("Hyundai", "Ioniq 6", "Car", 5390000, 77.4, 614, 18,
         168, 185, 126, 1, 18, 5, 5,
         "Digital side mirrors,V2L,Wireless charging,Full LED lighting",
         "Gravity Gold,Phantom Black,Lucid Blue,Cyber Grey",
         "Hyundai India Website", "2024-09-01"),

        ("Kia", "EV6", "Car", 6095000, 77.4, 528, 18,
         168, 185, 147, 1, 18, 5, 7,
         "V2L technology,Curved display,Auto flush door handles,HUD",
         "Snow White Pearl,Aurora Black Pearl,Runway Red,Yacht Blue",
         "Kia India Website", "2024-06-01"),

        ("BYD", "Atto 3", "Car", 3399000, 60.48, 521, 9,
         150, 160, 116, 1, 50, 5, 8,
         "360-degree camera,Blade battery,Rotating centre console,Voice control",
         "Harbour Grey,Ski White,Boulder Grey",
         "BYD India Website", "2024-06-01"),

        ("BYD", "Seal", "Car", 4199000, 82.56, 650, 9.5,
         230, 180, 127, 1, 35, 5, 6,
         "Blade battery,Rotating HUD,Adaptive air suspension,15.6-inch infotainment",
         "Cosmos Black,Glacier White,Celestial Blue",
         "BYD India Website", "2024-09-01"),

        ("Mahindra", "BE 6e", "Car", 1849000, 79, 682, 21,
         170, 170, 116, 1, 20, 5, 8,
         "Panoramic sunroof,Shoot Up console,ADAS,8-speaker Harman audio",
         "Everest White,Burnt Sienna,Teal Ombre",
         "Mahindra Website", "2025-01-01"),

        ("Mahindra", "XEV 9e", "Car", 2149000, 79, 656, 21,
         170, 170, 120, 1, 20, 5, 8,
         "Triple screen setup,Aircraft-inspired cabin,ADAS,Harman Kardon audio",
         "Stealth Black,Icicle White,Crimson Red",
         "Mahindra Website", "2025-01-01"),

        ("Volvo", "XC40 Recharge", "Car", 6550000, 78, 418, 8,
         300, 180, 187, 1, 40, 5, 8,
         "Google built-in,Bowers & Wilkins audio,360-degree camera,Pilot Assist",
         "Fjord Blue,Crystal White,Onyx Black,Vapour Grey",
         "Volvo India Website", "2024-06-01"),

        ("BMW", "iX1", "Car", 6799000, 64.7, 440, 10.5,
         230, 180, 147, 1, 29, 5, 5,
         "BMW Curved Display,Harman Kardon audio,Parking assistant,Ambient lighting",
         "Mineral White,Jet Black,Phytonic Blue",
         "BMW India Website", "2024-06-01"),

        # --- SCOOTERS ---
        ("Ola Electric", "S1 Pro", "Scooter", 147499, 4, 195, 6.5,
         8.5, 120, 31, 1, 75, 2, 3,
         "7-inch touchscreen,MoveOS,Hill hold,Reverse mode,Cruise control",
         "Jet Black,Porcelain White,Caicos Blue,Coral Glam,Midnight Blue",
         "Ola Electric Website", "2024-06-01"),

        ("Ola Electric", "S1 Air", "Scooter", 104999, 3, 151, 6.5,
         6, 90, 20, 0, None, 2, 3,
         "7-inch touchscreen,MoveOS,Hill hold,Reverse mode",
         "Jet Black,Porcelain White,Caicos Blue,Coral Glam",
         "Ola Electric Website", "2024-06-01"),

        ("Ather Energy", "450X", "Scooter", 146390, 3.7, 146, 5.4,
         6, 90, 25, 1, 80, 2, 3,
         "Touchscreen dashboard,Ather Grid compatible,Guide mode,Warp mode",
         "Cosmic Black,Silver Grey,Space Grey,Racing Red",
         "Ather Energy Website", "2024-06-01"),

        ("TVS", "iQube Electric", "Scooter", 119990, 3.4, 145, 5,
         4.4, 78, 23, 0, None, 2, 3,
         "7-inch touchscreen,SmartXonnect,Navigation,Eco/Power/Sport modes",
         "White,Grey,Blue,Red",
         "TVS Motor Website", "2024-06-01"),

        ("Bajaj", "Chetak Premium", "Scooter", 134999, 3.0, 126, 5,
         4.2, 73, 24, 0, None, 2, 3,
         "IP67 waterproof body,4G connectivity,Digital instrument cluster",
         "Cyber White,Steel Blue,Hazel Brown,Hazel Honey",
         "Bajaj Auto Website", "2024-06-01"),

        ("Hero Electric", "Optima HX", "Scooter", 79900, 1.8, 120, 5,
         1.3, 45, 15, 0, None, 2, 3,
         "Digital cluster,USB charging,Reverse assist,Remote diagnostics",
         "Brown,Green,Red,Blue",
         "Hero Electric Website", "2024-06-01"),

        ("Ampere", "Magnus EX", "Scooter", 84990, 1.92, 121, 5,
         1.55, 55, 16, 0, None, 2, 2,
         "Digital cluster,USB port,Remote lock/unlock,Find my vehicle",
         "White,Black,Red,Blue",
         "Greaves Electric Website", "2024-06-01"),

        # --- MOTORCYCLES ---
        ("Revolt", "RV400", "Motorcycle", 152990, 3.24, 150, 4.5,
         8.5, 85, 22, 1, 90, 2, 3,
         "App connectivity,Artificial exhaust sound,Geo-fencing,Eco/Normal/Sport",
         "Rebel Red,Cosmic Black,Mist Grey",
         "Revolt Motors Website", "2024-06-01"),

        ("Tork Motors", "Kratos R", "Motorcycle", 144999, 4, 180, 5,
         7.5, 105, 22, 1, 80, 2, 3,
         "7-inch touchscreen,IP67,4G connectivity,GPS,Cloud connectivity",
         "Matte Black,Glossy Black",
         "Tork Motors Website", "2024-06-01"),

        ("Ola Electric", "Roadster", "Motorcycle", 199999, 4.5, 200, 5.5,
         11, 130, 23, 1, 60, 2, 3,
         "7-inch display,MoveOS 5,600mm seat height,Hyper mode",
         "Matte Black,White,Red",
         "Ola Electric Website", "2025-01-01"),

        # --- E-RICKSHAW ---
        ("Mahindra Treo", "Treo Yaari", "E-Rickshaw", 285000, 7.37, 130, 6,
         7, 35, 57, 0, None, 4, 3,
         "IP67 battery,Regenerative braking,Digital display",
         "Green,Yellow",
         "Mahindra Electric Website", "2024-06-01"),
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO ev_vehicles
        (brand, model, vehicle_type, price_inr, battery_kwh, range_km, charge_time_hrs,
         motor_power_kw, top_speed_kmh, wh_per_km, fast_charge_supported, fast_charge_time_mins,
         seating_capacity, warranty_years, features, color_options, source, last_updated)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, vehicles)
    conn.commit()
    print(f"✅ {len(vehicles)} EV vehicles seeded.")


def seed_govt_schemes(conn):
    """Insert government EV schemes data."""
    schemes = [
        # (scheme_name, scheme_type, state, vehicle_types, eligibility, benefits,
        #  subsidy_amount, max_subsidy, scheme_status, valid_from, valid_until,
        #  official_url, source, last_updated)

        ("FAME II – Faster Adoption and Manufacturing of Electric Vehicles",
         "Central", "All India",
         "Car,Scooter,Motorcycle,Bus,E-Rickshaw",
         "Individual buyers, fleet operators, public transport agencies",
         "Upfront subsidy on purchase price; ₹10,000/kWh for electric 2-wheelers; up to ₹1.5 lakh for 4-wheelers; reduced GST to 5%",
         10000, 150000, "Closed – Succeeded by PM E-DRIVE",
         "2019-04-01", "2024-03-31",
         "https://heavyindustries.gov.in/fame-india",
         "Ministry of Heavy Industries", "2024-06-01"),

        ("PM E-DRIVE Scheme",
         "Central", "All India",
         "Car,Scooter,Motorcycle,Bus,E-Rickshaw",
         "Individual and institutional buyers; deployed through authorized dealers",
         "₹10,900 crore scheme; subsidy on electric 2-wheelers, 3-wheelers, trucks, buses; charging infrastructure creation",
         None, None, "Active",
         "2024-10-01", "2026-03-31",
         "https://heavyindustries.gov.in",
         "Ministry of Heavy Industries", "2024-10-01"),

        ("Maharashtra EV Policy 2021",
         "State", "Maharashtra",
         "Car,Scooter,Motorcycle,E-Rickshaw",
         "Individual and institutional buyers; vehicles registered in Maharashtra",
         "₹5,000/kWh incentive on 2W (max ₹10,000); ₹5,000/kWh on 3W (max ₹30,000); ₹5,000/kWh on 4W (max ₹1.5 lakh); road tax exemption; registration fee waiver",
         5000, 150000, "Active",
         "2021-07-01", "2025-12-31",
         "https://mahadiscom.in/ev-policy",
         "Government of Maharashtra", "2024-06-01"),

        ("Delhi EV Policy",
         "State", "Delhi",
         "Car,Scooter,Motorcycle,E-Rickshaw",
         "Delhi residents purchasing EVs with Delhi registration",
         "₹5,000/kWh subsidy on 2W (max ₹30,000); ₹30,000 on 3W; ₹1.5 lakh on 4W; road tax waiver; scrapping incentive",
         5000, 150000, "Active",
         "2020-08-01", "2024-12-31",
         "https://ev.delhi.gov.in",
         "Delhi Government", "2024-06-01"),

        ("Gujarat EV Policy 2021",
         "State", "Gujarat",
         "Car,Scooter,Motorcycle",
         "Gujarat residents; first 10,000 EVs per category eligible",
         "₹10,000 subsidy on 2W; ₹20,000 on 3W; ₹1.5 lakh on 4W; road tax exemption",
         10000, 150000, "Active",
         "2021-06-01", "2025-05-31",
         "https://geda.gujarat.gov.in",
         "Government of Gujarat", "2024-06-01"),

        ("Rajasthan EV Policy 2022",
         "State", "Rajasthan",
         "Car,Scooter,Motorcycle,E-Rickshaw",
         "Rajasthan residents and commercial vehicle operators",
         "Registration fee waiver; road tax exemption; ₹10,000 subsidy on 2W; ₹25,000 subsidy on 3W",
         10000, 25000, "Active",
         "2022-07-01", "2025-06-30",
         "https://energy.rajasthan.gov.in",
         "Government of Rajasthan", "2024-06-01"),

        ("Karnataka EV Policy 2021",
         "State", "Karnataka",
         "Car,Scooter,Motorcycle",
         "Karnataka residents; manufacturing incentives for EV makers in Karnataka",
         "Road tax waiver; registration fee waiver; interest subvention on EV loans",
         None, None, "Active",
         "2021-09-01", "2026-03-31",
         "https://ev.karnataka.gov.in",
         "Government of Karnataka", "2024-06-01"),

        ("Tamil Nadu EV Policy 2023",
         "State", "Tamil Nadu",
         "Car,Scooter,Motorcycle,Bus",
         "Tamil Nadu residents and fleet operators",
         "Road tax exemption; 100% registration fee waiver; interest subsidy on loans; charging infrastructure subsidy",
         None, None, "Active",
         "2023-10-01", "2027-09-30",
         "https://teda.in",
         "Government of Tamil Nadu", "2024-06-01"),

        ("Telangana EV Policy 2020",
         "State", "Telangana",
         "Car,Scooter,Motorcycle,Bus,E-Rickshaw",
         "Telangana residents; EV manufacturers in Telangana",
         "Road tax exemption; registration fee waiver; ₹10,000 subsidy on 2W; various commercial vehicle subsidies",
         10000, 10000, "Active",
         "2020-09-01", "2025-08-31",
         "https://tsiic.telangana.gov.in",
         "Government of Telangana", "2024-06-01"),

        ("GST Reduction on EVs",
         "Central", "All India",
         "Car,Scooter,Motorcycle,Bus,E-Rickshaw",
         "All buyers of electric vehicles",
         "GST reduced to 5% on all EVs (down from 12%); EV chargers at 5% GST",
         None, None, "Active",
         "2019-07-01", None,
         "https://cbic.gov.in",
         "CBIC / Ministry of Finance", "2024-06-01"),

        ("Section 80EEB – Income Tax Deduction on EV Loan",
         "Central", "All India",
         "Car,Scooter,Motorcycle",
         "Individual taxpayers who take a loan to purchase an EV for personal use",
         "Deduction up to ₹1.5 lakh per year on interest paid on EV loan under Section 80EEB of Income Tax Act",
         None, 150000, "Active",
         "2019-04-01", None,
         "https://incometax.gov.in",
         "Income Tax Department of India", "2024-06-01"),
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO govt_schemes
        (scheme_name, scheme_type, state, vehicle_types, eligibility, benefits,
         subsidy_amount, max_subsidy, scheme_status, valid_from, valid_until,
         official_url, source, last_updated)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, schemes)
    conn.commit()
    print(f"✅ {len(schemes)} government schemes seeded.")


def seed_showrooms(conn):
    """Insert EV showroom data."""
    showrooms = [
        # (brand, showroom_name, city, state, address, phone, email, google_maps_url, lat, lng, working_hours, source, last_updated)
        ("Tata", "Tata Motors EV Studio – Andheri", "Mumbai", "Maharashtra",
         "Andheri East, Mumbai, Maharashtra 400069", "+91-22-66007755", "",
         "https://maps.google.com/?q=Tata+Motors+Andheri+Mumbai", 19.1136, 72.8697,
         "Mon-Sat: 9AM-7PM, Sun: 10AM-5PM", "Tata Motors Website", "2024-06-01"),

        ("Tata", "Tata Motors – Koramangala", "Bengaluru", "Karnataka",
         "80 Feet Road, Koramangala, Bengaluru 560034", "+91-80-25535500", "",
         "https://maps.google.com/?q=Tata+Motors+Koramangala+Bengaluru", 12.9352, 77.6245,
         "Mon-Sat: 9AM-7PM, Sun: 10AM-5PM", "Tata Motors Website", "2024-06-01"),

        ("Tata", "Tata Motors – Connaught Place", "Delhi", "Delhi",
         "Connaught Place, New Delhi 110001", "+91-11-43517100", "",
         "https://maps.google.com/?q=Tata+Motors+Connaught+Place+Delhi", 28.6315, 77.2167,
         "Mon-Sat: 9AM-7PM, Sun: 10AM-5PM", "Tata Motors Website", "2024-06-01"),

        ("Tata", "Tata Motors EV Showroom – Pune", "Pune", "Maharashtra",
         "Baner Road, Pune, Maharashtra 411045", "+91-20-27290000", "",
         "https://maps.google.com/?q=Tata+Motors+Baner+Pune", 18.5590, 73.7868,
         "Mon-Sat: 9AM-7PM, Sun: 10AM-5PM", "Tata Motors Website", "2024-06-01"),

        ("MG", "MG Motor – Worli", "Mumbai", "Maharashtra",
         "Worli, Mumbai, Maharashtra 400018", "+91-22-66700800", "",
         "https://maps.google.com/?q=MG+Motor+Worli+Mumbai", 19.0148, 72.8184,
         "Mon-Sat: 9AM-7PM, Sun: 10AM-5PM", "MG Motor India", "2024-06-01"),

        ("MG", "MG Motor – Whitefield", "Bengaluru", "Karnataka",
         "Whitefield Main Road, Bengaluru 560066", "+91-80-67890000", "",
         "https://maps.google.com/?q=MG+Motor+Whitefield+Bengaluru", 12.9695, 77.7499,
         "Mon-Sat: 9AM-7PM, Sun: 10AM-5PM", "MG Motor India", "2024-06-01"),

        ("Hyundai", "Hyundai IONIQ Studio – Gurugram", "Gurugram", "Haryana",
         "DLF Cyber City, Gurugram, Haryana 122002", "+91-124-4500800", "",
         "https://maps.google.com/?q=Hyundai+IONIQ+Studio+Gurugram", 28.4949, 77.0887,
         "Mon-Sat: 9AM-7PM, Sun: 10AM-5PM", "Hyundai India", "2024-06-01"),

        ("Ola Electric", "Ola Electric Experience Centre – HSR Layout", "Bengaluru", "Karnataka",
         "HSR Layout Sector 1, Bengaluru 560102", "+91-99000-11111", "",
         "https://maps.google.com/?q=Ola+Electric+HSR+Layout+Bengaluru", 12.9116, 77.6389,
         "Mon-Sun: 9AM-8PM", "Ola Electric Website", "2024-06-01"),

        ("Ola Electric", "Ola Electric – Andheri", "Mumbai", "Maharashtra",
         "MIDC Andheri East, Mumbai 400093", "+91-99000-22222", "",
         "https://maps.google.com/?q=Ola+Electric+Andheri+Mumbai", 19.1107, 72.8721,
         "Mon-Sun: 9AM-8PM", "Ola Electric Website", "2024-06-01"),

        ("Ather Energy", "Ather Space – Indira Nagar", "Bengaluru", "Karnataka",
         "100 Feet Road, Indiranagar, Bengaluru 560038", "+91-80-47118000", "",
         "https://maps.google.com/?q=Ather+Space+Indiranagar+Bengaluru", 12.9784, 77.6408,
         "Mon-Sat: 10AM-8PM, Sun: 11AM-6PM", "Ather Energy Website", "2024-06-01"),

        ("Ather Energy", "Ather Space – Bandra", "Mumbai", "Maharashtra",
         "Bandra West, Mumbai, Maharashtra 400050", "+91-22-47118000", "",
         "https://maps.google.com/?q=Ather+Space+Bandra+Mumbai", 19.0544, 72.8405,
         "Mon-Sat: 10AM-8PM, Sun: 11AM-6PM", "Ather Energy Website", "2024-06-01"),

        ("BYD", "BYD India – Worli", "Mumbai", "Maharashtra",
         "Dr Annie Besant Road, Worli, Mumbai 400018", "+91-22-66556655", "",
         "https://maps.google.com/?q=BYD+India+Worli+Mumbai", 18.9938, 72.8158,
         "Mon-Sat: 10AM-7PM", "BYD India", "2024-06-01"),

        ("Mahindra", "Mahindra EV – Kandivali", "Mumbai", "Maharashtra",
         "Kandivali East, Mumbai, Maharashtra 400101", "+91-22-28001800", "",
         "https://maps.google.com/?q=Mahindra+EV+Kandivali+Mumbai", 19.2094, 72.8562,
         "Mon-Sat: 9AM-7PM, Sun: 10AM-5PM", "Mahindra Electric", "2024-06-01"),

        ("TVS", "TVS Electric – T Nagar", "Chennai", "Tamil Nadu",
         "T Nagar, Chennai, Tamil Nadu 600017", "+91-44-28343434", "",
         "https://maps.google.com/?q=TVS+Electric+T+Nagar+Chennai", 13.0418, 80.2341,
         "Mon-Sat: 9AM-7PM", "TVS Motor Company", "2024-06-01"),

        ("Tata", "Tata Motors – Hyderabad", "Hyderabad", "Telangana",
         "Banjara Hills, Hyderabad, Telangana 500034", "+91-40-23545454", "",
         "https://maps.google.com/?q=Tata+Motors+Banjara+Hills+Hyderabad", 17.4156, 78.4347,
         "Mon-Sat: 9AM-7PM, Sun: 10AM-5PM", "Tata Motors Website", "2024-06-01"),

        ("Tata", "Tata Motors – Ahmedabad", "Ahmedabad", "Gujarat",
         "Satellite, Ahmedabad, Gujarat 380015", "+91-79-26757575", "",
         "https://maps.google.com/?q=Tata+Motors+Satellite+Ahmedabad", 23.0225, 72.5714,
         "Mon-Sat: 9AM-7PM, Sun: 10AM-5PM", "Tata Motors Website", "2024-06-01"),

        ("Kia", "Kia India – Worli", "Mumbai", "Maharashtra",
         "Worli Naka, Mumbai, Maharashtra 400018", "+91-22-67007700", "",
         "https://maps.google.com/?q=Kia+India+Worli+Mumbai", 19.0120, 72.8151,
         "Mon-Sat: 9AM-7PM, Sun: 10AM-5PM", "Kia India Website", "2024-06-01"),
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO showrooms
        (brand, showroom_name, city, state, address, phone, email,
         google_maps_url, lat, lng, working_hours, source, last_updated)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, showrooms)
    conn.commit()
    print(f"✅ {len(showrooms)} showrooms seeded.")


def seed_charging_stations(conn):
    """Insert charging station data."""
    stations = [
        # (station_name, operator, city, state, address, charger_types, max_power_kw,
        #  num_connectors, phone, google_maps_url, lat, lng, is_24x7, pricing_info, data_source, last_updated)

        ("Tata Power EV Hub – BKC", "Tata Power", "Mumbai", "Maharashtra",
         "Bandra Kurla Complex, Mumbai 400051",
         "CCS2,Type2,AC", 60, 4, "+91-22-66451000",
         "https://maps.google.com/?q=Tata+Power+EV+BKC+Mumbai",
         19.0590, 72.8677, 1, "₹14/kWh (AC), ₹16/kWh (DC)",
         "Tata Power EZ Charge", "2024-06-01"),

        ("Ather Grid – HSR Layout", "Ather Energy", "Bengaluru", "Karnataka",
         "HSR Layout Sector 3, Bengaluru 560102",
         "Ather fast charger (proprietary)", 3.3, 2, "+91-80-47118000",
         "https://maps.google.com/?q=Ather+Grid+HSR+Bengaluru",
         12.9095, 77.6375, 0, "₹2 per unit for Ather owners",
         "Ather Grid App", "2024-06-01"),

        ("BESCOM EV Station – MG Road", "BESCOM", "Bengaluru", "Karnataka",
         "MG Road Metro Station, Bengaluru 560001",
         "CCS2,CHAdeMO,Type2", 50, 3, "",
         "https://maps.google.com/?q=BESCOM+EV+MG+Road+Bengaluru",
         12.9756, 77.6099, 1, "₹12/kWh",
         "BESCOM Public Portal", "2024-06-01"),

        ("Charzer Station – Connaught Place", "Charzer", "Delhi", "Delhi",
         "Block A, Connaught Place, New Delhi 110001",
         "CCS2,Type2", 22, 2, "",
         "https://maps.google.com/?q=Charzer+Connaught+Place+Delhi",
         28.6329, 77.2195, 1, "₹15/kWh",
         "Charzer App", "2024-06-01"),

        ("EVCS – Cyber City", "EVCS India", "Gurugram", "Haryana",
         "DLF Cyber Hub, Gurugram 122002",
         "CCS2,CHAdeMO,AC", 60, 6, "",
         "https://maps.google.com/?q=EVCS+Cyber+Hub+Gurugram",
         28.4949, 77.0887, 1, "₹16/kWh",
         "EVCS India Portal", "2024-06-01"),

        ("Tata Power EV – Pune IT Park", "Tata Power", "Pune", "Maharashtra",
         "Hinjewadi Phase 1, Pune 411057",
         "CCS2,Type2", 50, 3, "",
         "https://maps.google.com/?q=Tata+Power+EV+Hinjewadi+Pune",
         18.5908, 73.7380, 1, "₹14/kWh",
         "Tata Power EZ Charge", "2024-06-01"),

        ("Ola Hypercharger – Whitefield", "Ola Electric", "Bengaluru", "Karnataka",
         "Whitefield Main Road, Bengaluru 560066",
         "Ola Hypercharger", 4, 5, "",
         "https://maps.google.com/?q=Ola+Hypercharger+Whitefield+Bengaluru",
         12.9716, 77.7500, 0, "₹1.5/km equivalent",
         "Ola App", "2024-06-01"),

        ("IOCL EV Station – Andheri", "Indian Oil", "Mumbai", "Maharashtra",
         "IOCL Petrol Pump, Andheri West, Mumbai 400058",
         "CCS2,Type2,AC", 30, 2, "",
         "https://maps.google.com/?q=IOCL+EV+Andheri+Mumbai",
         19.1205, 72.8342, 0, "₹15/kWh",
         "IndianOil-EVEMS Portal", "2024-06-01"),

        ("MG Motor Fast Charger – Worli", "MG Motor", "Mumbai", "Maharashtra",
         "MG Showroom, Worli, Mumbai 400018",
         "CCS2", 60, 1, "",
         "https://maps.google.com/?q=MG+Motor+Worli+Mumbai",
         19.0148, 72.8184, 0, "Complimentary for MG owners",
         "MG Motor India", "2024-06-01"),

        ("Hyundai Dealer Charger – Gurugram", "Hyundai", "Gurugram", "Haryana",
         "MG Road, Sector 28, Gurugram 122002",
         "CCS2", 50, 1, "",
         "https://maps.google.com/?q=Hyundai+EV+Charger+Gurugram",
         28.4673, 77.0320, 0, "For Hyundai EV owners",
         "Hyundai India", "2024-06-01"),

        ("BPCL Pulse – Hebbal", "BPCL", "Bengaluru", "Karnataka",
         "Hebbal Flyover, Bengaluru 560024",
         "CCS2,Type2,AC", 60, 4, "",
         "https://maps.google.com/?q=BPCL+Pulse+Hebbal+Bengaluru",
         13.0454, 77.5967, 1, "₹13/kWh",
         "BPCL Pulse App", "2024-06-01"),

        ("Zeon Charging – T Nagar", "Zeon Charging", "Chennai", "Tamil Nadu",
         "T Nagar Bus Terminus, Chennai 600017",
         "CCS2,CHAdeMO,AC", 60, 3, "",
         "https://maps.google.com/?q=Zeon+Charging+T+Nagar+Chennai",
         13.0418, 80.2341, 1, "₹14/kWh",
         "Zeon Charging App", "2024-06-01"),

        ("EESL Charging Station – Banjara Hills", "EESL", "Hyderabad", "Telangana",
         "Road No. 10, Banjara Hills, Hyderabad 500034",
         "CCS2,Type2", 30, 2, "",
         "https://maps.google.com/?q=EESL+EV+Banjara+Hills+Hyderabad",
         17.4156, 78.4347, 0, "₹12/kWh",
         "EESL India Portal", "2024-06-01"),

        ("Fortum Charge & Drive – Satellite", "Fortum India", "Ahmedabad", "Gujarat",
         "Satellite Area, Ahmedabad 380015",
         "CCS2,AC", 22, 2, "",
         "https://maps.google.com/?q=Fortum+EV+Satellite+Ahmedabad",
         23.0300, 72.5500, 0, "₹14/kWh",
         "Fortum India", "2024-06-01"),

        ("Jio-bp EV Station – Lower Parel", "Jio-bp", "Mumbai", "Maharashtra",
         "Lower Parel, Mumbai 400013",
         "CCS2,CHAdeMO,Type2", 120, 6, "",
         "https://maps.google.com/?q=Jiobp+EV+Lower+Parel+Mumbai",
         18.9940, 72.8294, 1, "₹18/kWh (DC Fast)",
         "Jio-bp EV Hub App", "2024-06-01"),
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO charging_stations
        (station_name, operator, city, state, address, charger_types, max_power_kw,
         num_connectors, phone, google_maps_url, lat, lng, is_24x7, pricing_info,
         data_source, last_updated)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, stations)
    conn.commit()
    print(f"✅ {len(stations)} charging stations seeded.")


def seed_notifications(conn):
    """Insert sample notifications/alerts."""
    notifications = [
        ("scheme", "PM E-DRIVE Scheme Launched!",
         "The PM E-DRIVE scheme (₹10,900 crore) was launched in October 2024, replacing FAME II. Check Government Schemes for details.",
         "success", 1, "2024-10-01", None),

        ("scheme", "Income Tax Deduction Available on EV Loans",
         "Section 80EEB allows individual taxpayers to claim up to ₹1.5 lakh deduction on EV loan interest. Consult your tax advisor.",
         "info", 1, "2024-06-01", None),

        ("charging", "Jio-bp EV Stations Now Available",
         "Jio-bp has launched 120 kW DC fast charging stations in Mumbai and other cities. These support CCS2, CHAdeMO, and Type 2 connectors.",
         "info", 1, "2024-06-01", None),

        ("general", "GST on EVs is 5%",
         "All electric vehicles attract only 5% GST (down from 12%), making them significantly cheaper. EV chargers also attract 5% GST.",
         "info", 1, "2024-06-01", None),
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO notifications
        (category, title, message, severity, is_active, created_at, expires_at)
        VALUES (?,?,?,?,?,?,?)
    """, notifications)
    conn.commit()
    print(f"✅ {len(notifications)} notifications seeded.")


def seed_admin_config(conn):
    """Insert default admin config values."""
    config = [
        ("app_version", "1.0.0", "EVMitra application version", "2024-06-01"),
        ("data_last_refreshed", "2024-10-01", "Last time reference data was refreshed", "2024-10-01"),
        ("co2_factor_kg_per_litre", "2.31", "CO2 emission factor per litre of petrol (kg). Source: IPCC/CPCB approx.", "2024-06-01"),
        ("default_electricity_tariff", "8.0", "Default electricity tariff in ₹/kWh used in calculators", "2024-06-01"),
        ("default_petrol_price", "105.0", "Default petrol price in ₹/litre used in calculators", "2024-06-01"),
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO admin_config (config_key, config_value, description, last_updated)
        VALUES (?,?,?,?)
    """, config)
    conn.commit()
    print(f"✅ {len(config)} admin config entries seeded.")


def init_database():
    """Main function: initialize database, create tables, seed data."""
    os.makedirs(DB_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    try:
        create_tables(conn)
        seed_ev_vehicles(conn)
        seed_govt_schemes(conn)
        seed_showrooms(conn)
        seed_charging_stations(conn)
        seed_notifications(conn)
        seed_admin_config(conn)
        print(f"\n✅ EVMitra database initialized at: {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()

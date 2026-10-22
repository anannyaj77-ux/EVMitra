@echo off
echo ============================================================
echo        EVMitra - Smart Electric Vehicle Platform
echo             MCA Semester 3 Mini Project Setup
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python not found. Please install Python 3.10+ from python.org
        pause
        exit /b 1
    )
    set PYTHON=py
) else (
    set PYTHON=python
)

echo [1/4] Installing Python packages...
%PYTHON% -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Package installation failed. Check requirements.txt
    pause
    exit /b 1
)
echo       Done.

echo [2/4] Creating .env file (if not exists)...
if not exist ".env" (
    copy .env.example .env >nul
    echo       .env created from .env.example
    echo       Default admin: admin / evmitra2024
) else (
    echo       .env already exists, skipping.
)

echo [3/4] Initializing database...
%PYTHON% database/init_db.py
if errorlevel 1 (
    echo ERROR: Database initialization failed.
    pause
    exit /b 1
)

echo [4/4] Training ML model...
%PYTHON% ml/train_model.py
if errorlevel 1 (
    echo WARNING: ML training had an issue. The app will still run with fallback predictions.
)

echo.
echo ============================================================
echo  Setup complete! Starting EVMitra...
echo  Open your browser at: http://localhost:8501
echo ============================================================
echo.
%PYTHON% -m streamlit run app.py

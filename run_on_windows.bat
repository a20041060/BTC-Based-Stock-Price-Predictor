@echo off
TITLE BTC Stock Predictor Setup & Run

echo ===================================================
echo 🚀 Setting up BTC Stock Predictor for Windows...
echo ===================================================

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed or not in your PATH.
    echo    Please install Python 3.10+ from https://www.python.org/downloads/
    echo    Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b
)

REM Create virtual environment if it doesn't exist
IF NOT EXIST "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Run the application
echo ===================================================
echo 📈 Starting BTC Stock Predictor...
echo ✅ The app should open in your default browser automatically.
echo    If not, visit http://localhost:8501
echo ===================================================

streamlit run btc_stock_predictor_ui.py

pause

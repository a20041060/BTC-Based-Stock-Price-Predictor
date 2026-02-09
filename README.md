# 🪙 BTC Stock Predictor

An advanced financial analytics tool designed to predict stock prices (Miners & Proxy Stocks) based on Bitcoin's price movements. This project leverages historical correlation, beta analysis, and AI-driven sentiment analysis to provide actionable insights.

## 🧠 Project Mindset & Workflow

The core philosophy of this project is **Correlation-First Prediction**.
1.  **Correlation Analysis**: First, establish how strongly a stock (e.g., IREN, MARA) moves with Bitcoin.
2.  **Beta & Power Law**: Use the calculated Beta (volatility relative to BTC) and Power Law (Log-Log regression) to project future prices based on a target BTC price.
3.  **Real-Time Tracking**: Monitor live prices to see if the correlation holds in real-time.
4.  **Sentiment Overlay**: Adjust quantitative predictions with qualitative AI news sentiment (FinBERT/VADER).

## 🏗️ Architecture

The project utilizes a **Rigid Layered Architecture** that adheres to strict software engineering principles, ensuring scalability, maintainability, and testability.

### 1. Core Components
*   **`btc_stock_predictor_ui.py` (Frontend)**: The interactive Streamlit dashboard. It acts as the "View" layer, injecting dependencies from the Application layer.
*   **`predictor/application/` (Application Layer)**: Orchestrates business logic using domain objects and interfaces.
*   **`predictor/domain/` (Domain Layer)**: Defines strict Pydantic models for data entities.
*   **`predictor/infrastructure/` (Infrastructure Layer)**: Concrete implementations of interfaces (external APIs like Yahoo Finance, Finnhub).
*   **`predictor/interfaces/` (Interface Layer)**: Abstract Base Classes (ABCs) defining contracts for data providers and analyzers.
*   **`predictor/core/` (Core Layer)**: Configuration management (Pydantic Settings) and centralized logging.

### 2. Data Pipeline
*   **Real-Time BTC**: Fetched via **Binance Public API** (No key required, fastest).
*   **Real-Time Stocks**: Fetched via **Finnhub API** (Optional key) or fallback to **Yahoo Finance** (15-min delayed).
*   **Historical Data**: Sourced from **Yahoo Finance** for regression modeling.

## 🚀 Features

*   **⚡ Real-Time Dashboard**: Live price tracking for BTC and key miner stocks.
*   **🔮 Dual-Model Prediction**: Compare **Beta-based** (Linear) vs. **Power Law** (Log-Log) price targets.
*   **🤖 AI News Sentiment**: Analyzes latest news headlines to gauge market sentiment (Bullish/Bearish).
*   **🔗 Correlation Heatmap**: Visualize how different miners correlate with each other and BTC.
*   **📈 Interactive Charts**: Plotly-powered interactive regression and history charts.

## 🛠️ Installation & Usage

### Prerequisites
*   Python 3.10+
*   (Optional) Finnhub API Key for real-time stock data

### Setup (Windows)

1.  **Run the Setup Script**
    Double-click the `run_on_windows.bat` file. This will automatically:
    *   Create a virtual environment (`venv`)
    *   Install all dependencies
    *   Launch the Streamlit frontend

    *Alternatively, install manually via Command Prompt / PowerShell:*
    ```cmd
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Run the Frontend (Streamlit)**
    ```cmd
    venv\Scripts\activate
    streamlit run btc_stock_predictor_ui.py
    ```

3.  **Run the Backend (Django)**
    Open a new terminal window:
    ```cmd
    venv\Scripts\activate
    python manage.py migrate
    python manage.py runserver
    ```
    The backend will run at `http://127.0.0.1:8000/`.

### Setup (macOS/Linux)

1.  **Run the Setup Script**
    ```bash
    bash run_on_mac.sh
    ```

    *Alternatively, install manually:*
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Run the Application**
    ```bash
    source venv/bin/activate
    streamlit run btc_stock_predictor_ui.py
    ```

## 📂 Project Structure

```
btc_stock_predictor/
├── btc_stock_predictor_ui.py  # 🏠 Main Application (Streamlit Frontend)
├── btc_backend/               # ⚙️ Django Project Settings
├── predictor/                 # 🧠 Django App & Business Logic
│   ├── application/           # 🎮 Application Services
│   ├── core/                  # � Config & Logging
│   ├── domain/                # 📦 Pydantic Models
│   ├── infrastructure/        # 🔌 External API Implementations
│   ├── interfaces/            # 📝 Abstract Base Classes
│   └── views.py               # 🌐 Django Views
├── manage.py                  # 🚀 Django Management Script

├── requirements.txt           # 📦 Python Dependencies
├── run_on_mac.sh              # 🚀 Quick Start Script
├── INSTRUCTIONS.txt           # 📖 Detailed Setup Guide
└── README.md                  # 📄 Project Documentation
```

## 🛡️ Disclaimer
This tool is for educational and informational purposes only. It is **not** financial advice. Cryptocurrency and stock markets are highly volatile.

# BTC Stock Predictor - Mobile Client

A cross-platform React Native mobile application for the BTC Stock Predictor system. This app provides real-time market monitoring, AI-driven stock price predictions based on Bitcoin movements, and comprehensive market sentiment analysis.

## 🚀 Features

*   **Real-Time Dashboard**: Monitor live prices for BTC and correlated Bitcoin mining stocks (e.g., IREN, MARA, COIN).
*   **AI Predictions**: 
    *   **Beta Model**: Linear correlation-based price targets.
    *   **Power Law Model**: Non-linear growth projections.
*   **Market Signal Indicator**:
    *   Combines **Technical Analysis** (SMA20/SMA50 trends) with **Fundamental Analysis** (News/Social Sentiment).
    *   Provides clear Bullish/Bearish/Neutral signals with strength scores.
*   **Hybrid Data Fetching**:
    *   **Direct Mode**: Fetch prices directly from Binance (BTC) and Yahoo Finance (Stocks) for minimum latency.
    *   **Backend Mode**: Fallback to local Django backend for processed data and AI inference.
*   **Settings**: User-configurable data source toggles.

## 🛠 Tech Stack

*   **Framework**: [React Native](https://reactnative.dev/) via [Expo](https://expo.dev/)
*   **Language**: [TypeScript](https://www.typescriptlang.org/)
*   **Networking**: Axios with `Promise.allSettled` for parallel fetching
*   **Architecture**: Component-Based with Rigid Layered separation (Screens, Components, Types)

## 📂 Project Structure

```
mobile_predictor/
├── components/         # Reusable UI components
│   ├── Card.tsx        # Styled container
│   ├── MetricBox.tsx   # Key-value display
│   └── TabButton.tsx   # Navigation control
├── screens/            # Main application screens
│   ├── DashboardScreen.tsx # Real-time prices
│   ├── AnalysisScreen.tsx  # Predictions & Sentiment
│   └── SettingsScreen.tsx  # App configuration
├── constants.ts        # Global configuration (API URLs, Tickers)
├── types.ts            # TypeScript interfaces
├── App.tsx             # Main entry point & Navigation
└── package.json        # Dependencies
```

## 🚦 Getting Started

### Prerequisites

*   Node.js (LTS version recommended)
*   Expo CLI (`npm install -g expo-cli`)
*   Running backend instance (Django server)

### Installation

1.  Navigate to the mobile app directory:
    ```bash
    cd app/mobile_predictor
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

### Running the App

**Start the Expo development server:**

```bash
npx expo start
```

*   **Web**: Press `w` in the terminal to open in browser.
*   **Android**: Press `a` (requires Android Emulator or connected device).
*   **iOS**: Press `i` (requires iOS Simulator or macOS).

### Configuration

*   **API URL**: Configure `API_BASE_URL` in `constants.ts`. 
    *   Default for Android Emulator: `http://10.0.2.2:8000`
    *   Default for Web/iOS: `http://localhost:8000`
*   **Tickers**: Modify `STOCK_TICKERS` in `constants.ts` to track different assets.

## 📱 Usage

1.  **Dashboard**: View live prices. Pull down to refresh.
2.  **Analysis**: Select a stock, input a target BTC price, and click "Analyze" to see predicted prices and sentiment.
3.  **Settings**: Toggle "Direct BTC Fetch" or "Direct Stock Fetch" to bypass the backend for price data (useful for reducing latency).

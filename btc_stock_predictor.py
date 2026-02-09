import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import sys


def get_input(prompt):
    return input(prompt).strip()


def fetch_data(stock_ticker, start_date="2024-01-01"):
    print(f"Fetching data for {stock_ticker} and BTC-USD...")
    try:
        # Fetch data
        tickers = [stock_ticker, "BTC-USD"]
        data = yf.download(tickers, start=start_date, progress=False)["Close"]

        # Handle cases where data might be MultiIndex or single level
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(
                0
            )  # Keep only ticker names if 'Price' level exists

        # Ensure we have both columns (renaming if necessary or just accessing)
        # yfinance download structure varies by version.
        # Typically it returns a DataFrame with tickers as columns if multiple tickers.

        if stock_ticker not in data.columns or "BTC-USD" not in data.columns:
            # Fallback for individual downloads if bulk download structure is unexpected
            stock_data = yf.download(stock_ticker, start=start_date, progress=False)[
                "Close"
            ]
            btc_data = yf.download("BTC-USD", start=start_date, progress=False)["Close"]
            data = pd.DataFrame({stock_ticker: stock_data, "BTC-USD": btc_data})

        data = data.dropna()
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def analyze_and_predict(data, stock_ticker, predicted_btc_price):
    # Calculate Log Returns for better statistical properties
    returns = np.log(data / data.shift(1)).dropna()

    X = returns["BTC-USD"].values.reshape(-1, 1)
    y = returns[stock_ticker].values

    # 1. Calculate Beta using Linear Regression on Returns
    model = LinearRegression()
    model.fit(X, y)
    beta = model.coef_[0]
    r_squared = model.score(X, y)
    correlation = np.sqrt(r_squared) if beta > 0 else -np.sqrt(r_squared)

    # Current Prices
    current_btc_price = data["BTC-USD"].iloc[-1]
    current_stock_price = data[stock_ticker].iloc[-1]

    # 2. Prediction Calculation
    # Percent change in BTC
    btc_pct_change = (predicted_btc_price - current_btc_price) / current_btc_price

    # Predicted Stock Return = Beta * BTC Return
    predicted_stock_return = beta * btc_pct_change

    # Predicted Stock Price
    predicted_stock_price = current_stock_price * (1 + predicted_stock_return)

    # 3. Alternative: Log-Log Price Regression (Power Law)
    # ln(Stock) = a + b * ln(BTC)
    log_prices = np.log(data)
    X_log = log_prices["BTC-USD"].values.reshape(-1, 1)
    y_log = log_prices[stock_ticker].values

    price_model = LinearRegression()
    price_model.fit(X_log, y_log)
    price_beta = price_model.coef_[0]
    price_intercept = price_model.intercept_

    # Predicted Price using Log-Log model
    log_predicted_btc = np.log(predicted_btc_price)
    log_predicted_stock = price_intercept + price_beta * log_predicted_btc
    predicted_stock_price_log_model = np.exp(log_predicted_stock)

    return {
        "current_btc": current_btc_price,
        "current_stock": current_stock_price,
        "beta": beta,
        "correlation": correlation,
        "prediction_beta": predicted_stock_price,
        "prediction_log_model": predicted_stock_price_log_model,
        "price_beta": price_beta,  # Elasticity
    }


def main():
    print("--- BTC-Based Stock Price Predictor ---")

    while True:
        stock_ticker = get_input(
            "\nEnter Stock Ticker (e.g., IREN, MARA, COIN) or 'q' to quit: "
        ).upper()
        if stock_ticker == "Q":
            break

        try:
            target_btc_input = get_input("Enter Predicted Bitcoin Price (USD): ")
            target_btc_price = float(target_btc_input.replace(",", "").replace("$", ""))
        except ValueError:
            print("Invalid price. Please enter a number.")
            continue

        data = fetch_data(stock_ticker)
        if data is None or data.empty:
            print("Could not fetch data. Please check the ticker symbol.")
            continue

        results = analyze_and_predict(data, stock_ticker, target_btc_price)

        print("\n" + "=" * 40)
        print(f"Analysis for {stock_ticker} vs BTC-USD")
        print("=" * 40)
        print(f"Current BTC Price:   ${results['current_btc']:,.2f}")
        print(f"Current {stock_ticker} Price:    ${results['current_stock']:,.2f}")
        print(f"Correlation:         {results['correlation']:.2f}")
        print(f"Beta (Volatility):   {results['beta']:.2f}")
        print("-" * 40)
        print(f"Target BTC Price:    ${target_btc_price:,.2f}")
        print("-" * 40)
        print(f"Prediction (Beta Model):      ${results['prediction_beta']:,.2f}")
        print(f"Prediction (Power Law Model): ${results['prediction_log_model']:,.2f}")
        print("=" * 40)
        print("Note: Beta Model assumes linear return correlation.")
        print(
            "Power Law Model fits ln(Price) relationship (often better for large moves)."
        )


if __name__ == "__main__":
    main()

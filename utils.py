import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from sklearn.linear_model import LinearRegression
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    from transformers import pipeline

    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


@st.cache_data(ttl=3600)
def fetch_news(ticker):
    try:
        t = yf.Ticker(ticker)
        return t.news
    except Exception as e:
        return []


@st.cache_resource
def load_sentiment_model():
    if HAS_TRANSFORMERS:
        try:
            # Use FinBERT for financial sentiment
            return pipeline("sentiment-analysis", model="ProsusAI/finbert")
        except Exception as e:
            st.warning(f"Failed to load FinBERT model: {e}. Falling back to VADER.")
            return None
    return None


def analyze_sentiment(news_items):
    if not news_items:
        return 0.0, "Neutral", []

    analyzed_news = []
    scores = []

    # Load model if available
    finbert = load_sentiment_model()

    # Fallback to VADER if FinBERT is missing
    vader = SentimentIntensityAnalyzer() if not finbert else None

    for item in news_items:
        try:
            content = item.get("content", {})
            if not content:
                content = item

            title = content.get("title", "")
            summary = content.get("summary", "")
            text = f"{title}. {summary}"

            if not text.strip():
                continue

            sentiment_label = "Neutral"
            score_val = 0.0

            if finbert:
                # Truncate text to 512 tokens approx (FinBERT limit)
                result = finbert(text[:512])[0]
                label = result["label"]  # positive, negative, neutral
                score = result["score"]

                if label == "positive":
                    score_val = score
                    sentiment_label = "Bullish"
                elif label == "negative":
                    score_val = -score
                    sentiment_label = "Bearish"
                else:
                    score_val = 0
                    sentiment_label = "Neutral"
            else:
                # VADER logic
                vs = vader.polarity_scores(text)
                compound = vs["compound"]
                score_val = compound
                if compound >= 0.05:
                    sentiment_label = "Bullish"
                elif compound <= -0.05:
                    sentiment_label = "Bearish"
                else:
                    sentiment_label = "Neutral"

            scores.append(score_val)
            analyzed_news.append(
                {
                    "title": title,
                    "link": content.get("clickThroughUrl", {}).get("url", "#")
                    if content.get("clickThroughUrl")
                    else "#",
                    "provider": content.get("provider", {}).get(
                        "displayName", "Source"
                    ),
                    "date": content.get("pubDate", "")[:10],
                    "sentiment": sentiment_label,
                    "score": score_val,
                }
            )

        except Exception as e:
            continue

    if not scores:
        return 0.0, "Neutral", []

    avg_score = np.mean(scores)

    # Map final score to label
    final_label = "Neutral"
    if avg_score >= 0.1:  # Thresholds might need tuning for FinBERT vs VADER
        final_label = "Bullish" if avg_score < 0.5 else "Very Bullish"
    elif avg_score <= -0.1:
        final_label = "Bearish" if avg_score > -0.5 else "Very Bearish"

    return avg_score, final_label, analyzed_news


def fetch_binance_btc():
    """Fetches real-time BTC price from Binance Public API (No Key Required)"""
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data["price"])
    except Exception as e:
        # st.warning(f"Binance API failed: {e}")
        pass
    return None


def fetch_finnhub_price(ticker, api_key):
    """Fetches real-time stock price from Finnhub (Key Required)"""
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={api_key}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data["c"])  # 'c' is the current price
    except Exception:
        pass
    return None


@st.cache_data(ttl=10)  # Reduced cache to 10s for real-time feel
def fetch_realtime_price(ticker, finnhub_key=None):
    # 1. BTC: Try Binance first (Fastest, Free)
    if ticker == "BTC-USD":
        btc_price = fetch_binance_btc()
        if btc_price:
            return btc_price

    # 2. Stocks: Try Finnhub if key provided
    if finnhub_key and ticker != "BTC-USD":
        price = fetch_finnhub_price(ticker, finnhub_key)
        if price:
            return price

    # 3. Fallback: yfinance (Slower, potentially delayed)
    try:
        t = yf.Ticker(ticker)
        # Try fast_info first (new yfinance)
        if hasattr(t, "fast_info"):
            price = t.fast_info.get("last_price")
            if price:
                return price

        # Fallback to history
        data = t.history(period="1d")
        if not data.empty:
            return data["Close"].iloc[-1]

        return 0.0
    except Exception:
        return 0.0


@st.cache_data(ttl=3600)
def fetch_data(ticker, start_date):
    try:
        tickers = [ticker, "BTC-USD"]
        data = yf.download(tickers, start=start_date, progress=False)["Close"]

        # Handle MultiIndex if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(0)

        # Fallback if columns are missing
        if ticker not in data.columns or "BTC-USD" not in data.columns:
            # st.warning(f"Bulk download failed structure check. Retrying individually...")
            stock_data = yf.download(ticker, start=start_date, progress=False)["Close"]
            btc_data = yf.download("BTC-USD", start=start_date, progress=False)["Close"]
            data = pd.DataFrame({ticker: stock_data, "BTC-USD": btc_data})

        data = data.dropna()
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


def calculate_metrics(data, ticker):
    # Log returns
    returns = np.log(data / data.shift(1)).dropna()

    X = returns["BTC-USD"].values.reshape(-1, 1)
    y = returns[ticker].values

    # Linear Regression (Beta)
    model = LinearRegression()
    model.fit(X, y)
    beta = model.coef_[0]
    r_squared = model.score(X, y)
    correlation = np.sqrt(r_squared) if beta > 0 else -np.sqrt(r_squared)

    return beta, correlation, model


def predict_prices(
    data,
    ticker,
    target_btc,
    beta,
    event_multiplier=1.0,
    manual_current_btc=0.0,
    manual_current_stock=0.0,
):
    # Use manual/real-time BTC price if provided, otherwise fallback to last historical close
    current_btc = (
        manual_current_btc if manual_current_btc > 0 else data["BTC-USD"].iloc[-1]
    )

    # Use real-time stock price if provided, otherwise fallback to last historical close
    current_stock = (
        manual_current_stock if manual_current_stock > 0 else data[ticker].iloc[-1]
    )

    # 1. Beta Model Prediction
    btc_return = (target_btc - current_btc) / current_btc
    stock_return = beta * btc_return
    pred_beta = current_stock * (1 + stock_return)

    # Apply Event Multiplier
    pred_beta = pred_beta * event_multiplier

    # 2. Power Law (Log-Log) Model
    if target_btc <= 0:
        pred_power_law = 0.0
    else:
        log_prices = np.log(data)
        X_log = log_prices["BTC-USD"].values.reshape(-1, 1)
        y_log = log_prices[ticker].values

        log_model = LinearRegression()
        log_model.fit(X_log, y_log)

        log_target_btc = np.log(target_btc)
        log_pred_stock = log_model.predict([[log_target_btc]])[0]
        pred_power_law = np.exp(log_pred_stock)

    # Apply Event Multiplier
    pred_power_law = pred_power_law * event_multiplier

    return current_btc, current_stock, pred_beta, pred_power_law


@st.cache_data(ttl=3600)
def fetch_stocks_data(tickers, start_date):
    try:
        data = yf.download(tickers, start=start_date, progress=False)["Close"]

        # Handle MultiIndex if present (when downloading multiple stocks)
        if isinstance(data.columns, pd.MultiIndex):
            # yf.download for multiple tickers usually returns MultiIndex (Price, Ticker) or just (Ticker) if only Close.
            # 'Close' access above might strip the Price level if it was the top level.
            # But let's check. yf.download(..., group_by='ticker') vs default.
            # Default: Columns are (Price, Ticker). data['Close'] -> Columns are Tickers.
            # So data.columns should be Index([Ticker1, Ticker2, ...])
            pass

        data = data.dropna()
        return data
    except Exception as e:
        st.error(f"Error fetching bulk data: {e}")
        return None

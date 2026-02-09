import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from predictor.services import (
    fetch_news,
    analyze_sentiment,
    fetch_realtime_price,
    fetch_data,
    calculate_metrics,
    predict_prices,
    HAS_TRANSFORMERS,
)

# --- Page Config ---
st.set_page_config(page_title="BTC Stock Predictor", page_icon="📈", layout="wide")

# --- Title & Description ---
st.title("🪙 BTC-Based Stock Price Predictor")
st.markdown(
    """
    This tool predicts the price of a stock (e.g., Miners, Proxy Stocks) based on a target Bitcoin price. 
    It calculates the historical correlation and beta to estimate future moves.
"""
)

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("⚙️ Configuration")

    # Stock Selection (For News Only)
    news_tickers = ["IREN", "APLD", "HUT", "MARA", "CLSK", "COIN", "MSTR"]
    stock_ticker = st.selectbox(
        "Select Ticker for News Analysis", news_tickers, index=0
    )

    current_btc_price_ref = st.number_input(
        "Current BTC Reference (Optional)",
        value=0.0,
        help="Leave 0 to fetch live price",
    )

    st.divider()
    st.markdown("**⚡ Real-Time Data Source**")
    finnhub_api_key = st.text_input(
        "Finnhub API Key (Optional)",
        type="password",
        help="Get free key at finnhub.io for faster stock data.",
    )
    if not finnhub_api_key:
        st.caption("ℹ️ Using Binance (Free) for BTC and Yahoo (Delayed) for Stocks.")
    else:
        st.caption("✅ Using Finnhub for Real-Time Stocks!")

    target_btc_price = st.number_input(
        "Target BTC Price ($)", value=67000.0, step=1000.0, min_value=1.0
    )
    start_date = st.date_input(
        "Start Date for Analysis", value=pd.to_datetime("2024-01-01")
    )

    st.divider()

    st.subheader("📰 AI/HPC Event Impact")

    # Fetch and Analyze News
    with st.spinner("Analyzing news sentiment (AI Model)..."):
        news_items = fetch_news(stock_ticker)
        sentiment_score, sentiment_label, analyzed_news = analyze_sentiment(news_items)

    st.info(
        f"🤖 AI Sentiment Analysis: **{sentiment_label}** (Score: {sentiment_score:.2f})"
    )

    if HAS_TRANSFORMERS:
        st.caption("✅ Using FinBERT (Financial Transformers)")
    else:
        st.caption("⚠️ Using VADER (Rule-based Fallback)")

    with st.expander("View Latest News Source"):
        if analyzed_news:
            for item in analyzed_news[:5]:
                sentiment_color = (
                    "green"
                    if item["sentiment"] == "Bullish"
                    else "red"
                    if item["sentiment"] == "Bearish"
                    else "gray"
                )
                st.markdown(
                    f"**:{sentiment_color}[{item['sentiment']}]** [{item['title']}]({item['link']})"
                )
                st.caption(f"{item['provider']} • {item['date']}")
        else:
            st.caption("No recent news found.")

    event_impact = st.select_slider(
        "Adjust Sentiment Impact",
        options=["Very Bearish", "Bearish", "Neutral", "Bullish", "Very Bullish"],
        value=sentiment_label
        if sentiment_label
        in ["Very Bearish", "Bearish", "Neutral", "Bullish", "Very Bullish"]
        else "Neutral",
        help="Adjust based on recent news about AI data center contracts.",
    )

    impact_multipliers = {
        "Very Bearish": 0.70,
        "Bearish": 0.85,
        "Neutral": 1.0,
        "Bullish": 1.15,
        "Very Bullish": 1.30,
    }

    # Map "Positive" to "Bullish" for slider compatibility if needed
    if event_impact == "Positive":
        event_impact = "Bullish"

    event_multiplier = impact_multipliers.get(event_impact, 1.0)

    st.divider()
    st.caption("Powered by Yahoo Finance & Scikit-Learn")

# --- Real-Time Dashboard ---
st.subheader("⚡ Real-Time Market Prices")
market_tickers = ["BTC-USD", "IREN", "APLD", "HUT", "MARA", "CLSK", "COIN", "MSTR"]
cols = st.columns(4)

for i, ticker in enumerate(market_tickers):
    price = fetch_realtime_price(ticker, finnhub_api_key)
    with cols[i % 4]:
        st.metric(label=ticker, value=f"${price:,.2f}" if price else "N/A")

st.divider()

# --- Main Execution ---
st.header("📊 Detailed Stock Analysis")

analysis_tickers = ["IREN", "APLD", "HUT", "MARA", "CLSK", "COIN", "MSTR"]
real_time_btc = fetch_realtime_price("BTC-USD", finnhub_api_key)

for ticker in analysis_tickers:
    st.markdown(f"### 🪙 {ticker}")

    with st.spinner(f"Analyzing {ticker}..."):
        data = fetch_data(ticker, start_date)

        # Fetch Real-time Stock Price
        real_time_stock = fetch_realtime_price(ticker, finnhub_api_key)

        # Determine which BTC price to use (Manual Override > Real-time > Historical Last Close)
        if current_btc_price_ref > 0:
            used_btc_price = current_btc_price_ref
        elif real_time_btc > 0:
            used_btc_price = real_time_btc
        elif data is not None and not data.empty:
            used_btc_price = data["BTC-USD"].iloc[-1]
        else:
            used_btc_price = 0.0

        # Determine which Stock price to use (Real-time > Historical Last Close)
        if real_time_stock > 0:
            used_stock_price = real_time_stock
        elif data is not None and not data.empty:
            used_stock_price = data[ticker].iloc[-1]
        else:
            used_stock_price = 0.0

        if data is not None and not data.empty:
            # Perform Calculations
            beta, correlation, beta_model = calculate_metrics(data, ticker)
            current_btc, current_stock, pred_beta, pred_power_law = predict_prices(
                data,
                ticker,
                target_btc_price,
                beta,
                event_multiplier,
                manual_current_btc=used_btc_price,
                manual_current_stock=used_stock_price,
            )

            # --- Display Metrics ---
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Current BTC Price",
                    f"${current_btc:,.2f}",
                    delta=f"{((current_btc - data['BTC-USD'].iloc[-2])/data['BTC-USD'].iloc[-2]*100):.2f}%",
                )
            with col2:
                st.metric(
                    f"Current {ticker} Price",
                    f"${current_stock:,.2f}",
                    delta=f"{((current_stock - data[ticker].iloc[-2])/data[ticker].iloc[-2]*100):.2f}%",
                )
            with col3:
                st.metric(
                    "Beta (Volatility)",
                    f"{beta:.2f}",
                    help="How much the stock moves relative to BTC. >1 means more volatile.",
                )
            with col4:
                st.metric(
                    "Correlation",
                    f"{correlation:.2f}",
                    help="1.0 is perfect correlation. 0.0 is no correlation.",
                )

            # --- Display Predictions ---
            st.caption(f"🔮 Price Prediction at BTC ${target_btc_price:,.0f}")

            p_col1, p_col2 = st.columns(2)

            with p_col1:
                st.info(
                    f"**Beta Model Prediction:**\n# ${pred_beta:,.2f} ({((pred_beta - current_stock)/current_stock*100):.1f}%)"
                )

            with p_col2:
                st.success(
                    f"**Power Law (Log-Log) Prediction:**\n# ${pred_power_law:,.2f}"
                )

            # --- Visualizations ---
            with st.expander(f"📈 View Charts for {ticker}", expanded=False):
                tab1, tab2 = st.tabs(["Regression Analysis", "Price History"])

                with tab1:
                    # Scatter Plot with Regression Line
                    fig = px.scatter(
                        data,
                        x="BTC-USD",
                        y=ticker,
                        title=f"{ticker} vs BTC Price Correlation",
                        trendline="ols",
                        opacity=0.6,
                    )
                    # Add the target point
                    fig.add_trace(
                        go.Scatter(
                            x=[target_btc_price],
                            y=[pred_beta],
                            mode="markers+text",
                            marker=dict(color="red", size=15, symbol="star"),
                            name="Beta Prediction",
                            text=[f"Beta: ${pred_beta:.0f}"],
                            textposition="top center",
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=[target_btc_price],
                            y=[pred_power_law],
                            mode="markers+text",
                            marker=dict(color="green", size=15, symbol="star"),
                            name="Power Law Prediction",
                            text=[f"Power: ${pred_power_law:.0f}"],
                            textposition="bottom center",
                        )
                    )
                    st.plotly_chart(fig, width="stretch", key=f"scatter_{ticker}")

                with tab2:
                    # Normalized Price History
                    norm_data = data / data.iloc[0] * 100
                    fig2 = px.line(
                        norm_data, title="Normalized Price History (Base=100)"
                    )
                    st.plotly_chart(fig2, width="stretch", key=f"history_{ticker}")

        else:
            st.error(f"No data found for {ticker}.")

    st.divider()

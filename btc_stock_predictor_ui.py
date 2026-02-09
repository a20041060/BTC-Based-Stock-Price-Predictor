import streamlit as st
import pandas as pd
from datetime import datetime
from predictor.core.config import settings
from predictor.core.logger import get_logger
from predictor.infrastructure.market_data import MarketDataProvider
from predictor.infrastructure.sentiment_analysis import SentimentAnalyzer
from predictor.infrastructure.social_media_scraper import NitterScraperProvider
from predictor.application.prediction_service import PredictionService

# --- Initialize Dependencies ---
logger = get_logger("streamlit_app")

# Dependency Injection with Caching
@st.cache_resource
def get_prediction_service():
    market_data_provider = MarketDataProvider()
    sentiment_analyzer = SentimentAnalyzer()
    social_media_provider = NitterScraperProvider()
    return PredictionService(market_data_provider, sentiment_analyzer, social_media_provider)

prediction_service = get_prediction_service()
market_data_provider = prediction_service.market_data # Access for direct calls if needed

# --- Page Config ---
st.set_page_config(page_title=settings.APP_NAME, page_icon="📈", layout="wide")

# --- Title & Description ---
st.title(f"🪙 {settings.APP_NAME}")
st.markdown(
    """
    This tool predicts the price of a stock (e.g., Miners, Proxy Stocks) based on a target Bitcoin price. 
    It calculates the historical correlation and beta to estimate future moves.
    """
)

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("⚙️ Configuration")

    # Dark Mode Toggle
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True

    is_dark_mode = st.toggle("Dark Mode 🌙", key="dark_mode")
    if is_dark_mode:
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            section[data-testid="stSidebar"] {
                background-color: #262730;
                color: #FAFAFA;
            }
            /* Sidebar Nav Title/Links */
            div[data-testid="stSidebarNav"] a, div[data-testid="stSidebarNav"] span {
                color: #FAFAFA !important;
            }
            /* Top Header (fix white edge) */
            header[data-testid="stHeader"] {
                background-color: #0E1117;
            }
            /* Cards/Containers overrides might be needed */
            div[data-testid="stMetricValue"] {
                color: #FAFAFA;
            }
            /* Widget Labels */
            div[data-testid="stWidgetLabel"] p {
                color: #FAFAFA !important;
            }
            /* Metric Labels */
            div[data-testid="stMetricLabel"] p {
                 color: #FAFAFA !important;
            }
            div[data-testid="stMetricLabel"] label {
                 color: #FAFAFA !important;
            }
             /* Markdown Text */
            div[data-testid="stMarkdownContainer"] p {
                 color: #FAFAFA;
            }
             /* Headers */
            h1, h2, h3, h4, h5, h6 {
                color: #FAFAFA !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
         st.markdown(
            """
            <style>
            .stApp {
                background-color: #FFFFFF;
                color: #000000;
            }
            section[data-testid="stSidebar"] {
                background-color: #F0F2F6;
                color: #000000;
            }
            div[data-testid="stMetricValue"] {
                color: #000000;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

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
    
    # Update settings if user provides key (Note: In a real rigid app, we might avoid modifying global settings like this, 
    # but for Streamlit interaction it's a necessary compromise or we pass it to the provider method)
    finnhub_api_key_input = st.text_input(
        "Finnhub API Key (Optional)",
        type="password",
        help="Get free key at finnhub.io for faster stock data.",
    )
    
    if finnhub_api_key_input:
        settings.FINNHUB_API_KEY = finnhub_api_key_input
        st.caption("✅ Using Finnhub for Real-Time Stocks!")
    else:
        st.caption("ℹ️ Using Binance (Free) for BTC and Yahoo (Delayed) for Stocks.")

    target_btc_price = st.number_input(
        "Target BTC Price ($)", value=70500.0, step=1000.0, min_value=1.0
    )
    
    start_date_input = st.date_input(
        "Start Date for Analysis", value=pd.to_datetime("2024-01-01")
    )
    # Ensure start_date is datetime
    start_date = pd.to_datetime(start_date_input)

    st.divider()

    st.subheader("📰 AI/HPC Event Impact")

    # Fetch and Analyze News
    with st.spinner("Analyzing news sentiment (AI Model)..."):
        sentiment_result = prediction_service.get_market_sentiment(stock_ticker)
        
    # --- Market Signal Display ---
    if hasattr(sentiment_result, 'composite_label') and sentiment_result.composite_label:
        st.subheader("🚦 Market Signal (Trend + News)")
        
        # Determine Color
        comp_color = "green" if "Bullish" in sentiment_result.composite_label else "red" if "Bearish" in sentiment_result.composite_label else "orange"
        
        st.markdown(
            f"<h2 style='text-align: center; color: {comp_color};'>{sentiment_result.composite_label.upper()}</h2>", 
            unsafe_allow_html=True
        )
        st.caption(f"Composite Signal Strength: {sentiment_result.composite_score:.2f}")

        # Breakdown
        s_col1, s_col2 = st.columns(2)
        with s_col1:
            trend_color = "normal"
            if "Bullish" in sentiment_result.trend_label: trend_color = "normal" # metric handles green automatically for positive delta? No, delta color depends on value.
            # actually st.metric delta color is good enough
            st.metric("Price Trend", sentiment_result.trend_label, delta=f"{sentiment_result.trend_score:.2f}")
        with s_col2:
            st.metric("News Sentiment", sentiment_result.label, delta=f"{sentiment_result.score:.2f}")
            
    else:
        st.info(
            f"🤖 AI Sentiment Analysis: **{sentiment_result.label}** (Score: {sentiment_result.score:.2f})"
        )

    if settings.USE_TRANSFORMERS:
        st.caption("✅ Using FinBERT (Financial Transformers)")
    else:
        st.caption("⚠️ Using VADER (Rule-based Fallback)")

    with st.expander("View Latest News & Social"):
        if sentiment_result.analyzed_items:
            for item in sentiment_result.analyzed_items[:10]:
                sentiment_color = (
                    "green"
                    if item["sentiment"] in ["Bullish", "Very Bullish"]
                    else "red"
                    if item["sentiment"] == "Bearish"
                    else "gray"
                )
                
                if item.get("type") == "news":
                     st.markdown(
                        f"**{item['title']}** ({item['provider']}) - :{sentiment_color}[{item['sentiment']}]"
                    )
                     st.caption(f"[Link]({item['link']}) | {item['date']}")
                elif item.get("type") == "social":
                    platform_label = item.get('platform', 'X.com')
                    if "Simulated" in platform_label:
                        st.warning(f"⚠️ Scraping Failed - Using {platform_label}")
                    
                    st.markdown(
                        f"**@{item.get('author', 'unknown')} ({platform_label})** - :{sentiment_color}[{item['sentiment']}]"
                    )
                    st.markdown(f"> {item.get('content', '')}")
                    st.caption(f"[Link]({item.get('url', '#')}) | {item.get('date', '')}")
                
                st.divider()
        else:
            st.caption("No recent news or social posts found.")

    event_impact = st.select_slider(
        "Adjust Sentiment Impact",
        options=["Very Bearish", "Bearish", "Neutral", "Bullish", "Very Bullish"],
        value=sentiment_result.label
        if sentiment_result.label
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

    event_multiplier = impact_multipliers.get(event_impact, 1.0)

    st.divider()
    st.caption("Powered by Yahoo Finance & Scikit-Learn")

# --- Real-Time Dashboard ---
st.subheader("⚡ Real-Time Market Prices")
market_tickers = ["BTC-USD", "IREN", "APLD", "HUT", "MARA", "CLSK", "COIN", "MSTR"]
cols = st.columns(4)

for i, ticker in enumerate(market_tickers):
    info = market_data_provider.get_extended_stock_info(ticker)
        
    with cols[i % 4]:
        if not info or info.get("price") is None:
            st.metric(label=ticker, value="N/A")
        else:
            price = info.get("price")
            st.metric(label=ticker, value=f"${price:,.2f}")
            
            # Show Extended Hours if Market is NOT Open
            market_state = info.get("market_state")
            if market_state != "OPEN":
                pre_price = info.get("pre_market_price")
                post_price = info.get("post_market_price")
                
                # Logic: Show relevant extended hours prices
                if market_state == "PRE":
                    if pre_price: st.caption(f"🌑 Pre-Market: ${pre_price:,.2f}")
                elif market_state == "POST":
                    if post_price: st.caption(f"🌑 After-Market: ${post_price:,.2f}")
                else: # CLOSED
                    if pre_price: st.caption(f"🌑 Pre-Market: ${pre_price:,.2f}")
                    if post_price: st.caption(f"🌑 After-Market: ${post_price:,.2f}")

st.divider()

# --- Main Execution ---
st.header("📊 Detailed Stock Analysis")

analysis_tickers = ["IREN", "APLD", "HUT", "MARA", "CLSK", "COIN", "MSTR"]

for ticker in analysis_tickers:
    st.markdown(f"### 🪙 {ticker}")

    with st.spinner(f"Analyzing {ticker}..."):
        result = prediction_service.predict_price(
            ticker=ticker,
            target_btc_price=target_btc_price,
            start_date=start_date,
            event_impact_multiplier=event_multiplier,
            manual_current_btc=current_btc_price_ref
        )

        if result:
            # --- Display Metrics ---
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Current BTC Price",
                    f"${result.current_btc_price:,.2f}"
                )
            with col2:
                st.metric(
                    f"Current {ticker} Price",
                    f"${result.current_stock_price:,.2f}"
                )
            with col3:
                st.metric(
                    "Beta (Volatility)",
                    f"{result.beta:.2f}",
                    help="Measure of how much the stock moves relative to BTC."
                )
            with col4:
                st.metric(
                    "Correlation",
                    f"{result.correlation:.2f}",
                    help="Correlation between stock and BTC returns."
                )

            # --- Prediction Display ---
            st.success(
                f"🎯 **Prediction for {ticker} at BTC ${target_btc_price:,.0f}**"
            )
            
            p_col1, p_col2 = st.columns(2)
            
            with p_col1:
                st.metric(
                    label="Based on Beta (Linear)",
                    value=f"${result.predicted_stock_price_beta:.2f}",
                    delta=f"{((result.predicted_stock_price_beta - result.current_stock_price) / result.current_stock_price * 100):.1f}% Potential"
                )
                
            with p_col2:
                st.metric(
                    label="Based on Power Law (Log-Log)",
                    value=f"${result.predicted_stock_price_power_law:.2f}",
                    delta=f"{((result.predicted_stock_price_power_law - result.current_stock_price) / result.current_stock_price * 100):.1f}% Potential"
                )

        else:
            st.warning(f"Insufficient data to analyze {ticker}")

    st.divider()

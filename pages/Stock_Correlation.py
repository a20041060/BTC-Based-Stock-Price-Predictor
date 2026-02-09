import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from predictor.services import fetch_stocks_data

st.set_page_config(
    page_title="Stock Correlation Analysis", page_icon="🔗", layout="wide"
)

st.title("🔗 Stock-to-Stock Correlation Analysis")
st.markdown("Analyze how different miners and proxy stocks correlate with each other.")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")

    available_tickers = [
        "BTC-USD",
        "IREN",
        "APLD",
        "HUT",
        "MARA",
        "CLSK",
        "COIN",
        "MSTR",
    ]
    selected_tickers = st.multiselect(
        "Select Assets to Correlate",
        available_tickers,
        default=["IREN", "HUT", "MARA", "CLSK", "COIN"],
    )

    start_date = st.date_input("Start Date", value=pd.to_datetime("2024-01-01"))

    st.divider()
    st.caption("Powered by Yahoo Finance")

if len(selected_tickers) < 2:
    st.warning("Please select at least 2 assets to analyze correlation.")
    st.stop()

# --- Fetch Data ---
with st.spinner("Fetching data..."):
    data = fetch_stocks_data(selected_tickers, start_date)

if data is None or data.empty:
    st.error(
        "Failed to fetch data. Please check your internet connection or try different tickers."
    )
    st.stop()

# Clean Data: Drop columns with all NaNs if any
data = data.dropna(axis=1, how="all")
data = data.dropna()  # Drop rows with any NaNs (alignment)

if data.shape[1] < 2:
    st.error(
        "Not enough data available for correlation analysis (less than 2 valid assets fetched)."
    )
    st.stop()

# Calculate Returns (Log Returns for better statistical properties)
returns = np.log(data / data.shift(1)).dropna()

# --- Correlation Matrix ---
st.subheader("🔥 Correlation Heatmap")
corr_matrix = returns.corr()

fig_corr = px.imshow(
    corr_matrix,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    title="Daily Returns Correlation Matrix",
)
st.plotly_chart(fig_corr, width="stretch")

st.divider()

# --- Pairwise Analysis ---
st.subheader("⚖️ Pairwise Deep Dive")

col1, col2 = st.columns(2)
with col1:
    # Filter selected_tickers to those actually in data columns
    valid_tickers = [t for t in selected_tickers if t in data.columns]
    if not valid_tickers:
        st.stop()

    asset_x = st.selectbox("Select X-Axis Asset", valid_tickers, index=0)

with col2:
    # Default to second asset if available
    default_y_index = 1 if len(valid_tickers) > 1 else 0
    asset_y = st.selectbox("Select Y-Axis Asset", valid_tickers, index=default_y_index)

if asset_x == asset_y:
    st.info("Select different assets to see correlation.")
else:
    # Scatter Plot
    fig_scatter = px.scatter(
        data,
        x=asset_x,
        y=asset_y,
        title=f"{asset_y} vs {asset_x} Price Correlation",
        trendline="ols",
        opacity=0.6,
        hover_data=[data.index],
    )

    # Calculate specific correlation
    pair_corr = returns[asset_x].corr(returns[asset_y])

    st.plotly_chart(fig_scatter, width="stretch")

    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric(f"Correlation: {asset_x} vs {asset_y}", f"{pair_corr:.2f}")

    # Rolling Correlation
    st.markdown("### 🔄 Rolling Correlation (30-Day Window)")
    rolling_corr = returns[asset_x].rolling(window=30).corr(returns[asset_y])

    fig_rolling = px.line(
        rolling_corr,
        title=f"30-Day Rolling Correlation: {asset_x} vs {asset_y}",
        labels={"value": "Correlation", "index": "Date"},
    )
    # Add zero line
    fig_rolling.add_hline(y=0, line_dash="dash", line_color="gray")

    st.plotly_chart(fig_rolling, width="stretch")

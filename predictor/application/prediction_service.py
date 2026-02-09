import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Tuple, Optional
from datetime import datetime
import pandas as pd

from predictor.interfaces.market_data_provider import IMarketDataProvider
from predictor.interfaces.sentiment_analyzer import ISentimentAnalyzer
from predictor.interfaces.social_media_provider import ISocialMediaProvider
from predictor.domain.models import PredictionResult, SentimentResult, NewsItem
from predictor.core.logger import get_logger

logger = get_logger(__name__)

class PredictionService:
    def __init__(
        self, 
        market_data_provider: IMarketDataProvider,
        sentiment_analyzer: ISentimentAnalyzer,
        social_media_provider: Optional[ISocialMediaProvider] = None
    ):
        self.market_data = market_data_provider
        self.sentiment_analyzer = sentiment_analyzer
        self.social_media_provider = social_media_provider

    def get_market_sentiment(self, ticker: str) -> SentimentResult:
        logger.info(f"Analyzing sentiment for {ticker}")
        
        items = []
        
        # Get News
        try:
            news_items = self.market_data.get_news(ticker)
            items.extend(news_items)
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            
        # Get Social Posts
        if self.social_media_provider:
            try:
                # Search for ticker with $ prefix (common in finance twitter)
                # and maybe company name if we had it, but ticker is good start
                # Limiting to 5-10 posts per query to be fast
                posts = self.social_media_provider.get_posts(f"${ticker}", limit=10)
                items.extend(posts)
            except Exception as e:
                logger.error(f"Error fetching social posts for {ticker}: {e}")
        
        # 1. Analyze News/Social Sentiment
        base_result = self.sentiment_analyzer.analyze(items)
        
        # 2. Analyze Price Trend
        trend_data = self._analyze_price_trend(ticker)
        
        # 3. Combine Scores (50% Sentiment, 50% Trend)
        composite_score = (base_result.score * 0.5) + (trend_data['score'] * 0.5)
        
        composite_label = "Neutral"
        if composite_score > 0.2: 
            composite_label = "Bullish"
        elif composite_score < -0.2: 
            composite_label = "Bearish"
            
        return SentimentResult(
            score=base_result.score,
            label=base_result.label,
            trend_score=trend_data['score'],
            trend_label=trend_data['label'],
            composite_score=composite_score,
            composite_label=composite_label,
            analyzed_items=base_result.analyzed_items
        )

    def _analyze_price_trend(self, ticker: str) -> dict:
        try:
            # Fetch last 150 days to ensure we have enough for SMA50
            end_date = datetime.now()
            start_date = end_date - pd.Timedelta(days=150)
            
            data = self.market_data.get_historical_data(ticker, start_date.strftime("%Y-%m-%d"))
            
            if data.empty or len(data) < 50:
                return {"label": "Neutral", "score": 0.0}

            prices = data[ticker]
            
            # Get latest available data
            current_price = prices.iloc[-1]
            
            # Calculate SMAs
            sma_20 = prices.rolling(window=20).mean().iloc[-1]
            sma_50 = prices.rolling(window=50).mean().iloc[-1]
            
            # Score Calculation (-1 to 1)
            score = 0.0
            
            # Price vs SMA20 (Short term momentum)
            if current_price > sma_20: 
                score += 0.5
            else: 
                score -= 0.5
            
            # SMA20 vs SMA50 (Medium term trend)
            if sma_20 > sma_50: 
                score += 0.5
            else: 
                score -= 0.5
            
            # Label
            label = "Neutral"
            if score >= 0.5: 
                label = "Bullish"
            elif score <= -0.5: 
                label = "Bearish"
            
            return {"label": label, "score": score}
            
        except Exception as e:
            logger.error(f"Error analyzing price trend for {ticker}: {e}")
            return {"label": "Neutral", "score": 0.0}

    def predict_price(
        self,
        ticker: str,
        target_btc_price: float,
        start_date: datetime,
        event_impact_multiplier: float = 1.0,
        manual_current_btc: float = 0.0,
        manual_current_stock: float = 0.0
    ) -> Optional[PredictionResult]:
        
        # 1. Fetch Historical Data
        data = self.market_data.get_historical_data(ticker, start_date.strftime("%Y-%m-%d"))
        if data.empty or len(data) < 10:
            logger.warning("Insufficient data for prediction")
            return None

        # 2. Calculate Beta and Correlation
        returns = np.log(data / data.shift(1)).dropna()
        X = returns["BTC-USD"].values.reshape(-1, 1)
        y = returns[ticker].values

        model = LinearRegression()
        model.fit(X, y)
        beta = float(model.coef_[0])
        r_squared = model.score(X, y)
        correlation = float(np.sqrt(r_squared) if beta > 0 else -np.sqrt(r_squared))

        # 3. Determine Current Prices
        # Prefer manual input -> then realtime -> then last historical close
        current_btc = manual_current_btc
        if current_btc <= 0:
            current_btc = self.market_data.get_realtime_btc_price() or data["BTC-USD"].iloc[-1]
            
        current_stock = manual_current_stock
        if current_stock <= 0:
            current_stock = self.market_data.get_realtime_stock_price(ticker) or data[ticker].iloc[-1]

        # 4. Beta Model Prediction
        btc_return = (target_btc_price - current_btc) / current_btc
        stock_return = beta * btc_return
        pred_beta = current_stock * (1 + stock_return)
        pred_beta *= event_impact_multiplier

        # 5. Power Law (Log-Log) Model Prediction
        pred_power_law = 0.0
        if target_btc_price > 0:
            log_prices = np.log(data)
            X_log = log_prices["BTC-USD"].values.reshape(-1, 1)
            y_log = log_prices[ticker].values
            
            log_model = LinearRegression()
            log_model.fit(X_log, y_log)
            
            log_target_btc = np.log(target_btc_price)
            log_pred_stock = log_model.predict([[log_target_btc]])[0]
            pred_power_law = float(np.exp(log_pred_stock))
            pred_power_law *= event_impact_multiplier

        return PredictionResult(
            current_btc_price=current_btc,
            current_stock_price=current_stock,
            predicted_stock_price_beta=pred_beta,
            predicted_stock_price_power_law=pred_power_law,
            beta=beta,
            correlation=correlation
        )
    
    def get_chart_data(self, ticker: str, start_date: datetime) -> pd.DataFrame:
        return self.market_data.get_historical_data(ticker, start_date.strftime("%Y-%m-%d"))

    def get_correlation_data(self, tickers: list[str], start_date: datetime) -> pd.DataFrame:
        return self.market_data.get_multiple_historical_data(tickers, start_date.strftime("%Y-%m-%d"))

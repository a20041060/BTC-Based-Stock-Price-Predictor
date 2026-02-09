import logging
import numpy as np
from typing import List, Optional, Any, Union
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from predictor.interfaces.sentiment_analyzer import ISentimentAnalyzer
from predictor.domain.models import NewsItem, SocialPost, SentimentResult
from predictor.core.config import settings
from predictor.core.logger import get_logger

logger = get_logger(__name__)

class SentimentAnalyzer(ISentimentAnalyzer):
    def __init__(self):
        self.finbert_pipeline = None
        self.vader_analyzer = SentimentIntensityAnalyzer()
        if settings.USE_TRANSFORMERS:
            self._load_finbert()

    def _load_finbert(self):
        try:
            from transformers import pipeline
            self.finbert_pipeline = pipeline("sentiment-analysis", model=settings.TRANSFORMER_MODEL)
            logger.info("FinBERT model loaded successfully.")
        except ImportError:
            logger.warning("Transformers library not found. Falling back to VADER.")
        except Exception as e:
            logger.warning(f"Failed to load FinBERT model: {e}. Falling back to VADER.")

    def analyze(self, items: List[Union[NewsItem, SocialPost]]) -> SentimentResult:
        if not items:
            return SentimentResult(score=0.0, label="Neutral", analyzed_items=[])

        scores = []
        analyzed_items_data = []

        for item in items:
            text = ""
            if isinstance(item, NewsItem):
                text = f"{item.title}. {item.summary or ''}"
            elif isinstance(item, SocialPost):
                text = item.content
            
            if not text.strip():
                continue

            score_val = 0.0
            label = "Neutral"

            if self.finbert_pipeline:
                try:
                    # Truncate to 512 chars approx for safety
                    result = self.finbert_pipeline(text[:512])[0]
                    bert_label = result["label"]
                    bert_score = result["score"]

                    if bert_label == "positive":
                        score_val = bert_score
                        label = "Bullish"
                    elif bert_label == "negative":
                        score_val = -bert_score
                        label = "Bearish"
                    else:
                        score_val = 0
                        label = "Neutral"
                except Exception as e:
                    logger.error(f"FinBERT error: {e}")
                    # Fallback to VADER for this item
                    score_val, label = self._analyze_vader(text)
            else:
                score_val, label = self._analyze_vader(text)

            scores.append(score_val)
            
            item_data = {
                "sentiment": label,
                "score": score_val
            }
            
            if isinstance(item, NewsItem):
                item_data.update({
                    "title": item.title,
                    "link": item.link,
                    "provider": item.provider,
                    "date": item.date,
                    "type": "news"
                })
            elif isinstance(item, SocialPost):
                item_data.update({
                    "content": item.content,
                    "author": item.author,
                    "url": item.url,
                    "date": item.date.isoformat() if hasattr(item.date, 'isoformat') else str(item.date),
                    "platform": item.platform,
                    "type": "social"
                })
            
            analyzed_items_data.append(item_data)

        if not scores:
            return SentimentResult(score=0.0, label="Neutral", analyzed_items=[])

        avg_score = float(np.mean(scores))
        final_label = self._get_label_from_score(avg_score)

        return SentimentResult(
            score=avg_score,
            label=final_label,
            analyzed_items=analyzed_items_data
        )

    def _analyze_vader(self, text: str):
        vs = self.vader_analyzer.polarity_scores(text)
        compound = vs["compound"]
        if compound >= 0.05:
            return compound, "Bullish"
        elif compound <= -0.05:
            return compound, "Bearish"
        return 0.0, "Neutral"

    def _get_label_from_score(self, score: float) -> str:
        if score >= 0.1:
            return "Bullish" if score < 0.5 else "Very Bullish"
        elif score <= -0.1:
            return "Bearish" if score > -0.5 else "Very Bearish"
        return "Neutral"

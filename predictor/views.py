from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import datetime
import pandas as pd
from predictor.infrastructure.market_data import MarketDataProvider
from predictor.infrastructure.sentiment_analysis import SentimentAnalyzer
from predictor.infrastructure.social_media_scraper import NitterScraperProvider
from predictor.application.prediction_service import PredictionService

# Initialize dependencies (Could be done in apps.py or using a DI container)
market_data_provider = MarketDataProvider()
sentiment_analyzer = SentimentAnalyzer()
social_media_provider = NitterScraperProvider()
prediction_service = PredictionService(market_data_provider, sentiment_analyzer, social_media_provider)

@require_http_methods(["GET"])
def api_predict(request):
    """API endpoint for price prediction."""
    try:
        ticker = request.GET.get('ticker', 'IREN')
        target_btc = float(request.GET.get('target_btc', 100000.0))
        event_multiplier = float(request.GET.get('event_multiplier', 1.0))
        start_date_str = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')

        result = prediction_service.predict_price(
            ticker=ticker,
            target_btc_price=target_btc,
            start_date=start_date,
            event_impact_multiplier=event_multiplier
        )

        if not result:
            return JsonResponse({'error': 'Prediction failed or insufficient data'}, status=400)

        return JsonResponse({
            'ticker': ticker,
            'current_btc_price': result.current_btc_price,
            'current_stock_price': result.current_stock_price,
            'predicted_stock_price_beta': result.predicted_stock_price_beta,
            'predicted_stock_price_power_law': result.predicted_stock_price_power_law,
            'beta': result.beta,
            'correlation': result.correlation
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def api_sentiment(request):
    """API endpoint for sentiment analysis."""
    try:
        ticker = request.GET.get('ticker', 'IREN')
        sentiment_result = prediction_service.get_market_sentiment(ticker)
        
        # Serialize analyzed items
        items_data = []
        if sentiment_result.analyzed_items:
            items_data = sentiment_result.analyzed_items

        return JsonResponse({
            'ticker': ticker,
            'score': sentiment_result.score,
            'label': sentiment_result.label,
            'trend_score': sentiment_result.trend_score,
            'trend_label': sentiment_result.trend_label,
            'composite_score': sentiment_result.composite_score,
            'composite_label': sentiment_result.composite_label,
            'items': items_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def api_market_prices(request):
    """API endpoint for real-time market prices."""
    try:
        tickers_param = request.GET.get('tickers', 'BTC-USD,IREN,APLD,HUT,MARA,CLSK,COIN,MSTR')
        tickers = [t.strip() for t in tickers_param.split(',')]
        
        prices = {}
        for ticker in tickers:
            if ticker == "BTC-USD":
                price = market_data_provider.get_realtime_btc_price()
            else:
                price = market_data_provider.get_realtime_stock_price(ticker)
            prices[ticker] = price
            
        return JsonResponse({'prices': prices})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def index(request):
    # Default values
    ticker = request.GET.get('ticker', 'IREN')
    target_btc = float(request.GET.get('target_btc', 100000.0))
    event_multiplier = float(request.GET.get('event_multiplier', 1.0))
    start_date_str = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    
    # Context data
    context = {
        'ticker': ticker,
        'target_btc': target_btc,
        'event_multiplier': event_multiplier,
        'start_date': start_date_str,
    }

    if request.method == 'POST':
        # Handle form submission if needed, but GET is fine for search/filter
        pass

    # Use PredictionService
    result = prediction_service.predict_price(
        ticker=ticker,
        target_btc_price=target_btc,
        start_date=start_date,
        event_impact_multiplier=event_multiplier
    )
    
    if result:
        context.update({
            'beta': round(result.beta, 2),
            'correlation': round(result.correlation, 2),
            'current_btc': round(result.current_btc_price, 2),
            'current_stock': round(result.current_stock_price, 2),
            'pred_beta': round(result.predicted_stock_price_beta, 2),
            'pred_power_law': round(result.predicted_stock_price_power_law, 2),
        })

    return render(request, 'predictor/index.html', context)

def correlation(request):
    # Default tickers
    default_tickers = ["IREN", "MARA", "RIOT", "CLSK", "HUT", "WULF", "CIFR", "BTBT",  "CORZ", "MSTR", "COIN"]
    selected_tickers = request.GET.getlist('tickers', default_tickers)
    start_date_str = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    
    context = {
        'selected_tickers': selected_tickers,
    }
    
    data = prediction_service.get_correlation_data(selected_tickers, start_date)
    
    if data is not None and not data.empty:
        corr_matrix = data.corr()
        # Convert to list of lists or dict for template rendering/JS
        # For simplicity, passing the matrix as HTML table or similar
        context['corr_matrix'] = corr_matrix.to_html(classes="table table-striped")
    
    return render(request, 'predictor/correlation.html', context)

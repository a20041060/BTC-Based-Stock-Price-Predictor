from django.shortcuts import render
from django.http import JsonResponse
from .services import (
    fetch_data,
    calculate_metrics,
    predict_prices,
    fetch_realtime_price,
    fetch_news,
    analyze_sentiment,
    fetch_stocks_data
)
import datetime
import pandas as pd

def index(request):
    # Default values
    ticker = request.GET.get('ticker', 'IREN')
    target_btc = float(request.GET.get('target_btc', 100000.0))
    event_multiplier = float(request.GET.get('event_multiplier', 1.0))
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    
    # Context data
    context = {
        'ticker': ticker,
        'target_btc': target_btc,
        'event_multiplier': event_multiplier,
        'start_date': start_date,
    }

    if request.method == 'POST':
        # Handle form submission if needed, but GET is fine for search/filter
        pass

    # Fetch Data
    data = fetch_data(ticker, start_date)
    
    if data is not None and not data.empty:
        # Calculate Metrics
        beta, correlation, _ = calculate_metrics(data, ticker)
        
        # Real-time prices
        current_btc_realtime = fetch_realtime_price("BTC-USD")
        current_stock_realtime = fetch_realtime_price(ticker)
        
        # Predictions
        current_btc, current_stock, pred_beta, pred_power_law = predict_prices(
            data, ticker, target_btc, beta, event_multiplier, 
            manual_current_btc=current_btc_realtime,
            manual_current_stock=current_stock_realtime
        )
        
        context.update({
            'beta': round(beta, 2),
            'correlation': round(correlation, 2),
            'current_btc': round(current_btc, 2),
            'current_stock': round(current_stock, 2),
            'pred_beta': round(pred_beta, 2),
            'pred_power_law': round(pred_power_law, 2),
        })

    return render(request, 'predictor/index.html', context)

def correlation(request):
    # Default tickers
    default_tickers = ["IREN", "MARA", "RIOT", "CLSK", "HUT", "WULF", "CIFR", "BTBT",  "CORZ", "MSTR", "COIN"]
    selected_tickers = request.GET.getlist('tickers', default_tickers)
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    
    data = fetch_stocks_data(selected_tickers, start_date)
    
    context = {
        'selected_tickers': selected_tickers,
    }
    
    if data is not None and not data.empty:
        corr_matrix = data.corr()
        # Convert to list of lists or dict for template rendering/JS
        # For simplicity, passing the matrix as HTML table or similar
        context['corr_matrix'] = corr_matrix.to_html(classes="table table-striped")
    
    return render(request, 'predictor/correlation.html', context)

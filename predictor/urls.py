from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('correlation/', views.correlation, name='correlation'),
    path('api/predict/', views.api_predict, name='api_predict'),
    path('api/sentiment/', views.api_sentiment, name='api_sentiment'),
    path('api/market-prices/', views.api_market_prices, name='api_market_prices'),
]

import os
import django
from django.urls import resolve, reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc_backend.settings")
django.setup()

print("--- Debugging URLs ---")
try:
    match = resolve('/api/market-prices/')
    print(f"Resolved: {match.view_name}")
except Exception as e:
    print(f"Resolution Error: {e}")

try:
    url = reverse('api_market_prices')
    print(f"Reversed: {url}")
except Exception as e:
    print(f"Reverse Error: {e}")

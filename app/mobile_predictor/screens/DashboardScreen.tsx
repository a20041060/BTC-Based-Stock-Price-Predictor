import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, RefreshControl, StyleSheet } from 'react-native';
import axios from 'axios';
import { Card } from '../components/Card';
import { API_BASE_URL, STOCK_TICKERS } from '../constants';
import { MarketPrices } from '../types';

interface DashboardScreenProps {
  useDirectFetch: boolean;
  useDirectStocks: boolean;
}

export const DashboardScreen = ({ useDirectFetch, useDirectStocks }: DashboardScreenProps) => {
  const [marketPrices, setMarketPrices] = useState<MarketPrices>({});
  const [loadingPrices, setLoadingPrices] = useState(false);

  const fetchDirectBTCPrice = async () => {
    try {
      const response = await axios.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', { timeout: 5000 });
      return parseFloat(response.data.price);
    } catch (err) {
      console.warn("Direct Binance fetch failed:", err);
      return null;
    }
  };

  const fetchDirectStockPrice = async (ticker: string) => {
    try {
      // Using Yahoo Finance query1 API (Unofficial but widely used)
      // Note: May encounter CORS issues in Web Browser environments without proxy
      const response = await axios.get(`https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1m&range=1d`, { timeout: 5000 });
      const result = response.data.chart.result[0];
      return result.meta.regularMarketPrice;
    } catch (err) {
      console.warn(`Direct Yahoo fetch failed for ${ticker}:`, err);
      return null;
    }
  };

  const fetchMarketPrices = async () => {
    setLoadingPrices(true);
    try {
      let newPrices: MarketPrices = {};

      // 1. Decide source for BTC
      const btcPromise = useDirectFetch ? fetchDirectBTCPrice() : Promise.resolve(null);
      
      // 2. Decide source for Stocks
      const stockPromises = useDirectStocks 
        ? STOCK_TICKERS.map(t => fetchDirectStockPrice(t).then(price => ({ ticker: t, price })))
        : [];

      // 3. Backend Fetch
      const shouldFetchBackend = !useDirectFetch || !useDirectStocks;
      const backendPromise = shouldFetchBackend 
        ? axios.get(`${API_BASE_URL}/api/market-prices/`, { timeout: 5000 }).catch(err => {
            console.warn("Backend fetch failed:", err);
            return null;
          })
        : Promise.resolve(null);

      const [btcResult, backendResult, ...stockResults] = await Promise.all([
        btcPromise,
        backendPromise,
        ...stockPromises
      ]);

      // Process Backend Data first (as base)
      if (backendResult && backendResult.data) {
        newPrices = { ...backendResult.data.prices };
      }

      // Override with Direct Stock Data
      stockResults.forEach((res: any) => {
        if (res && res.price !== null) {
          newPrices[res.ticker] = res.price;
        }
      });

      // Override with Direct BTC Data
      if (btcResult !== null) {
        newPrices['BTC-USD'] = btcResult;
      }

      setMarketPrices(newPrices);
    } catch (err) {
      console.error("Failed to fetch prices:", err);
    } finally {
      setLoadingPrices(false);
    }
  };

  useEffect(() => {
    fetchMarketPrices();
    const interval = setInterval(fetchMarketPrices, 30000); // Auto-refresh every 30s
    return () => clearInterval(interval);
  }, [useDirectFetch, useDirectStocks]);

  return (
    <ScrollView 
      contentContainerStyle={styles.scrollContent}
      refreshControl={<RefreshControl refreshing={loadingPrices} onRefresh={fetchMarketPrices} />}
    >
      <Text style={styles.headerTitle}>⚡ Real-Time Market</Text>
      <Text style={styles.lastUpdated}>Pull to refresh • Auto-updates 30s</Text>
      
      <View style={styles.gridContainer}>
        {Object.entries(marketPrices).length > 0 ? (
          Object.entries(marketPrices).map(([symbol, price]) => (
            <Card key={symbol} style={styles.priceCard}>
              <Text style={styles.tickerText}>{symbol}</Text>
              <Text style={styles.priceText}>
                ${price ? price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) : 'N/A'}
              </Text>
            </Card>
          ))
        ) : (
          <Text style={styles.loadingText}>Loading market data...</Text>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  scrollContent: {
    padding: 16,
    paddingTop: 60,
    paddingBottom: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: '#1a1a1a',
    marginBottom: 5,
  },
  lastUpdated: {
    fontSize: 12,
    color: '#666',
    marginBottom: 20,
  },
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  priceCard: {
    width: '48%',
    alignItems: 'center',
    paddingVertical: 20,
  },
  tickerText: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
  },
  priceText: {
    fontSize: 22,
    fontWeight: '600',
    color: '#007AFF',
    marginTop: 5,
  },
  loadingText: {
    textAlign: 'center',
    color: '#666',
    marginTop: 20,
  },
});

import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, RefreshControl, StyleSheet } from 'react-native';
import axios from 'axios';
import { Card } from '../components/Card';
import { API_BASE_URL, STOCK_TICKERS } from '../constants';
import { MarketPrices, ExtendedPriceInfo } from '../types';

interface DashboardScreenProps {
  useDirectFetch: boolean;
  useDirectStocks: boolean;
  isDarkMode?: boolean;
}

export const DashboardScreen = ({ useDirectFetch, useDirectStocks, isDarkMode }: DashboardScreenProps) => {
  const [marketPrices, setMarketPrices] = useState<MarketPrices>({});
  const [loadingPrices, setLoadingPrices] = useState(false);

  const themeStyles = {
    headerTitle: { color: isDarkMode ? '#fff' : '#1a1a1a' },
    lastUpdated: { color: isDarkMode ? '#aaa' : '#666' },
    tickerText: { color: isDarkMode ? '#eee' : '#333' },
    priceText: { color: isDarkMode ? '#4dabf7' : '#007AFF' },
    extendedText: { color: isDarkMode ? '#bbb' : '#666' },
    loadingText: { color: isDarkMode ? '#aaa' : '#666' },
    card: { backgroundColor: isDarkMode ? '#1e1e1e' : '#fff' },
  };

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
      // Use quote endpoint for extended hours data
      const response = await axios.get(`https://query1.finance.yahoo.com/v7/finance/quote?symbols=${ticker}`, { timeout: 5000 });
      const result = response.data.quoteResponse.result[0];
      
      // Map Yahoo marketState to our format
      let marketState = result.marketState;
      if (marketState === 'REGULAR') marketState = 'OPEN';
      
      return {
        price: result.regularMarketPrice,
        market_state: marketState,
        regular_market_price: result.regularMarketPrice,
        pre_market_price: result.preMarketPrice,
        post_market_price: result.postMarketPrice
      } as ExtendedPriceInfo;
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

  const renderPriceInfo = (symbol: string, data: number | ExtendedPriceInfo | null) => {
    if (data === null || data === undefined) {
      return <Text style={[styles.priceText, themeStyles.priceText]}>N/A</Text>;
    }

    if (typeof data === 'number') {
      return <Text style={[styles.priceText, themeStyles.priceText]}>${data.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</Text>;
    }

    // Extended Info Object
    const state = data.market_state ? data.market_state.toUpperCase() : 'CLOSED';
    const isMarketOpen = state === 'OPEN' || state === 'REGULAR';
    
    const showPre = !isMarketOpen && (state === 'PRE' || state === 'CLOSED') && !!data.pre_market_price;
    const showPost = !isMarketOpen && (state === 'POST' || state === 'CLOSED') && !!data.post_market_price;

    // Logic: If Closed, show relevant one. Usually Yahoo gives both or valid ones.
    // Requirement: "when US stock market open dont show the pre-market and after-market price"
    
    return (
      <View style={{ alignItems: 'center' }}>
        <Text style={[styles.priceText, themeStyles.priceText]}>
          ${data.price?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) ?? 'N/A'}
        </Text>
        
        {showPre && (
          <Text style={[styles.extendedText, themeStyles.extendedText]}>Pre: ${data.pre_market_price?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</Text>
        )}
        
        {showPost && (
          <Text style={[styles.extendedText, themeStyles.extendedText]}>Post: ${data.post_market_price?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</Text>
        )}
      </View>
    );
  };

  return (
    <ScrollView 
      contentContainerStyle={styles.scrollContent}
      refreshControl={<RefreshControl refreshing={loadingPrices} onRefresh={fetchMarketPrices} tintColor={isDarkMode ? "#fff" : "#000"} colors={[isDarkMode ? "#fff" : "#000"]} />}
    >
      <Text style={[styles.headerTitle, themeStyles.headerTitle]}>⚡ Real-Time Market</Text>
      <Text style={[styles.lastUpdated, themeStyles.lastUpdated]}>Pull to refresh • Auto-updates 30s</Text>
      
      <View style={styles.gridContainer}>
        {Object.entries(marketPrices).length > 0 ? (
          Object.entries(marketPrices).map(([symbol, price]) => (
            <Card key={symbol} style={[styles.priceCard, themeStyles.card]}>
              <Text style={[styles.tickerText, themeStyles.tickerText]}>{symbol}</Text>
              {renderPriceInfo(symbol, price)}
            </Card>
          ))
        ) : (
          <Text style={[styles.loadingText, themeStyles.loadingText]}>Loading market data...</Text>
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
    marginBottom: 15,
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
  extendedText: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  loadingText: {
    textAlign: 'center',
    color: '#666',
    marginTop: 20,
  },
});

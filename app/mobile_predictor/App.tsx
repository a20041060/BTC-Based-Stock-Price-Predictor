import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, ActivityIndicator, Platform, RefreshControl, Dimensions, Switch } from 'react-native';
import axios from 'axios';

// --- Types ---
interface PredictionResult {
  ticker: string;
  current_btc_price: number;
  current_stock_price: number;
  predicted_stock_price_beta: number;
  predicted_stock_price_power_law: number;
  beta: number;
  correlation: number;
}

interface SentimentResult {
  ticker: string;
  score: number;
  label: string;
  trend_score?: number;
  trend_label?: string;
  composite_score?: number;
  composite_label?: string;
  items: any[];
}

interface MarketPrices {
  [ticker: string]: number;
}

// --- Configuration ---
const API_BASE_URL = Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000';
const STOCK_TICKERS = ["IREN", "APLD", "HUT", "MARA", "CLSK", "COIN", "MSTR"];

// --- Components ---

const TabButton = ({ title, isActive, onPress }: { title: string, isActive: boolean, onPress: () => void }) => (
  <TouchableOpacity 
    style={[styles.tabButton, isActive && styles.activeTabButton]} 
    onPress={onPress}
  >
    <Text style={[styles.tabButtonText, isActive && styles.activeTabButtonText]}>{title}</Text>
  </TouchableOpacity>
);

const Card = ({ children, style }: { children: React.ReactNode, style?: any }) => (
  <View style={[styles.card, style]}>{children}</View>
);

const MetricBox = ({ label, value, delta, subLabel }: { label: string, value: string, delta?: string, subLabel?: string }) => (
  <View style={styles.metricBox}>
    <Text style={styles.metricLabel}>{label}</Text>
    <Text style={styles.metricValue}>{value}</Text>
    {delta && <Text style={[styles.metricDelta, delta.includes('-') ? styles.textRed : styles.textGreen]}>{delta}</Text>}
    {subLabel && <Text style={styles.metricSubLabel}>{subLabel}</Text>}
  </View>
);

// --- Main App ---

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'analysis' | 'settings'>('dashboard');
  
  // Settings State
  const [useDirectFetch, setUseDirectFetch] = useState(true); // Direct BTC
  const [useDirectStocks, setUseDirectStocks] = useState(false); // Direct Stocks (New)

  // Dashboard State
  const [marketPrices, setMarketPrices] = useState<MarketPrices>({});
  const [loadingPrices, setLoadingPrices] = useState(false);
  
  // Analysis State
  const [ticker, setTicker] = useState('IREN');
  const [targetBtc, setTargetBtc] = useState('100000');
  const [sentimentImpact, setSentimentImpact] = useState(1.0); // 1.0 = Neutral
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [sentiment, setSentiment] = useState<SentimentResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // --- Effects ---
  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchMarketPrices();
      const interval = setInterval(fetchMarketPrices, 30000); // Auto-refresh every 30s
      return () => clearInterval(interval);
    }
  }, [activeTab]);

  // --- API Calls ---
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

      // 3. Backend Fetch (Always fetch as fallback or base, unless we want to be purely offline)
      // But user said "without fetching local backend". So if both are ON, maybe we skip backend?
      // For safety, let's fetch backend if EITHER is off, or just always fetch to fill gaps.
      // However, to strictly follow "without fetching local backend", if both are ON, we shouldn't call backend.
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

  const handlePredict = async () => {
    setLoadingAnalysis(true);
    setError(null);
    setPrediction(null);
    setSentiment(null);

    try {
      // Fetch Prediction
      const predResponse = await axios.get(`${API_BASE_URL}/api/predict/`, {
        params: {
          ticker: ticker,
          target_btc: targetBtc,
          event_multiplier: sentimentImpact
        },
        timeout: 10000 // 10s timeout for prediction (might be slower)
      });
      setPrediction(predResponse.data);

      // Fetch Sentiment
      const sentResponse = await axios.get(`${API_BASE_URL}/api/sentiment/`, {
        params: { ticker: ticker },
        timeout: 10000 // 10s timeout for sentiment
      });
      setSentiment(sentResponse.data);

    } catch (err: any) {
      setError(err.message || 'An error occurred');
      console.error(err);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  // --- Render Views ---

  const renderDashboard = () => (
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

  const renderAnalysis = () => (
    <ScrollView contentContainerStyle={styles.scrollContent}>
      <Text style={styles.headerTitle}>📊 Stock Analysis</Text>
      
      <Card style={styles.configCard}>
        <Text style={styles.sectionHeader}>Configuration</Text>
        
        {/* Ticker Selector */}
        <Text style={styles.label}>Select Stock</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tickerSelector}>
          {STOCK_TICKERS.map(t => (
            <TouchableOpacity 
              key={t} 
              style={[styles.tickerOption, ticker === t && styles.activeTickerOption]}
              onPress={() => setTicker(t)}
            >
              <Text style={[styles.tickerOptionText, ticker === t && styles.activeTickerOptionText]}>{t}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Target BTC */}
        <Text style={styles.label}>Target BTC Price ($)</Text>
        <TextInput 
          style={styles.input} 
          value={targetBtc} 
          onChangeText={setTargetBtc}
          keyboardType="numeric"
          placeholder="100000"
        />

        {/* Sentiment Impact */}
        <Text style={styles.label}>Sentiment Impact (Event Multiplier)</Text>
        <View style={styles.segmentContainer}>
          {[
            { label: 'Bearish', value: 0.85 },
            { label: 'Neutral', value: 1.0 },
            { label: 'Bullish', value: 1.15 }
          ].map((opt) => (
            <TouchableOpacity 
              key={opt.label}
              style={[styles.segmentButton, sentimentImpact === opt.value && styles.activeSegmentButton]}
              onPress={() => setSentimentImpact(opt.value)}
            >
              <Text style={[styles.segmentText, sentimentImpact === opt.value && styles.activeSegmentText]}>
                {opt.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity style={styles.primaryButton} onPress={handlePredict} disabled={loadingAnalysis}>
          {loadingAnalysis ? <ActivityIndicator color="#fff" /> : <Text style={styles.primaryButtonText}>Analyze {ticker}</Text>}
        </TouchableOpacity>
      </Card>

      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {prediction && (
        <View>
          <Text style={styles.subHeader}>Prediction Results</Text>
          <Card>
             <View style={styles.row}>
               <MetricBox label="Current BTC" value={`$${prediction.current_btc_price.toLocaleString()}`} />
               <MetricBox label={`Current ${prediction.ticker}`} value={`$${prediction.current_stock_price.toLocaleString()}`} />
             </View>
             <View style={styles.divider} />
             <View style={styles.row}>
               <MetricBox label="Beta" value={prediction.beta.toFixed(2)} />
               <MetricBox label="Correlation" value={prediction.correlation.toFixed(2)} />
             </View>
          </Card>

          <Text style={styles.subHeader}>Price Targets @ BTC ${parseInt(targetBtc).toLocaleString()}</Text>
          <View style={styles.row}>
            <Card style={{flex: 1, marginRight: 5, backgroundColor: '#e3f2fd'}}>
              <Text style={styles.targetLabel}>Linear (Beta)</Text>
              <Text style={styles.targetValue}>${prediction.predicted_stock_price_beta.toFixed(2)}</Text>
              <Text style={styles.targetDelta}>
                {((prediction.predicted_stock_price_beta - prediction.current_stock_price) / prediction.current_stock_price * 100).toFixed(1)}%
              </Text>
            </Card>
            <Card style={{flex: 1, marginLeft: 5, backgroundColor: '#fff8e1'}}>
              <Text style={styles.targetLabel}>Power Law</Text>
              <Text style={styles.targetValue}>${prediction.predicted_stock_price_power_law.toFixed(2)}</Text>
              <Text style={styles.targetDelta}>
                {((prediction.predicted_stock_price_power_law - prediction.current_stock_price) / prediction.current_stock_price * 100).toFixed(1)}%
              </Text>
            </Card>
          </View>
        </View>
      )}

      {sentiment && (
        <View style={{marginBottom: 40}}>
           {sentiment.composite_label && (
             <>
               <Text style={styles.subHeader}>Market Signal (Trend + News)</Text>
               <Card style={{backgroundColor: sentiment.composite_label === 'Bullish' ? '#e8f5e9' : sentiment.composite_label === 'Bearish' ? '#ffebee' : '#fff3e0'}}>
                 <View style={{alignItems: 'center', padding: 10}}>
                   <Text style={{fontSize: 24, fontWeight: 'bold', color: sentiment.composite_label === 'Bullish' ? '#2e7d32' : sentiment.composite_label === 'Bearish' ? '#c62828' : '#ef6c00'}}>
                     {sentiment.composite_label.toUpperCase()}
                   </Text>
                   <Text style={{color: '#666', marginTop: 5}}>
                     Signal Strength: {sentiment.composite_score?.toFixed(2)}
                   </Text>
                   
                   <View style={{flexDirection: 'row', marginTop: 15, width: '100%', justifyContent: 'space-around'}}>
                     <View style={{alignItems: 'center'}}>
                       <Text style={{fontSize: 12, color: '#666', marginBottom: 2}}>Price Trend</Text>
                       <Text style={{fontWeight: '600', color: sentiment.trend_label === 'Bullish' ? 'green' : sentiment.trend_label === 'Bearish' ? 'red' : 'orange'}}>
                         {sentiment.trend_label}
                       </Text>
                     </View>
                     <View style={{width: 1, backgroundColor: '#ccc'}} />
                     <View style={{alignItems: 'center'}}>
                       <Text style={{fontSize: 12, color: '#666', marginBottom: 2}}>News Sentiment</Text>
                       <Text style={{fontWeight: '600', color: sentiment.label.includes('Bullish') ? 'green' : sentiment.label.includes('Bearish') ? 'red' : 'orange'}}>
                         {sentiment.label.replace(' Sentiment', '')}
                       </Text>
                     </View>
                   </View>
                 </View>
               </Card>
             </>
           )}

           <Text style={styles.subHeader}>AI Sentiment Analysis</Text>
           <Card>
             <Text style={[styles.sentimentScore, {color: sentiment.label.includes('Bullish') ? '#2e7d32' : sentiment.label.includes('Bearish') ? '#c62828' : '#f57f17'}]}>
               {sentiment.label} ({sentiment.score.toFixed(2)})
             </Text>
             <View style={styles.divider} />
             {sentiment.items.slice(0, 5).map((item, i) => (
               <View key={i} style={styles.newsItem}>
                 <Text style={styles.newsSource}>
                   {item.type === 'social' ? `@${item.author} (Social)` : item.provider || 'News'}
                 </Text>
                 <Text style={styles.newsTitle} numberOfLines={2}>{item.title || item.content}</Text>
                 <Text style={[styles.newsSentiment, {color: item.sentiment === 'Bullish' ? 'green' : item.sentiment === 'Bearish' ? 'red' : 'gray'}]}>
                   {item.sentiment}
                 </Text>
               </View>
             ))}
           </Card>
        </View>
      )}
    </ScrollView>
  );

  const renderSettings = () => (
    <ScrollView contentContainerStyle={styles.scrollContent}>
      <Text style={styles.headerTitle}>⚙️ Settings</Text>
      <Card>
        <Text style={styles.sectionHeader}>Data Source</Text>
        <View style={styles.settingRow}>
          <Text style={styles.label}>Direct BTC Fetch (Binance)</Text>
          <Switch
            trackColor={{ false: "#767577", true: "#81b0ff" }}
            thumbColor={useDirectFetch ? "#f5dd4b" : "#f4f3f4"}
            ios_backgroundColor="#3e3e3e"
            onValueChange={setUseDirectFetch}
            value={useDirectFetch}
          />
        </View>
        <Text style={styles.settingDescription}>
          Fetch BTC prices directly from Binance API.
        </Text>

        <View style={styles.divider} />

        <View style={styles.settingRow}>
          <Text style={styles.label}>Direct Stock Fetch (Yahoo)</Text>
          <Switch
            trackColor={{ false: "#767577", true: "#81b0ff" }}
            thumbColor={useDirectStocks ? "#f5dd4b" : "#f4f3f4"}
            ios_backgroundColor="#3e3e3e"
            onValueChange={setUseDirectStocks}
            value={useDirectStocks}
          />
        </View>
        <Text style={styles.settingDescription}>
          Fetch stock prices directly from Yahoo Finance. Warning: May fail on web due to CORS (use Proxy or Native app).
        </Text>
      </Card>
      
      <Card>
        <Text style={styles.sectionHeader}>App Info</Text>
        <Text style={styles.text}>BTC Stock Predictor v1.0</Text>
        <Text style={styles.text}>Rigid Architecture Mobile Client</Text>
        <View style={styles.divider} />
        <Text style={styles.label}>Backend URL</Text>
        <Text style={styles.value}>{API_BASE_URL}</Text>
      </Card>
    </ScrollView>
  );

  return (
    <View style={styles.container}>
      <StatusBar style="auto" />
      
      <View style={styles.contentContainer}>
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'analysis' && renderAnalysis()}
        {activeTab === 'settings' && renderSettings()}
      </View>

      <View style={styles.tabBar}>
        <TabButton title="Dashboard" isActive={activeTab === 'dashboard'} onPress={() => setActiveTab('dashboard')} />
        <TabButton title="Analysis" isActive={activeTab === 'analysis'} onPress={() => setActiveTab('analysis')} />
        <TabButton title="Settings" isActive={activeTab === 'settings'} onPress={() => setActiveTab('settings')} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  contentContainer: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingTop: 60,
    paddingBottom: 20,
  },
  // --- Typography ---
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
  sectionHeader: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 15,
    color: '#333',
  },
  subHeader: {
    fontSize: 20,
    fontWeight: '700',
    marginTop: 25,
    marginBottom: 10,
    color: '#333',
  },
  text: {
    fontSize: 16,
    color: '#333',
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#555',
    marginTop: 10,
    marginBottom: 5,
  },
  value: {
    fontSize: 16,
    color: '#333',
  },
  // --- Cards & Layout ---
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
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
  divider: {
    height: 1,
    backgroundColor: '#eee',
    marginVertical: 12,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  // --- Inputs & Buttons ---
  configCard: {
    marginBottom: 10,
  },
  input: {
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  tickerSelector: {
    flexDirection: 'row',
    marginBottom: 10,
  },
  tickerOption: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    marginRight: 8,
  },
  activeTickerOption: {
    backgroundColor: '#007AFF',
  },
  tickerOptionText: {
    fontWeight: '600',
    color: '#555',
  },
  activeTickerOptionText: {
    color: '#fff',
  },
  segmentContainer: {
    flexDirection: 'row',
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    padding: 4,
    marginTop: 5,
    marginBottom: 15,
  },
  segmentButton: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    borderRadius: 6,
  },
  activeSegmentButton: {
    backgroundColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 1,
    elevation: 1,
  },
  segmentText: {
    fontWeight: '600',
    color: '#666',
    fontSize: 13,
  },
  activeSegmentText: {
    color: '#007AFF',
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  settingDescription: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
    marginBottom: 15,
  },
  primaryButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 10,
  },
  primaryButtonText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 16,
  },
  // --- Metrics ---
  metricBox: {
    flex: 1,
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
  },
  metricDelta: {
    fontSize: 12,
    marginTop: 2,
  },
  metricSubLabel: {
    fontSize: 10,
    color: '#999',
  },
  textGreen: { color: 'green' },
  textRed: { color: 'red' },
  
  // --- Targets ---
  targetLabel: {
    fontSize: 12,
    color: '#555',
    fontWeight: '600',
    marginBottom: 5,
  },
  targetValue: {
    fontSize: 20,
    fontWeight: '800',
    color: '#333',
  },
  targetDelta: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
  },
  
  // --- Sentiment ---
  sentimentScore: {
    fontSize: 24,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 10,
  },
  newsItem: {
    marginBottom: 12,
  },
  newsSource: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
    marginBottom: 2,
  },
  newsTitle: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  newsSentiment: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 2,
  },

  // --- Tab Bar ---
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#eee',
    paddingBottom: Platform.OS === 'ios' ? 20 : 0,
    elevation: 8,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
  },
  activeTabButton: {
    borderTopWidth: 2,
    borderTopColor: '#007AFF',
  },
  tabButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#999',
  },
  activeTabButtonText: {
    color: '#007AFF',
  },
  
  // --- Error ---
  errorBox: {
    backgroundColor: '#ffebee',
    padding: 12,
    borderRadius: 8,
    marginTop: 10,
    borderWidth: 1,
    borderColor: '#ef5350',
  },
  errorText: {
    color: '#c62828',
    textAlign: 'center',
  },
});

import React, { useState } from 'react';
import { View, Text, ScrollView, TextInput, TouchableOpacity, ActivityIndicator, StyleSheet } from 'react-native';
import axios from 'axios';
import { Card } from '../components/Card';
import { MetricBox } from '../components/MetricBox';
import { API_BASE_URL, STOCK_TICKERS } from '../constants';
import { PredictionResult, SentimentResult } from '../types';

interface AnalysisScreenProps {
  isDarkMode?: boolean;
}

export const AnalysisScreen = ({ isDarkMode }: AnalysisScreenProps) => {
  const [ticker, setTicker] = useState('IREN');
  const [targetBtc, setTargetBtc] = useState('100000');
  const [sentimentImpact, setSentimentImpact] = useState(1.0); // 1.0 = Neutral
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [sentiment, setSentiment] = useState<SentimentResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const themeStyles = {
    headerTitle: { color: isDarkMode ? '#fff' : '#1a1a1a' },
    sectionHeader: { color: isDarkMode ? '#eee' : '#333' },
    subHeader: { color: isDarkMode ? '#ddd' : '#333' },
    label: { color: isDarkMode ? '#ccc' : '#555' },
    tickerOptionText: { color: isDarkMode ? '#ddd' : '#555' },
    input: { 
      backgroundColor: isDarkMode ? '#333' : '#f5f5f5',
      color: isDarkMode ? '#fff' : '#000',
      borderColor: isDarkMode ? '#444' : '#e0e0e0'
    },
    segmentContainer: { backgroundColor: isDarkMode ? '#333' : '#f0f0f0' },
    segmentButton: { backgroundColor: isDarkMode ? '#333' : '#f0f0f0' },
    activeSegmentButton: { backgroundColor: isDarkMode ? '#555' : '#fff' },
    segmentText: { color: isDarkMode ? '#aaa' : '#666' },
    activeSegmentText: { color: isDarkMode ? '#fff' : '#333' },
    card: { backgroundColor: isDarkMode ? '#1e1e1e' : '#fff' },
    newsTitle: { color: isDarkMode ? '#ddd' : '#333' },
    targetLabel: { color: isDarkMode ? '#aaa' : '#666' },
    targetValue: { color: isDarkMode ? '#eee' : '#333' },
    newsSource: { color: isDarkMode ? '#888' : '#888' },
    divider: { backgroundColor: isDarkMode ? '#333' : '#eee' },
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

  return (
    <ScrollView contentContainerStyle={styles.scrollContent}>
      <Text style={[styles.headerTitle, themeStyles.headerTitle]}>📊 Stock Analysis</Text>
      
      <Card style={[styles.configCard, themeStyles.card]}>
        <Text style={[styles.sectionHeader, themeStyles.sectionHeader]}>Configuration</Text>
        
        {/* Ticker Selector */}
        <Text style={[styles.label, themeStyles.label]}>Select Stock</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tickerSelector}>
          {STOCK_TICKERS.map(t => (
            <TouchableOpacity 
              key={t} 
              style={[styles.tickerOption, ticker === t && styles.activeTickerOption]}
              onPress={() => setTicker(t)}
            >
              <Text style={[styles.tickerOptionText, themeStyles.tickerOptionText, ticker === t && styles.activeTickerOptionText]}>{t}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Target BTC */}
        <Text style={[styles.label, themeStyles.label]}>Target BTC Price ($)</Text>
        <TextInput 
          style={[styles.input, themeStyles.input]} 
          value={targetBtc} 
          onChangeText={setTargetBtc}
          keyboardType="numeric"
          placeholder="100000"
          placeholderTextColor={isDarkMode ? "#666" : "#999"}
        />

        {/* Sentiment Impact */}
        <Text style={[styles.label, themeStyles.label]}>Sentiment Impact (Event Multiplier)</Text>
        <View style={[styles.segmentContainer, themeStyles.segmentContainer]}>
          {[
            { label: 'Bearish', value: 0.85 },
            { label: 'Neutral', value: 1.0 },
            { label: 'Bullish', value: 1.15 }
          ].map((opt) => (
            <TouchableOpacity 
              key={opt.label}
              style={[
                styles.segmentButton, 
                themeStyles.segmentButton, 
                sentimentImpact === opt.value && styles.activeSegmentButton,
                sentimentImpact === opt.value && themeStyles.activeSegmentButton
              ]}
              onPress={() => setSentimentImpact(opt.value)}
            >
              <Text style={[
                styles.segmentText, 
                themeStyles.segmentText, 
                sentimentImpact === opt.value && styles.activeSegmentText,
                sentimentImpact === opt.value && themeStyles.activeSegmentText
              ]}>
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
          <Text style={[styles.subHeader, themeStyles.subHeader]}>Prediction Results</Text>
          <Card style={themeStyles.card}>
             <View style={styles.row}>
               <MetricBox label="Current BTC" value={`$${prediction.current_btc_price.toLocaleString()}`} isDarkMode={isDarkMode} />
               <MetricBox label={`Current ${prediction.ticker}`} value={`$${prediction.current_stock_price.toLocaleString()}`} isDarkMode={isDarkMode} />
             </View>
             <View style={[styles.divider, themeStyles.divider]} />
             <View style={styles.row}>
               <MetricBox label="Beta" value={prediction.beta.toFixed(2)} isDarkMode={isDarkMode} />
               <MetricBox label="Correlation" value={prediction.correlation.toFixed(2)} isDarkMode={isDarkMode} />
             </View>
          </Card>

          <Text style={[styles.subHeader, themeStyles.subHeader]}>Price Targets @ BTC ${parseInt(targetBtc).toLocaleString()}</Text>
          <View style={styles.row}>
            <Card style={{flex: 1, marginRight: 5, backgroundColor: isDarkMode ? '#1a237e' : '#e3f2fd'}}>
              <Text style={[styles.targetLabel, themeStyles.targetLabel, {color: isDarkMode ? '#ddd' : '#666'}]}>Linear (Beta)</Text>
              <Text style={[styles.targetValue, themeStyles.targetValue, {color: isDarkMode ? '#fff' : '#333'}]}>${prediction.predicted_stock_price_beta.toFixed(2)}</Text>
              <Text style={styles.targetDelta}>
                {((prediction.predicted_stock_price_beta - prediction.current_stock_price) / prediction.current_stock_price * 100).toFixed(1)}%
              </Text>
            </Card>
            <Card style={{flex: 1, marginLeft: 5, backgroundColor: isDarkMode ? '#3e2723' : '#fff8e1'}}>
              <Text style={[styles.targetLabel, themeStyles.targetLabel, {color: isDarkMode ? '#ddd' : '#666'}]}>Power Law</Text>
              <Text style={[styles.targetValue, themeStyles.targetValue, {color: isDarkMode ? '#fff' : '#333'}]}>${prediction.predicted_stock_price_power_law.toFixed(2)}</Text>
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
               <Text style={[styles.subHeader, themeStyles.subHeader]}>Market Signal (Trend + News)</Text>
               <Card style={{backgroundColor: sentiment.composite_label === 'Bullish' ? (isDarkMode ? '#1b5e20' : '#e8f5e9') : sentiment.composite_label === 'Bearish' ? (isDarkMode ? '#b71c1c' : '#ffebee') : (isDarkMode ? '#e65100' : '#fff3e0')}}>
                 <View style={{alignItems: 'center', padding: 10}}>
                   <Text style={{fontSize: 24, fontWeight: 'bold', color: sentiment.composite_label === 'Bullish' ? (isDarkMode ? '#66bb6a' : '#2e7d32') : sentiment.composite_label === 'Bearish' ? (isDarkMode ? '#ef5350' : '#c62828') : (isDarkMode ? '#ffb74d' : '#ef6c00')}}>
                     {sentiment.composite_label.toUpperCase()}
                   </Text>
                   <Text style={{color: isDarkMode ? '#ccc' : '#666', marginTop: 5}}>
                     Signal Strength: {sentiment.composite_score?.toFixed(2)}
                   </Text>
                   
                   <View style={{flexDirection: 'row', marginTop: 15, width: '100%', justifyContent: 'space-around'}}>
                     <View style={{alignItems: 'center'}}>
                       <Text style={{fontSize: 12, color: isDarkMode ? '#ccc' : '#666', marginBottom: 2}}>Price Trend</Text>
                       <Text style={{fontWeight: '600', color: sentiment.trend_label === 'Bullish' ? 'green' : sentiment.trend_label === 'Bearish' ? 'red' : 'orange'}}>
                         {sentiment.trend_label}
                       </Text>
                     </View>
                     <View style={{width: 1, backgroundColor: isDarkMode ? '#555' : '#ccc'}} />
                     <View style={{alignItems: 'center'}}>
                       <Text style={{fontSize: 12, color: isDarkMode ? '#ccc' : '#666', marginBottom: 2}}>News Sentiment</Text>
                       <Text style={{fontWeight: '600', color: sentiment.label.includes('Bullish') ? 'green' : sentiment.label.includes('Bearish') ? 'red' : 'orange'}}>
                         {sentiment.label.replace(' Sentiment', '')}
                       </Text>
                     </View>
                   </View>
                 </View>
               </Card>
             </>
           )}

           <Text style={[styles.subHeader, themeStyles.subHeader]}>AI Sentiment Analysis</Text>
           <Card style={themeStyles.card}>
             <Text style={[styles.sentimentScore, {color: sentiment.label.includes('Bullish') ? '#2e7d32' : sentiment.label.includes('Bearish') ? '#c62828' : '#f57f17'}]}>
               {sentiment.label} ({sentiment.score.toFixed(2)})
             </Text>
             <View style={[styles.divider, themeStyles.divider]} />
             {sentiment.items.slice(0, 5).map((item, i) => (
               <View key={i} style={styles.newsItem}>
                 <Text style={[styles.newsSource, themeStyles.newsSource]}>
                   {item.type === 'social' ? `@${item.author} (Social)` : item.provider || 'News'}
                 </Text>
                 <Text style={[styles.newsTitle, themeStyles.newsTitle]} numberOfLines={2}>{item.title || item.content}</Text>
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
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#555',
    marginTop: 10,
    marginBottom: 5,
  },
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
    shadowRadius: 2,
    elevation: 1,
  },
  segmentText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  activeSegmentText: {
    color: '#333',
    fontWeight: '600',
  },
  primaryButton: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 10,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
  errorBox: {
    backgroundColor: '#ffebee',
    padding: 12,
    borderRadius: 8,
    marginTop: 10,
    borderWidth: 1,
    borderColor: '#ffcdd2',
  },
  errorText: {
    color: '#c62828',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  divider: {
    height: 1,
    backgroundColor: '#eee',
    marginVertical: 12,
  },
  targetLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  targetValue: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
  },
  targetDelta: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 2,
    color: '#007AFF',
  },
  sentimentScore: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 10,
  },
  newsItem: {
    marginBottom: 12,
  },
  newsSource: {
    fontSize: 10,
    color: '#888',
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  newsTitle: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
    lineHeight: 20,
  },
  newsSentiment: {
    fontSize: 12,
    fontWeight: '600',
  },
});

import React from 'react';
import { View, Text, ScrollView, Switch, StyleSheet } from 'react-native';
import { Card } from '../components/Card';
import { API_BASE_URL } from '../constants';

interface SettingsScreenProps {
  useDirectFetch: boolean;
  setUseDirectFetch: (value: boolean) => void;
  useDirectStocks: boolean;
  setUseDirectStocks: (value: boolean) => void;
}

export const SettingsScreen = ({ 
  useDirectFetch, 
  setUseDirectFetch, 
  useDirectStocks, 
  setUseDirectStocks 
}: SettingsScreenProps) => {
  return (
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
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#555',
    marginTop: 10,
    marginBottom: 5,
  },
  text: {
    fontSize: 16,
    color: '#333',
  },
  value: {
    fontSize: 16,
    color: '#333',
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  settingDescription: {
    fontSize: 12,
    color: '#666',
    marginBottom: 10,
  },
  divider: {
    height: 1,
    backgroundColor: '#eee',
    marginVertical: 12,
  },
});

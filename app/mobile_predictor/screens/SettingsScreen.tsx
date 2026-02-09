import React from 'react';
import { View, Text, ScrollView, Switch, StyleSheet } from 'react-native';
import { Card } from '../components/Card';
import { API_BASE_URL } from '../constants';

interface SettingsScreenProps {
  useDirectFetch: boolean;
  setUseDirectFetch: (value: boolean) => void;
  useDirectStocks: boolean;
  setUseDirectStocks: (value: boolean) => void;
  isDarkMode: boolean;
  setIsDarkMode: (value: boolean) => void;
}

export const SettingsScreen = ({ 
  useDirectFetch, 
  setUseDirectFetch, 
  useDirectStocks, 
  setUseDirectStocks,
  isDarkMode,
  setIsDarkMode
}: SettingsScreenProps) => {
  const themeStyles = {
    headerTitle: { color: isDarkMode ? '#fff' : '#1a1a1a' },
    sectionHeader: { color: isDarkMode ? '#eee' : '#333' },
    label: { color: isDarkMode ? '#ccc' : '#555' },
    text: { color: isDarkMode ? '#ddd' : '#333' },
    value: { color: isDarkMode ? '#ddd' : '#333' },
    description: { color: isDarkMode ? '#aaa' : '#666' },
    card: { backgroundColor: isDarkMode ? '#1e1e1e' : '#fff' },
  };

  return (
    <ScrollView contentContainerStyle={styles.scrollContent}>
      <Text style={[styles.headerTitle, themeStyles.headerTitle]}>⚙️ Settings</Text>
      
      <Card style={themeStyles.card}>
        <Text style={[styles.sectionHeader, themeStyles.sectionHeader]}>Appearance</Text>
        <View style={styles.settingRow}>
          <Text style={[styles.label, themeStyles.label]}>Dark Mode</Text>
          <Switch
            trackColor={{ false: "#767577", true: "#81b0ff" }}
            thumbColor={isDarkMode ? "#f5dd4b" : "#f4f3f4"}
            ios_backgroundColor="#3e3e3e"
            onValueChange={setIsDarkMode}
            value={isDarkMode}
          />
        </View>
      </Card>

      <Card style={themeStyles.card}>
        <Text style={[styles.sectionHeader, themeStyles.sectionHeader]}>Data Source</Text>
        <View style={styles.settingRow}>
          <Text style={[styles.label, themeStyles.label]}>Direct BTC Fetch (Binance)</Text>
          <Switch
            trackColor={{ false: "#767577", true: "#81b0ff" }}
            thumbColor={useDirectFetch ? "#f5dd4b" : "#f4f3f4"}
            ios_backgroundColor="#3e3e3e"
            onValueChange={setUseDirectFetch}
            value={useDirectFetch}
          />
        </View>
        <Text style={[styles.settingDescription, themeStyles.description]}>
          Fetch BTC prices directly from Binance API.
        </Text>

        <View style={styles.divider} />

        <View style={styles.settingRow}>
          <Text style={[styles.label, themeStyles.label]}>Direct Stock Fetch (Yahoo)</Text>
          <Switch
            trackColor={{ false: "#767577", true: "#81b0ff" }}
            thumbColor={useDirectStocks ? "#f5dd4b" : "#f4f3f4"}
            ios_backgroundColor="#3e3e3e"
            onValueChange={setUseDirectStocks}
            value={useDirectStocks}
          />
        </View>
        <Text style={[styles.settingDescription, themeStyles.description]}>
          Fetch stock prices directly from Yahoo Finance. Warning: May fail on web due to CORS (use Proxy or Native app).
        </Text>
      </Card>
      
      <Card style={themeStyles.card}>
        <Text style={[styles.sectionHeader, themeStyles.sectionHeader]}>App Info</Text>
        <Text style={[styles.text, themeStyles.text]}>BTC Stock Predictor v1.0</Text>
        <Text style={[styles.text, themeStyles.text]}>Rigid Architecture Mobile Client</Text>
        <View style={styles.divider} />
        <Text style={[styles.label, themeStyles.label]}>Backend URL</Text>
        <Text style={[styles.value, themeStyles.value]}>{API_BASE_URL}</Text>
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

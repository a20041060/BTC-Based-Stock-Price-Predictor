import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';

// --- Components ---
import { TabButton } from './components/TabButton';

// --- Screens ---
import { DashboardScreen } from './screens/DashboardScreen';
import { AnalysisScreen } from './screens/AnalysisScreen';
import { SettingsScreen } from './screens/SettingsScreen';

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'analysis' | 'settings'>('dashboard');
  
  // Settings State (Global)
  const [useDirectFetch, setUseDirectFetch] = useState(true); // Direct BTC
  const [useDirectStocks, setUseDirectStocks] = useState(false); // Direct Stocks (New)

  // --- Render Views ---

  return (
    <View style={styles.container}>
      <StatusBar style="auto" />
      
      <View style={styles.contentContainer}>
        {activeTab === 'dashboard' && (
          <DashboardScreen 
            useDirectFetch={useDirectFetch} 
            useDirectStocks={useDirectStocks} 
          />
        )}
        {activeTab === 'analysis' && <AnalysisScreen />}
        {activeTab === 'settings' && (
          <SettingsScreen 
            useDirectFetch={useDirectFetch} 
            setUseDirectFetch={setUseDirectFetch}
            useDirectStocks={useDirectStocks}
            setUseDirectStocks={setUseDirectStocks}
          />
        )}
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
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#fff',
    paddingBottom: 20,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#eee',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 5,
  },
});

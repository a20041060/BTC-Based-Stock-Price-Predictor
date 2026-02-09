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
  const [isDarkMode, setIsDarkMode] = useState(false);

  const theme = {
    container: {
      backgroundColor: isDarkMode ? '#121212' : '#f8f9fa',
    },
    tabBar: {
      backgroundColor: isDarkMode ? '#1e1e1e' : '#fff',
      borderTopColor: isDarkMode ? '#333' : '#eee',
    }
  };

  // --- Render Views ---

  return (
    <View style={[styles.container, theme.container]}>
      <StatusBar style={isDarkMode ? "light" : "dark"} />
      
      <View style={styles.contentContainer}>
        {activeTab === 'dashboard' && (
          <DashboardScreen 
            useDirectFetch={useDirectFetch} 
            useDirectStocks={useDirectStocks} 
            isDarkMode={isDarkMode}
          />
        )}
        {activeTab === 'analysis' && <AnalysisScreen isDarkMode={isDarkMode} />}
        {activeTab === 'settings' && (
          <SettingsScreen 
            useDirectFetch={useDirectFetch} 
            setUseDirectFetch={setUseDirectFetch}
            useDirectStocks={useDirectStocks}
            setUseDirectStocks={setUseDirectStocks}
            isDarkMode={isDarkMode}
            setIsDarkMode={setIsDarkMode}
          />
        )}
      </View>

      <View style={[styles.tabBar, theme.tabBar]}>
        <TabButton title="Dashboard" isActive={activeTab === 'dashboard'} onPress={() => setActiveTab('dashboard')} isDarkMode={isDarkMode} />
        <TabButton title="Analysis" isActive={activeTab === 'analysis'} onPress={() => setActiveTab('analysis')} isDarkMode={isDarkMode} />
        <TabButton title="Settings" isActive={activeTab === 'settings'} onPress={() => setActiveTab('settings')} isDarkMode={isDarkMode} />
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

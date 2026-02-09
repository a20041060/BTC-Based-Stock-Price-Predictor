import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';

interface TabButtonProps {
  title: string;
  isActive: boolean;
  onPress: () => void;
  isDarkMode?: boolean;
}

export const TabButton = ({ title, isActive, onPress, isDarkMode }: TabButtonProps) => (
  <TouchableOpacity 
    style={[styles.tabButton, isActive && styles.activeTabButton]} 
    onPress={onPress}
  >
    <Text style={[
      styles.tabButtonText, 
      isDarkMode && styles.darkTabButtonText,
      isActive && styles.activeTabButtonText
    ]}>{title}</Text>
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  tabButton: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
  },
  activeTabButton: {
    backgroundColor: '#007AFF',
  },
  tabButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  darkTabButtonText: {
    color: '#aaa',
  },
  activeTabButtonText: {
    color: '#fff',
  },
});

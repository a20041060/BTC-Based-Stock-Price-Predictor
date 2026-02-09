import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface MetricBoxProps {
  label: string;
  value: string;
  delta?: string;
  subLabel?: string;
}

export const MetricBox = ({ label, value, delta, subLabel }: MetricBoxProps) => (
  <View style={styles.metricBox}>
    <Text style={styles.metricLabel}>{label}</Text>
    <Text style={styles.metricValue}>{value}</Text>
    {delta && <Text style={[styles.metricDelta, delta.includes('-') ? styles.textRed : styles.textGreen]}>{delta}</Text>}
    {subLabel && <Text style={styles.metricSubLabel}>{subLabel}</Text>}
  </View>
);

const styles = StyleSheet.create({
  metricBox: {
    alignItems: 'center',
    padding: 10,
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
  },
  metricDelta: {
    fontSize: 12,
    marginTop: 2,
    fontWeight: '600',
  },
  metricSubLabel: {
    fontSize: 10,
    color: '#888',
    marginTop: 2,
  },
  textGreen: {
    color: 'green',
  },
  textRed: {
    color: 'red',
  },
});

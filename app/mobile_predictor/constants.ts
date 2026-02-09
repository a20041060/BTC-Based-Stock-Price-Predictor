import { Platform } from 'react-native';

export const API_BASE_URL = Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000';
export const STOCK_TICKERS = ["IREN", "APLD", "HUT", "MARA", "CLSK", "COIN", "MSTR"];

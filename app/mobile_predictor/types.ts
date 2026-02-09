export interface PredictionResult {
  ticker: string;
  current_btc_price: number;
  current_stock_price: number;
  predicted_stock_price_beta: number;
  predicted_stock_price_power_law: number;
  beta: number;
  correlation: number;
}

export interface SentimentResult {
  ticker: string;
  score: number;
  label: string;
  trend_score?: number;
  trend_label?: string;
  composite_score?: number;
  composite_label?: string;
  items: any[];
}

export interface ExtendedPriceInfo {
  price: number;
  market_state?: string;
  pre_market_price?: number | null;
  post_market_price?: number | null;
  regular_market_price?: number;
}

export interface MarketPrices {
  [ticker: string]: number | ExtendedPriceInfo | null;
}

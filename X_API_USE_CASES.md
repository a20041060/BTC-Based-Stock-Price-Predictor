# Use Case Description for X API

## 1. Overview
The **BTC Stock Predictor** application integrates X (formerly Twitter) data to enhance financial analysis and stock price predictions. By analyzing real-time social media conversations, the application gauges market sentiment towards specific assets (Bitcoin and Bitcoin-mining stocks like IREN, MARA, HUT), which serves as a critical input for our predictive models.

## 2. Core Use Cases

### A. Real-Time Sentiment Analysis
*   **Description**: The application searches for recent posts containing specific stock tickers (e.g., `$IREN`, `$MARA`, `$BTC`) and keywords using the `recent search` endpoint.
*   **Purpose**: To capture the immediate market mood (Bullish vs. Bearish) that traditional financial indicators might miss.
*   **Methodology**:
    *   Fetch the latest 10-100 posts related to the asset.
    *   Process the text content using Natural Language Processing (NLP) models (FinBERT or VADER).
    *   Aggregate individual post sentiment scores into a single "Market Sentiment" metric.

### B. Enhanced Price Prediction Modeling
*   **Description**: The aggregated sentiment score derived from X data is used as a quantitative variable in our price prediction algorithms.
*   **Purpose**: To adjust price targets based on "Event Impact" and crowd psychology.
*   **Methodology**:
    *   The base prediction (derived from historical Beta and Correlation with Bitcoin) is multiplied by a "Sentiment Factor."
    *   For example, a "Very Bullish" sentiment from X data might increase the predicted price target by a factor of 1.15x, while "Bearish" sentiment might reduce it.

### C. User Context & Transparency
*   **Description**: The application displays a curated list of the most relevant recent posts directly in the user dashboard (Web and Mobile).
*   **Purpose**: To provide users with qualitative context behind the quantitative sentiment scores.
*   **Methodology**:
    *   Show the post content, author, and date alongside its calculated sentiment label (e.g., "Bullish").
    *   Allow users to see exactly what "the market" is saying to validate the AI's assessment.

## 3. Data Usage Specifics

*   **Endpoints Used**:
    *   `GET /2/tweets/search/recent`: To find relevant conversation about specific financial assets.
*   **Data Fields Accessed**:
    *   `text`: For sentiment analysis.
    *   `created_at`: To ensure relevance (analyzing only recent market reactions).
    *   `public_metrics` (likes/retweets): To weight the sentiment (e.g., a highly liked post may carry more weight in the sentiment score).
    *   `author_id` / `username`: For attribution in the UI.
*   **Volume**:
    *   Low volume. The app performs targeted searches only when a user actively requests an analysis for a specific ticker.
    *   Approx. 10-20 requests per user session.

## 4. Compliance & Privacy
*   **Display**: Posts are displayed in accordance with display requirements (showing author, content, and date).
*   **Storage**: Data is processed in-memory for the duration of the analysis session and is not permanently stored or redistributed.
*   **Privacy**: The application focuses solely on public metrics and public conversation about financial assets; it does not analyze private user data or target individuals.

## 5. Pricing & Requirements (Important)
*   **Free Tier**: The "Free" tier of the X API is primarily **write-only** (posting tweets). It **does not** support the `recent search` endpoint required for this application's sentiment analysis.
*   **Required Tier**: To use the `GET /2/tweets/search/recent` endpoint, you must subscribe to at least the **Basic Tier** (approx. $100/month).
    *   **Basic Tier Limits**: 10,000 posts per month (read limit).
    *   **Pro Tier**: Higher limits for enterprise-grade scaling.
*   **Fallback**: This application includes a "Mock Data" mode. If no valid API Key is provided (or if the subscription is inactive), the app will simulate data so features remain testable without cost.

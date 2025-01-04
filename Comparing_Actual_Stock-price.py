import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = fdr.DataReader('041510', '2024-11-01', '2024-11-30')
df.reset_index(inplace=True)

sentiment_daily = pd.read_csv('sentiment_daily.csv')
sentiment_daily['Date'] = pd.to_datetime(sentiment_daily['Date']).dt.date
df['Date'] = df['Date'].dt.date
df = pd.merge(df, sentiment_daily, on='Date', how='left')
df['sentiment_diff'] = df['sentiment_diff'].fillna(0)

def predict_prices_with_sentiment(df):
    predicted_prices = []
    prediction_dates = []

    for i in range(1, len(df)):
        previous_price = df.iloc[i - 1]['Close']
        sentiment_diff_sum = df[df['Date'] == df.iloc[i - 1]['Date']]['sentiment_diff'].sum()

        # Weight setting
        predicted_price = previous_price + sentiment_diff_sum*3

        predicted_prices.append(predicted_price)
        prediction_dates.append(df.iloc[i]['Date'])

    return prediction_dates, predicted_prices

prediction_dates, predicted_prices = predict_prices_with_sentiment(df)
actual_prices = df.iloc[1:]['Close'].values

# Visualization
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['Close'], label='Actual Stock Prices', color='blue', marker='o', alpha=0.7)
plt.plot(prediction_dates, predicted_prices, label='Predicted Stock Prices', color='red', linestyle='--', marker='x', alpha=0.7)
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.title('Actual vs Predicted Stock Prices (With Sentiment Analysis)')
plt.legend()
plt.grid(True)
plt.show()

for i in range(len(prediction_dates)):
    print(f"Date: {prediction_dates[i]}, Actual: {actual_prices[i-1]:.2f}, Predicted: {predicted_prices[i]:.2f}")

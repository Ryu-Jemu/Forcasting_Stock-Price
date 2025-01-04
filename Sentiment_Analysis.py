import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

news_df = pd.read_csv('crawled_news.csv')

MODEL_NAME = "beomi/KcELECTRA-base-v2022"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

def analyze_sentiment_kobert_safe(text):
    try:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=128,
            padding="max_length"
        )
        outputs = model(**inputs)
        scores = torch.nn.functional.softmax(outputs.logits, dim=1)
        sentiment = torch.argmax(scores).item()
        return sentiment, scores[0].tolist()
    except Exception as e:
        return None, [0, 0]

news_df['sentiment_diff'] = news_df['content'].apply(
    lambda text: analyze_sentiment_kobert_safe(text)[1][1] - analyze_sentiment_kobert_safe(text)[1][0]
)
# Value Amplification
news_df['sentiment_diff'] = news_df['sentiment_diff'] * 10000

news_df['Date'] = pd.to_datetime(news_df['date'])
sentiment_daily = news_df.groupby('Date')['sentiment_diff'].mean().reset_index()
news_df['positive_score'] = news_df['content'].apply(
    lambda text: analyze_sentiment_kobert_safe(text)[1][1]
)
news_df['negative_score'] = news_df['content'].apply(
    lambda text: analyze_sentiment_kobert_safe(text)[1][0]
)

print("Positive Score Mean:", news_df['positive_score'].mean())
print("Negative Score Mean:", news_df['negative_score'].mean())
print("Sentiment Diff Mean:", news_df['sentiment_diff'].mean())

# Visualization
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))
plt.hist(news_df['positive_score'], bins=50, alpha=0.7, label='Positive Score', color='blue')
plt.hist(news_df['negative_score'], bins=50, alpha=0.7, label='Negative Score', color='red')
plt.xlabel('Score')
plt.ylabel('Frequency')
plt.legend()
plt.title('Distribution of Sentiment Scores')
plt.grid(True)
plt.show()

sentiment_daily.to_csv('sentiment_daily.csv', index=False)

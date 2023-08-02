import pandas as pd
import re
import plotter
import chat_parser
from textblob import TextBlob


class DataAnalyzer:
    def __init__(self, df):
        self.message_counts = df['user'].value_counts().to_dict()
        self.link_counts = dict.fromkeys(df['user'].unique(), 0)
        self.image_counts = dict.fromkeys(df['user'].unique(), 0)
        self.video_counts = dict.fromkeys(df['user'].unique(), 0)
        self.gif_counts = dict.fromkeys(df['user'].unique(), 0)
        self.sticker_counts = dict.fromkeys(df['user'].unique(), 0)
        self.audio_counts = dict.fromkeys(df['user'].unique(), 0)
        self.sentiment_scores = {user: {'positive': 0, 'negative': 0, 'neutral': 0} for user in df['user'].unique()}
        self.first_responder_counts = self.analyze_first_responders(df)

        for i, row in df.iterrows():
            message = row['message']
            user = row['user']

            if is_url(message):
                self.link_counts[user] += 1
            elif 'image omitted' in message:
                self.image_counts[user] += 1
            elif 'video omitted' in message:
                self.video_counts[user] += 1
            elif 'GIF omitted' in message:
                self.gif_counts[user] += 1
            elif 'sticker omitted' in message:
                self.sticker_counts[user] += 1
            elif 'audio omitted' in message:
                self.audio_counts[user] += 1



        # Sort the data
        self.link_counts = {k: v for k, v in sorted(self.link_counts.items(), key=lambda item: item[1], reverse=True)}
        self.image_counts = {k: v for k, v in sorted(self.image_counts.items(), key=lambda item: item[1], reverse=True)}
        self.video_counts = {k: v for k, v in sorted(self.video_counts.items(), key=lambda item: item[1], reverse=True)}
        self.gif_counts = {k: v for k, v in sorted(self.gif_counts.items(), key=lambda item: item[1], reverse=True)}
        self.sticker_counts = {k: v for k, v in sorted(self.sticker_counts.items(), key=lambda item: item[1], reverse=True)}
        self.audio_counts = {k: v for k, v in sorted(self.audio_counts.items(), key=lambda item: item[1], reverse=True)}

        df['Hour'] = df['date'].dt.hour
        self.hourly_message_counts = df.groupby('Hour').size().to_dict()

        self.analyze_sentiment(df)

    def analyze_sentiment(self, df):
        for i, row in df.iterrows():
            message = row['message']
            user = row['user']

            # Analyzing sentiment for each message
            sentiment_score = TextBlob(message).sentiment.polarity
            # if sentiment_score < -0.5:
            #     print(f"User: {user},  message: {message},  Score: {sentiment_score}")
            # Categorizing sentiment and incrementing corresponding count
            if sentiment_score > 0.001:
                self.sentiment_scores[user]['positive'] += 1
            elif sentiment_score < -0.001:
                self.sentiment_scores[user]['negative'] += 1
            else:
                self.sentiment_scores[user]['neutral'] += 1

    def analyze_first_responders(self, df):
        first_responder_counts = {user: {responder: 0 for responder in df['user'].unique() if responder != user} for
                                  user in df['user'].unique()}

        # Iterate through the DataFrame to find responses
        last_message_user = None
        for i, row in df.iterrows():
            current_user = row['user']

            # Check if the last message was from a different user
            if last_message_user is not None and current_user != last_message_user:
                first_responder_counts[last_message_user][current_user] += 1

            last_message_user = current_user

        return first_responder_counts


# Function to check if a string is a URL
def is_url(s):
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_pattern.match(s) is not None


def analyze_chat(file):
    df = chat_parser.read_chat(file)
    results = DataAnalyzer(df)
    return results

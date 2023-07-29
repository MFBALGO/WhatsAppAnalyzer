import pandas as pd
import re
import plotter
import chat_parser


class DataAnalyzer:
    def __init__(self, df):
        self.message_counts = df['user'].value_counts().to_dict()
        self.link_counts = dict.fromkeys(df['user'].unique(), 0)
        self.image_counts = dict.fromkeys(df['user'].unique(), 0)
        self.video_counts = dict.fromkeys(df['user'].unique(), 0)
        self.gif_counts = dict.fromkeys(df['user'].unique(), 0)
        self.sticker_counts = dict.fromkeys(df['user'].unique(), 0)
        self.audio_counts = dict.fromkeys(df['user'].unique(), 0)

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



# Function to check if a string is a URL
def is_url(s):
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_pattern.match(s) is not None


def analyze_chat(file):
    df = chat_parser.read_chat(file)
    results = DataAnalyzer(df)
    return results

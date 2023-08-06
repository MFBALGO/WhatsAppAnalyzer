import pandas as pd
import re
import plotter
import chat_parser
from textblob import TextBlob


class DataAnalyzer:
    def __init__(self, df, users_to_include=None, user_cap=50):
        # If users_to_include is None and user count exceeds cap, raise an error
        if users_to_include is None and len(df['user'].unique()) > user_cap:
            raise ValueError(f"Too many users. Please specify up to {user_cap} users to include.")

        # Filter DataFrame to include only specified users if provided
        if users_to_include is not None:
            df = df[df['user'].isin(users_to_include)]

        self.message_counts = df['user'].value_counts().to_dict()
        self.link_counts = dict.fromkeys(df['user'].unique(), 0)
        self.image_counts = dict.fromkeys(df['user'].unique(), 0)
        self.video_counts = dict.fromkeys(df['user'].unique(), 0)
        self.gif_counts = dict.fromkeys(df['user'].unique(), 0)
        self.sticker_counts = dict.fromkeys(df['user'].unique(), 0)
        self.audio_counts = dict.fromkeys(df['user'].unique(), 0)
        self.sentiment_scores = {user: {'positive': 0, 'negative': 0, 'neutral': 0} for user in df['user'].unique()}
        self.first_responder_counts = self.analyze_first_responders(df)
        self.hourly_activity = self.analyze_activity_by_hour(df)
        if self.extract_group_descriptions_with_timestamps(df) != None:
            self.group_description_changes = self.extract_group_descriptions_with_timestamps(df)

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


        df = df.copy()
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

    def analyze_activity_by_hour(self, df):
        # Group by user and hour, then count the messages
        hourly_activity = df.groupby(['user', df['date'].dt.hour]).size().unstack(fill_value=0)

        # Ensure all hours are present for each user
        for user in hourly_activity.index:
            for hour in range(24):
                if hour not in hourly_activity.columns:
                    hourly_activity.loc[user, hour] = 0

        # Sort the columns to make sure the hours are in order
        hourly_activity = hourly_activity[sorted(hourly_activity.columns)]

        # Convert to dictionary for consistency with other results
        return hourly_activity.to_dict(orient='index')

    def extract_group_descriptions_with_timestamps(self, df):
        # Regular expression pattern to match the group description change pattern
        pattern = r'changed the subject to “(.+?)”'
        regex = re.compile(pattern)

        # Lists to store extracted group descriptions and timestamps
        group_descriptions = []
        timestamps = []

        # Iterate through the messages and extract group descriptions and timestamps
        for date, message in zip(df['date'], df['message']):
            match = regex.search(message)
            if match:
                # Extract the group description and timestamp, add them to the lists
                description = match.group(1)
                group_descriptions.append(description)
                timestamps.append(pd.to_datetime(date))

        group_description_changes = list(zip(timestamps, group_descriptions))
        
        return group_description_changes




# Function to check if a string is a URL
def is_url(s):
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_pattern.match(s) is not None






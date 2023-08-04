import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
import os
import time
import matplotlib
import glob
import pandas as pd
from matplotlib.widgets import Slider
matplotlib.use('Agg')


def plot_data(data, title):
    # Set figure style
    sns.set(style="whitegrid")

    fig, ax = plt.subplots(figsize=(10, 6))  # Increase the size of the plot
    items = list(data.keys())
    counts = list(data.values())

    bars = ax.bar(items, counts, color=sns.color_palette("viridis", len(items)))  # Add color to the bars

    # Add labels and title
    ax.set_xlabel("Users", fontsize=14)
    ax.set_ylabel("Count", fontsize=14)
    ax.set_title(title, fontsize=16)

    # Increase the font size of the ticks
    ax.tick_params(labelsize=12)

    # Add a grid
    ax.grid(True)

    # Rotate x-axis labels
    plt.xticks(rotation=90)

    plt.tight_layout()
    plt.savefig(f'static/plots/{title}.png')
    plt.close()



def plot_results(results, identifier):
    # Delete old plots
    delete_old_plots()

    # Create a directory to store the plots
    os.makedirs('static/plots', exist_ok=True)

    # Plotting all data
    plot_data(results.message_counts, f'message_counts_{identifier}')
    plot_data(results.link_counts, f'link_counts_{identifier}')
    plot_data(results.image_counts, f'image_counts_{identifier}')
    plot_data(results.video_counts, f'video_counts_{identifier}')
    plot_data(results.gif_counts, f'gif_counts_{identifier}')
    plot_data(results.sticker_counts, f'sticker_counts_{identifier}')
    plot_data(results.audio_counts, f'audio_counts_{identifier}')
    plot_data(results.hourly_message_counts, f'hourly_message_counts_{identifier}')
    plot_sentiment_counts(results.sentiment_scores, identifier)
    plot_first_responder_counts(results.first_responder_counts, identifier)
    plot_hourly_activity(results.hourly_activity, identifier)

    # Extract the timestamps and descriptions from the results (assuming they are included in the results)
    description_changes = results.group_description_changes
    plot_description_timeline(description_changes, identifier)


def delete_old_plots():
    files = glob.glob('static/plots/*.png')
    for f in files:
        os.remove(f)


def plot_sentiment_counts(sentiment_counts, identifier):
    # Create DataFrame from sentiment_counts
    df_sentiment = pd.DataFrame.from_dict(sentiment_counts, orient='index').reset_index()
    df_sentiment.columns = ['User', 'Positive', 'Negative', 'Neutral']

    # Set figure style
    sns.set(style="whitegrid")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    df_sentiment.plot(kind='bar', x='User', stacked=True, ax=ax, colormap='viridis')

    # Add labels and title
    ax.set_xlabel("Users", fontsize=14)
    ax.set_ylabel("Count", fontsize=14)
    ax.set_title(f'Sentiment Counts {identifier}', fontsize=16)

    # Increase the font size of the ticks
    ax.tick_params(labelsize=12)

    # Rotate x-axis labels
    plt.xticks(rotation=90)

    plt.tight_layout()
    plt.savefig(f'static/plots/sentiment_scores_{identifier}.png')
    plt.close()


def plot_first_responder_counts(first_responder_counts, identifier):
    # Convert nested dictionary to DataFrame
    df_first_responders = pd.DataFrame.from_dict(first_responder_counts, orient='index')

    # Plot heat map
    plt.figure(figsize=(12, 8))
    sns.heatmap(df_first_responders, cmap='viridis')
    plt.title(f'First Responder Counts {identifier}')
    plt.tight_layout()
    plt.savefig(f'static/plots/first_responder_counts_{identifier}.png')
    plt.close()


def plot_hourly_activity(hourly_activity, identifier):
    plt.figure(figsize=(12, 8))

    # Plot a line for each user
    for user, activity in hourly_activity.items():
        plt.plot(list(range(24)), list(activity.values()), label=user)

    plt.xlabel('Hour of Day')
    plt.ylabel('Message Count')
    plt.title(f'Message Count Per User Per Hour {identifier}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'static/plots/hourly_activity_{identifier}.png')
    plt.close()




def plot_description_timeline(description_changes, identifier):
    timestamps, descriptions = zip(*description_changes)
    y_index = range(len(descriptions))

    # Create a figure and axis with increased size
    fig, ax = plt.subplots(figsize=(20, 10))

    # Plot the markers without lines connecting them
    ax.plot(timestamps, y_index, marker='o', color='blue', linestyle='None') # Note the 'None' linestyle

    # Add annotations with increased font size, and set the font family to support emojis and Arabic text
    for i, desc in enumerate(descriptions):
        ax.annotate(desc, (timestamps[i], y_index[i]), fontsize=12, family='Segoe UI Emoji')

    # Additional plot styling, such as setting labels, title, etc.
    # ...

    # Save the plot
    plt.tight_layout()
    plt.savefig(f'static/plots/group_description_changes_{identifier}.png', format='png')
    plt.close()





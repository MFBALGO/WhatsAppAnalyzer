import seaborn as sns
import matplotlib.pyplot as plt
import os
import time
import matplotlib
import glob
matplotlib.use('Agg')


def plot_data(data, title):


    # Set figure style
    sns.set(style="whitegrid")

    fig, ax = plt.subplots(figsize=(10, 6))  # Increase the size of the plot
    items = list(data.keys())
    counts = list(data.values())

    bars = ax.bar(items, counts, color=sns.color_palette("viridis", len(items)))  # Add color to the bars

    # Add labels and title
    ax.set_xlabel("Items", fontsize=14)
    ax.set_ylabel("Counts", fontsize=14)
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



def delete_old_plots():
    files = glob.glob('static/plots/*.png')
    for f in files:
        os.remove(f)




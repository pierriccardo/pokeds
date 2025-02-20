import os
import tyro
import consts
import logger
import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from dataclasses import dataclass
from db import DB

logger.setup()
logger = logging.getLogger(__name__)


custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(
    style="dark",
    palette="deep",
    context="paper",
    rc=custom_params
)

db = DB()
os.makedirs("imgs", exist_ok=True)


# --------------------------------------------------
# Plotting stats
# --------------------------------------------------
def plot_samples_per_ratings(data, dir="imgs/"):
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(x="Range", y="Count", data=data)
    ax.bar_label(ax.containers[0], fontsize=10)
    plt.xlabel("ELO Range")
    plt.ylabel("Num. of logs in the DB")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(dir, "samples_per_ratings"))


def plot_ratings_per_formats(data, title: str = "ratings_per_formats", dir="imgs/"):
    # Compute total logs per format
    total_per_format = data.groupby("Format")["Count"].sum()

    # Convert counts to percentages
    data["Percentage"] = data.apply(lambda row: (row["Count"] / total_per_format[row["Format"]]) * 100, axis=1)

    plt.figure(figsize=(10, 6))
    sns.barplot(x="Range", y="Percentage", hue="Format", data=data)
    plt.xticks(rotation=45)
    plt.title("Barplot of Counts by Range and Format")
    plt.xlabel("ELO Range")
    plt.ylabel("% Logs in the DB")
    plt.tight_layout()
    plt.savefig(os.path.join(dir, f"{title}.png"))


def plot_bar_samples_per_formats(data, title="all_samples_per_format", dir="imgs/"):
    plt.figure(figsize=(30, 5))
    ax = sns.barplot(x="Format", y="Count", data=data)
    ax.bar_label(ax.containers[0], fontsize=7)
    plt.xlabel("Battle Format")
    plt.ylabel("Num. of logs in the DB")
    plt.xticks(rotation=90, fontsize=7)
    ax.set_yscale('log')
    plt.tight_layout()
    plt.savefig(os.path.join(dir, f"bar_{title}"))


def plot_pie_samples_per_formats(data, title="all_samples_per_format", dir="imgs/", threshold=2000):
    """
    Plots a pie chart of sample counts per format. If a format has a count less than `threshold`,
    it is grouped into an "Other" category to reduce clutter.

    Parameters:
    - data: DataFrame with ["Format", "Count"]
    - title: Title for the saved image
    - dir: Directory to save the image
    - threshold: Minimum count required to appear separately (default=5)
    """

    # Group small counts into "Other"
    other_count = data[data["Count"] < threshold]["Count"].sum()
    filtered_data = data[data["Count"] >= threshold].copy()

    if other_count > 0:
        # Create a new row for the "Other" category
        other_data = pd.DataFrame({"Format": ["Other"], "Count": [other_count]})
        # Concatenate the "Other" data with the filtered_data
        filtered_data = pd.concat([filtered_data, other_data], ignore_index=True)

    # Plot the pie chart
    plt.figure(figsize=(10, 6))
    plt.pie(
        filtered_data["Count"],
        labels=filtered_data["Format"],
        autopct='%1.1f%%',  # Show percentages
        startangle=140,  # Rotate for better spacing
        wedgeprops={"edgecolor": "black"}  # Improve visibility
    )

    plt.title("Samples per Format")
    plt.tight_layout()

    # Save and show
    os.makedirs(dir, exist_ok=True)
    plt.savefig(os.path.join(dir, f"pie_{title}.png"))
    plt.show()


def gen_ranges(start, end, step):
    r = []
    for x in range(start, end, step):
        r.append((x, x + step))
    return r

if __name__ == "__main__":


    @dataclass
    class Args():
        plot: bool = False
        """Wheter to plot stats as images."""


    args = tyro.cli(Args)

    db.stats()

    if args.plot:
        step = 100
        ranges = [(x, x + step) for x in range(900, 2500, step)]

        all_samples_per_format = db.count_logs_by_format()
        plot_pie_samples_per_formats(all_samples_per_format, threshold=3000)
        plot_bar_samples_per_formats(all_samples_per_format)

        fix_samples_per_format = db.count_logs_by_format(formats=consts.FORMATS)
        plot_pie_samples_per_formats(fix_samples_per_format, title="samples_per_format", threshold=0)


        samples_per_ratings = db.count_logs_by_rating(ranges)
        plot_samples_per_ratings(samples_per_ratings)

        ratings_per_formats = db.count_logs_by_rating(ranges, formats=consts.FORMATS)
        plot_ratings_per_formats(ratings_per_formats)







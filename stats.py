import os
import consts
import logger
import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from db import DB

logger.setup()
logger = logging.getLogger(__name__)

sns.set_theme()
sns.set_palette("bright")


db = DB()
os.makedirs("imgs", exist_ok=True)


# --------------------------------------------------
# Plotting stats
# --------------------------------------------------
def plot_samples_per_rating(dir="imgs/"):
    ranges = gen_ranges(900, 2500, 100) # elo ranges
    counts = [db.count_logs_by_rating(r_min, r_max) for r_min, r_max in ranges]
    x = [f"{r_min}-{r_max}" for r_min, r_max in ranges]
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(x=x, y=counts)
    ax.bar_label(ax.containers[0], fontsize=10)
    plt.xlabel("ELO Range")
    plt.ylabel("Num. of logs in the DB")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(dir, "samples_per_rating"))


def plot_samples_per_format(dir="imgs/", min_samples: int = 200):
    formats, counts = db.count_logs_by_format()
    df = pd.DataFrame({"Format": formats, "Count": counts})
    df = df[df["Count"] > min_samples]
    df = df[df['Format'].isin(consts.FORMATS)]
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(x="Format", y="Count", data=df)
    ax.bar_label(ax.containers[0], fontsize=7)
    plt.xlabel("Format")
    plt.ylabel("Num. of logs in the DB")
    plt.xticks(rotation=90, fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(dir, "samples_per_format"))


def plot_elo_per_format():
    ranges = gen_ranges(900, 2500, 100) # elo ranges
    data = {"Range": [f"{start}-{end}" for start, end in ranges]}
    for f in consts.FORMATS:
        data[f] = [db.count_logs_by_rating(r_min, r_max, format=f) for r_min, r_max in ranges]
    df = pd.DataFrame(data)

    # Melt the DataFrame to long format for seaborn
    df = pd.melt(df, id_vars=["Range"], value_vars=consts.FORMATS, var_name="Format", value_name="Count")

    plt.figure(figsize=(10, 6))
    sns.barplot(x="Range", y="Count", hue="Format", data=df)
    plt.xticks(rotation=45)
    plt.title("Barplot of Counts by Range and Format")
    plt.tight_layout()
    plt.savefig(os.path.join("imgs/", "elo_per_format"))


def gen_ranges(start, end, step):
    r = []
    for x in range(start, end, step):
        r.append((x, x + step))
    return r

if __name__ == "__main__":
    db.stats()

    plot_samples_per_rating()
    plot_samples_per_format()
    plot_elo_per_format()






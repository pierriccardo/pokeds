import os
import logger
import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from db import DB

logger.setup()
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Plotting stats
# --------------------------------------------------
def plot_samples_per_rating(ranges, counts, dir="imgs/"):
    x = [f"{r_min}-{r_max}" for r_min, r_max in ranges]
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(x=x, y=counts)
    ax.bar_label(ax.containers[0], fontsize=10)
    plt.xlabel("ELO Range")
    plt.ylabel("Num. of logs in the DB")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(dir, "samples_per_rating"))


def plot_samples_per_format(formats, counts, dir="imgs/", min_samples: int = 200):
    df = pd.DataFrame({"Format": formats, "Count": counts})
    df = df[df["Count"] > min_samples]
    plt.figure(figsize=(15, 6))
    ax = sns.barplot(x="Format", y="Count", data=df)
    ax.bar_label(ax.containers[0], fontsize=7)
    plt.xlabel("Format")
    plt.ylabel("Num. of logs in the DB")
    plt.xticks(rotation=90, fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(dir, "samples_per_format"))


if __name__ == "__main__":
    db = DB()
    os.makedirs("imgs", exist_ok=True)

    db.stats()
    ranges = [
        (800, 900),
        (900, 1000),
        (1000, 1100),
        (1200, 1300),
        (1300, 1400),
        (1400, 1500),
        (1500, 1600),
        (1600, 1700),
        (1700, 1800),
        (1800, 1900),
        (1900, 2000),
        (2000, 2100),
        (2100, 2200),
        (2200, 2300),
        (2300, 2400),
        (2400, 2500),
    ]
    counts = [db.count_logs_by_rating(r_min, r_max) for r_min, r_max in ranges]
    plot_samples_per_rating(ranges, counts)
    formats, counts = db.count_logs_by_format()
    # print(formats)
    # print(counts)
    # print(f"len format {len(formats)} len conu {len(counts)}")
    plot_samples_per_format(formats, counts)

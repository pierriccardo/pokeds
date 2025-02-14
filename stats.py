import os
import logger
import seaborn as sns
import matplotlib.pyplot as plt

from db import DB

logger.setup()


# --------------------------------------------------
# Plotting stats
# --------------------------------------------------
def plot_samples_per_rating(ranges, counts, dir="imgs/"):
    x = [f"{r_min}-{r_max}" for r_min, r_max in ranges]
    plt.figure(figsize=(10, 5))
    sns.barplot(x=x, y=counts)
    plt.xlabel("ELO Range")
    plt.ylabel("Num. of logs in the DB")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(dir, "samples_per_rating"))


def plot_samples_per_format(formats, counts, dir="imgs/"):
    plt.figure(figsize=(15, 6))
    ax = sns.barplot(x=formats, y=counts)
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
        (1000, 1100),
        (1200, 1300),
        (1300, 1400),
        (1400, 1500),
        (1500, 1600),
        (1600, 1700),
        (1700, 1800),
        (1800, 1900),
    ]
    counts = [db.count_logs_by_rating(r_min, r_max) for r_min, r_max in ranges]
    plot_samples_per_rating(ranges, counts)
    formats, counts = db.count_logs_by_format()
    # print(formats)
    # print(counts)
    # print(f"len format {len(formats)} len conu {len(counts)}")
    plot_samples_per_format(formats, counts)

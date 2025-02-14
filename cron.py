import time
import tyro
import logger
import logging

from dataclasses import dataclass
from scraper import scrape_logs
from db import DB

logger.setup()
logger = logging.getLogger(__name__)


@dataclass
class Args:
    wait: int = 1000
    """Seconds to wait until next requests"""

    size: int = 10000000000
    """Max db size (in bytes), cron stop when reached"""


if __name__ == "__main__":
    args = tyro.cli(Args)
    db = DB()

    logger.info("Scraper started")
    db.stats()
    while True:
        if db.size() > args.size:
            break
        try:
            for log in scrape_logs():
                db.add(*log)
            logger.info(f"Waiting {args.wait}s for next call")
            db.stats()
            time.sleep(args.wait)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

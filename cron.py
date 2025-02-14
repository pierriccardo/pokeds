import time
import tyro
import logger
import consts
import logging

from dataclasses import dataclass
from scraper import scrape_recently_played_data, scrape_log, scrape_search_data
from db import DB


@dataclass
class Args:
    wait: int = 1000
    """Seconds to wait until next requests"""

    size: int = 10000000000
    """Max db size (in bytes), cron stop when reached"""

    type: str = "recent"
    """
    Type of scraping to perform, available:
    - recent: run indefinitely and save recently played
    - format: save by format (formats configured in const.py)
    - player: tbd

    """

    level: int = 20
    """Logging level. Default INFO"""

args = tyro.cli(Args)


logger.setup(args.level)
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    db = DB()

    logger.info("Scraper started")
    db.stats()

    match args.type:

        case "recent":
            while True:
                if db.size() > args.size:
                    logger.warning("Database has reached maximum size - terminating cron")
                    break
                try:
                    replays = scrape_recently_played_data()
                    for r in replays:
                        if not db.exists(r.id):
                            db.add(
                                r.id,
                                r.format,
                                r.rating,
                                scrape_log(r.id)
                            )
                    logger.info(f"Waiting {args.wait}s for next call")
                    db.stats()
                    time.sleep(args.wait)

                except Exception as e:
                    logger.error(f"An unexpected error occurred: {e}")

        case "format":
            for f in consts.FORMATS:

                if db.size() > args.size:
                    logger.warning("Database has reached maximum size - terminating cron")
                    break

                try:
                    replays = scrape_search_data(f)
                    new = 0
                    for r in replays:
                        if not db.exists(r.id):
                            db.add(
                                r.id,
                                r.format,
                                r.rating,
                                scrape_log(r.id)
                            )
                            new += 1
                    logging.info(f"Added {new} new replays to DB")
                    db.stats()

                except Exception as e:
                    logger.error(f"An unexpected error occurred: {e}")
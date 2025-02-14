import time
import tyro
import logger
import consts
import logging
import schedule
import threading

from dataclasses import dataclass
from scraper import scrape_recents, scrape_formats, scrape_players, scrape_log
from db import DB


@dataclass
class Wait:
    #add_log: int = 10 # seconds
    recents: int = 10 # seconds
    formats: int = 600 # seconds
    players: int = 600 # seconds


@dataclass
class Args:
    wait: Wait
    """Seconds to wait until next requests"""

    size: int = 10000000000
    """Max db size (in bytes), cron stop when reached"""

    level: int = 20
    """Logging level. Default INFO"""

args = tyro.cli(Args)


logger.setup(args.level)
logger = logging.getLogger(__name__)


db = DB()


# global list of replays that is filled asynchronously
# each replay has a battle-id, a format and a rating
# the script loops forever and add replays if there are any
# scheduled jobs fill asyncronously the replays list
replays = []
replays_lock = threading.Lock()

def _scrape_recents():
    new_replays = scrape_recents()
    replays.extend(new_replays)


def _scrape_formats():
    new_replays = scrape_formats()
    replays.extend(new_replays)


def _scrape_players():
    new_replays = scrape_players()
    replays.extend(new_replays)

def add_logs():
    while replays:
        with replays_lock:
            r = replays.pop()
            if not db.exists(r.id):
                db.add(r.id, r.format, r.rating, scrape_log(r.id))


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

# run once, then run with scheduler
_scrape_recents()
_scrape_formats()
_scrape_players()

schedule.every(10).seconds.do(run_threaded, add_logs)
schedule.every(args.wait.recents).seconds.do(run_threaded, _scrape_recents)
schedule.every(args.wait.formats).seconds.do(run_threaded, _scrape_formats)
schedule.every(args.wait.players).seconds.do(run_threaded, _scrape_players)


if __name__ == "__main__":

    logger.info("Scraper started")
    db.stats()

    while True:
        logger.debug(f"Number of Replays to add {len(replays)}")

        schedule.run_pending()
        if db.size() > args.size:
            logger.warning("Database has reached maximum size - terminating cron")
            break
        time.sleep(1)

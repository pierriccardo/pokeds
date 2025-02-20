import time
import tyro
import logger
import consts
import logging
import schedule
import threading

from dataclasses import dataclass
from scraper import scrape_log, scrape_recents, scrape_formats, scrape_ladders, scrape_members, scrape_roomlst
from db import DB


@dataclass
class Wait:
    addlogs: int = 10 # seconds
    recents: int = 60 # seconds
    formats: int = 7200 # seconds
    ladders: int = 7200 # seconds
    members: int = 1800 # seconds
    roomlst: int = 300 # seconds


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
    logger.info(f"Starting job in thread: {threading.current_thread().name}")
    new_replays = scrape_recents()
    with replays_lock:
        replays.extend(new_replays)


def _scrape_formats():
    logger.info(f"Starting job in thread: {threading.current_thread().name}")
    new_replays = scrape_formats()
    with replays_lock:
        replays.extend(new_replays)


def _scrape_ladders():
    logger.info(f"Starting job in thread: {threading.current_thread().name}")
    new_replays = scrape_ladders()
    with replays_lock:
        replays.extend(new_replays)


def _scrape_members():
    logger.info(f"Starting job in thread: {threading.current_thread().name}")
    new_replays = scrape_members()
    with replays_lock:
        replays.extend(new_replays)


def _scrape_roomlst():
    logger.info(f"Starting job in thread: {threading.current_thread().name}")
    new_replays = scrape_roomlst()
    with replays_lock:
        replays.extend(new_replays)


def add_logs():
    while True:
        with replays_lock:
            if not replays:
                return
            r = replays.pop()
        if not db.exists(r.id):
            db.add(r.id, r.format, r.rating, scrape_log(r.id))


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.daemon = True  # Daemon thread to ensure it doesn't block program termination
    job_thread.start()

# run once, then run with scheduler
run_threaded(_scrape_recents)
run_threaded(_scrape_formats)
run_threaded(_scrape_ladders)
run_threaded(_scrape_members)
run_threaded(_scrape_roomlst)


schedule.every(args.wait.addlogs).seconds.do(run_threaded, add_logs)
schedule.every(args.wait.recents).seconds.do(run_threaded, _scrape_recents)
schedule.every(args.wait.formats).seconds.do(run_threaded, _scrape_formats)
schedule.every(args.wait.ladders).seconds.do(run_threaded, _scrape_ladders)
schedule.every(args.wait.members).seconds.do(run_threaded, _scrape_members)
schedule.every(args.wait.roomlst).seconds.do(run_threaded, _scrape_roomlst)


if __name__ == "__main__":

    logger.info("Scraper started")
    db.stats()

    while True:
        schedule.run_pending()
        if db.size() > args.size:
            logger.warning("Database has reached maximum size - terminating cron")
            break
        time.sleep(1)

import os
import json
import time
import consts
import logging
import requests
import functools
from dataclasses import dataclass
from consts import to_compact_notation

@dataclass(init=True)
class Replay:
    id: str
    format: str
    rating: int

logger = logging.getLogger(__name__)

URL = "https://replay.pokemonshowdown.com"


def handle_request_exceptions(func):
    """Decorator to handle request-related exceptions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.Timeout:
            logger.error("The request timed out.")
        except requests.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
        except ConnectionError:
            logger.error("There was a connection error.")
        except requests.RequestException as err:
            logger.error(f"An error occurred: {err}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        return None  # Return None or an appropriate fallback value

    return wrapper


@handle_request_exceptions
def scrape_log(id: str, wait: float = .05):
    """
    Retrieve the text log realted to battle id passed as argument.
    When used in a loop, might be necessary waiting some time.
    - id: battle id, a string of this form <format>-<battle-id>
    - wait: time between sequential requests
    """
    logger.debug(f"Requesting log id ({id}) json")
    response = requests.get(f"{URL}/{id}.log")
    response.raise_for_status()  # raises errors
    logger.debug(f"Succesfully retrieved log id {id} json")
    time.sleep(wait)
    return response.text  # return the log


@handle_request_exceptions
def scrape_recents():
    """
    Scrape recently played data and return a list of replay.
    Each replay contains an id (in form of <format>-<battle-id>)
    the format of the battle and the rating.
    """
    replays = []

    logger.debug("Requesting replay json")
    response = requests.get(f"{URL}/search.json?")
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
    logger.debug("Succesfully retrieved json, scraping each log")

    data = response.json()
    for d in data:
        replays.append(Replay(d["id"], d["format"], d["rating"]))
    return replays


def scrape_formats():
    for format in consts.FORMATS:
        replays = []
        logger.debug(f"Requesting replays with format {format}")
        for page in range(1, 101):
            logger.debug(f"Requesting replays for page {page} with format {format}")
            url = f"{URL}/search.json?format={format}&page={page}"
            logger.debug(f"Sending request")
            response = requests.get(url)
            response.raise_for_status()
            logger.debug("Succesfully retrieved json")

            data = response.json()

            for d in data:
                replays.append(Replay(d["id"], d["format"], d["rating"]))

            logger.info(f"Found {len(replays)} replays with format {format}")

    return replays


@handle_request_exceptions
def scrape_ladder_usernames(format: str):

    logger.info(f"Scraping ladder for {format} format")
    url = f'https://pokemonshowdown.com/ladder/{format}.json'

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    usernames = [entry['username'] for entry in data['toplist']]
    logger.info(f"Found {len(usernames)} for {format} format")
    return usernames


@handle_request_exceptions
def scrape_players():
    for format in consts.FORMATS:
        replays = []
        compact_format = to_compact_notation(format)
        logger.info(f"Requesting player data for format {compact_format}")
        players = scrape_ladder_usernames(compact_format)
        for player in players:
            logger.debug(f"Requesting replays with player {player} format {format}")
            url = f"{URL}/search.json?user={player}&format={format}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            for d in data:
                replays.append(Replay(d["id"], d["format"], d["rating"]))

            logger.info(f"Found {len(data)} replays for player {player} with format {format}")
        logger.info(f"Total replays found {len(replays)}")

    return replays
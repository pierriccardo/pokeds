import os
import json
import time
import logging
import requests
from dataclasses import dataclass


@dataclass(init=True)
class Replay:
    id: str
    format: str
    rating: int

logger = logging.getLogger(__name__)

URL = "https://replay.pokemonshowdown.com"


def scrape_log(id: str, wait: float = .05):
    """
    Retrieve the text log realted to battle id passed as argument.
    When used in a loop, might be necessary waiting some time.
    - id: battle id, a string of this form <format>-<battle-id>
    - wait: time between sequential requests
    """
    try:
        logger.debug(f"Requesting log id ({id}) json")
        response = requests.get(f"{URL}/{id}.log")
        response.raise_for_status()  # raises errors
        logger.debug(f"Succesfully retrieved log id {id} json")
        time.sleep(wait)
        return response.text  # return the log

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


def scrape_recently_played_data():
    """
    Scrape recently played data and return a list of replay.
    Each replay contains an id (in form of <format>-<battle-id>)
    the format of the battle and the rating.
    """
    replays = []
    try:
        logger.debug("Requesting replay json")
        response = requests.get(f"{URL}/search.json?")
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        logger.debug("Succesfully retrieved json, scraping each log")

        data = response.json()
        for d in data:
            replays.append(Replay(d["id"], d["format"], d["rating"]))
        return replays

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


def scrape_search_data(format: str = "[Gen 1] Random Battle"):
    replays = []
    try:
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


import os
import json
import time
import logging
import requests

logger = logging.getLogger(__name__)

URL = "https://replay.pokemonshowdown.com"


def scrape_logs():
    try:
        logger.debug("Requesting replay json")
        response = requests.get(f"{URL}/search.json?")
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        logger.debug("Succesfully retrieved json, scraping each log")

        data = response.json()
        for d in data:
            logger.debug(f"Requesting log id ({d['id']}) json")
            response = requests.get(f"{URL}/{d['id']}.log")
            response.raise_for_status()  # raises errors
            logger.debug(f"Succesfully retrieved log id ({d['id']}) json")
            yield (d["id"], d["format"], d["rating"], response.text)  # log
            time.sleep(1)

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

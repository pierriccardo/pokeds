import os
import json
import time
import consts
import logging
import random
import requests
import functools
import subprocess

from dataclasses import dataclass
from consts import to_compact_notation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

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


# --------------------------------------------------
# Scraping Sources
# --------------------------------------------------
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


@handle_request_exceptions
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
def scrape_ladders():
    for format in consts.FORMATS:
        replays = []
        compact_format = to_compact_notation(format)
        logger.info(f"Requesting player data for format {compact_format}")
        players = scrape_ladders_usernames(compact_format)
        for player in players:
            logger.debug(f"Requesting replays with player {player} format {format}")
            url = f"{URL}/search.json?user={player}&format={format}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            for d in data:
                replays.append(Replay(d["id"], d["format"], d["rating"]))

        logger.info(f"Found {len(replays)} replays with format {format} from ladders")

    return replays


@handle_request_exceptions
def scrape_members():
    players = scrape_members_usernames()
    replays = []

    for format in consts.FORMATS:
        for player in players:
            logger.debug(f"Requesting replays with player {player} format {format}")
            url = f"{URL}/search.json?user={player}&format={format}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            for d in data:
                replays.append(Replay(d["id"], d["format"], d["rating"]))

        logger.info(f"Found {len(replays)} replays with format {format} from members")

    return replays


def scrape_roomlst():
    players = []
    replays = []
    room = random.choice(consts.ROOMLIST)
    logger.info(f"Requesting usernames for room {room}")
    new_players = scrape_roomlist_usernames(room)
    players.extend(new_players)

    for format in consts.FORMATS:
        for player in players:
            logger.debug(f"Requesting replays with player {player} format {format}")
            url = f"{URL}/search.json?user={player}&format={format}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            for d in data:
                replays.append(Replay(d["id"], d["format"], d["rating"]))

        logger.info(f"Found {len(replays)} replays with format {format} from {room}")

    return replays





# --------------------------------------------------
# Username Scrapers
# --------------------------------------------------
@handle_request_exceptions
def scrape_ladders_usernames(format: str):

    logger.info(f"Scraping ladder for {format} format")
    url = f'https://pokemonshowdown.com/ladder/{format}.json'

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    usernames = [entry['username'] for entry in data['toplist']]
    logger.info(f"Found {len(usernames)} for {format} format")
    return usernames


def scrape_members_usernames():
    os.makedirs("tmp", exist_ok=True)
    logging.info(f"Checking chrome installed")

    if not os.path.exists(f"{os.getcwd()}/tmp/chrome-extracted"):
        subprocess.run(["wget", "-P", f"{os.getcwd()}/tmp", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"])
        subprocess.run(["dpkg-deb", "-x", f"{os.getcwd()}/tmp/google-chrome-stable_current_amd64.deb", f"{os.getcwd()}/tmp/chrome-extracted/"])

    # Set up headless Chrome options
    chrome_options = Options()
    chrome_options.binary_location = f"{os.getcwd()}/tmp/chrome-extracted/opt/google/chrome/google-chrome"
    #chrome_options.add_argument(f"--user-data-dir={os.getcwd()}/tmp/chrome-user-data")
    chrome_options.add_argument("--headless")  # Ensure the browser runs in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")

    try:
        # Set up the Chrome browser
        driver = webdriver.Chrome(options=chrome_options)
        usernames = []
        for page in range(1, 10):
            retries = consts.RETRIES
            for retry in range(retries):
                try:
                    url = f'https://www.smogon.com/forums/online/?type=member&{page}'
                    driver.get(url)
                    driver.implicitly_wait(2)

                    # retrieve all username on the page
                    wait = WebDriverWait(driver, random.uniform(5, 10))  # Explicit wait
                    elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'username')))
                    usernames.extend([e.text for e in elements])
                except StaleElementReferenceException as s:
                    logging.error(f"Retry {retry} Error {s}")
                    time.sleep(1)  # Short wait before retrying

        logging.info(f"Found {len(usernames)} online members")

        driver.quit()
        return usernames
    except Exception as e:
        logging.error(f"Error on selenium webdriver: {e}")
        return []


def scrape_roomlist_usernames(room_name: str = "lobby"):
    os.makedirs("tmp", exist_ok=True)
    logging.info("Checking if Chrome is installed")

    # Install Chrome if not available
    if not os.path.exists(f"{os.getcwd()}/tmp/chrome-extracted"):
        subprocess.run(["wget", "-P", f"{os.getcwd()}/tmp", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"])
        subprocess.run(["dpkg-deb", "-x", f"{os.getcwd()}/tmp/google-chrome-stable_current_amd64.deb", f"{os.getcwd()}/tmp/chrome-extracted/"])

    # Set up headless Chrome options
    chrome_options = Options()
    chrome_options.binary_location = f"{os.getcwd()}/tmp/chrome-extracted/opt/google/chrome/google-chrome"
    #chrome_options.add_argument(f"--user-data-dir={os.getcwd()}/tmp/chrome-user-data")
    chrome_options.add_argument("--headless")  # Runs Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")

    usernames = []
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://play.pokemonshowdown.com/")
        wait = WebDriverWait(driver, random.uniform(10, 15))  # Explicit wait
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))) # Ensure the page loads
        logging.info("Pokémon Showdown page loaded successfully.")

    except Exception as e:
        logging.error(f"Error with Selenium WebDriver: {e}")
        return []

    try:
        lobby_link = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[@class='roomlist']//a[@href='/{room_name}'][contains(@class, 'blocklink')]")))
        #time.sleep(1.45)
        driver.execute_script("arguments[0].click();", lobby_link)
        logging.info(f"Clicked {room_name} link")

    except Exception as e:
        logging.warning(f"{room_name} link not found or already open: {e}")

    try:
        # find all <li> elements containing the buttons with usernames and return them
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//li/button[@class="userbutton username"]')))
        retries = consts.RETRIES
        for retry in range(retries):
            try:
                list_items = driver.find_elements(By.XPATH, '//li/button[@class="userbutton username"]')
                usernames = [item.get_attribute("data-name") for item in list_items]
                logging.info(f"Found {len(usernames)} users in the {room_name}")
                return usernames
            except StaleElementReferenceException as s:
                logging.error(f"Retry {retry} Error {s}")
                time.sleep(1)  # Short wait before retrying
        return []

    except Exception as e:
        logging.error(f"Error finding user list: {e}")

    driver.quit()
    return usernames





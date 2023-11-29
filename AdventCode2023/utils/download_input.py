import os
import sys
from datetime import datetime, timedelta
from time import sleep
from log import MyLogger
import requests

logger = MyLogger(log_file="aoc2023.log", log_path="logs", name=__name__)


def start_session():
    return requests.Session()


def retrieve_cookie(env_name="AOC_SESSION"):
    if not os.getenv(env_name):
        logger.error(
            "AOC_SESSION env variable missing, should contain the session cookie"
        )
        sys.exit(1)
    return os.getenv(env_name)


def retrieve_user(env_name="AOC_USER"):
    if not os.getenv(env_name):
        logger.error("AOC_USER env variable missing, should contain the user id")
        sys.exit(1)
    return os.getenv(env_name)


def valid_status(r):
    if r.status_code != 200:
        logger.error(f"Error in request from {r.url}: status = {r.status_code}")
        logger.debug(
            "Possible reason is missing / invalid session cookie, expected as variable AOC_SESSION"
        )
        sys.exit(1)
    if "identify yourself" in r.text.lower():
        logger.error("Identification needed for server.")
        logger.debug(
            "Possible reason is missing / invalid session cookie, expected as variable AOC_SESSION"
        )
        sys.exit(1)
    logger.info("Valid response obtained")
    logger.debug(r.text[0:50] + "...")


def config_day():
    if YEAR == -1 and DAY == -1:
        now = datetime.utcnow() + timedelta(hours=-5)
        year, month, day = now.year, now.month, now.day

        if month != 12 or day > 25:
            logger.error(
                "`YEAR` and `DAY` not set, defaults revert to today and today is not Dec 1-25\n"
            )
            sys.exit(1)

        setup(year, day)
    else:
        setup(YEAR, DAY)


def setup(year, day):
    global YEAR
    global DAY

    if not (year >= 2020 and 1 <= day <= 25):
        logger.error("Invalid `YEAR` and/or `DAY` provided!\n")
        sys.exit(1)

    YEAR = year
    DAY = day
    cookie = retrieve_cookie()
    session.cookies.set("session", cookie)


def download_input(filename=None, session=None):
    if not session:
        session = start_session()
    config_day()
    logger.debug(f"Configured to run as year: {YEAR} and day: {DAY}")

    if not os.path.isdir(DOWNLOAD_FOLDER):
        try:
            os.mkdir(DOWNLOAD_FOLDER)
            logger.info(f"Download folder created: {DOWNLOAD_FOLDER}")
        except Exception as e:
            logger.error("Could not create download folder {DOWNLOAD_FOLDER}")
            logger.error(str(e))
            sys.exit(1)

    r = session.get(URL.format(YEAR, DAY, "input"))
    valid_status(r)
    if not filename:
        filename = os.path.join(DOWNLOAD_FOLDER, f"{YEAR}__{DAY}.txt")
    with open(filename, "wb") as f:
        f.write(r.content)
    logger.info(f"Input saved to {filename}")


URL = "https://adventofcode.com/{:d}/day/{:d}/{:s}"
YEAR = -1
DAY = -1
DOWNLOAD_FOLDER = "./inputs"
AOC_USER = os.getenv("AOC_USER")
AOC_EMAIL = os.getenv("AOC_EMAIL")
AOC_USER_AGENT = os.getenv("AOC_USER_AGENT")
# AOC_SESSION = os.getenv('AOC_SESSION')

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-y",
        "--year",
        help="Which AOC year are you trying to download?",
        required=False,
        default=-1,
    )
    parser.add_argument(
        "-d",
        "--day",
        help="Which AOC day are you trying to download?",
        required=False,
        default=-1,
    )
    namespace = parser.parse_args()
    YEAR = int(namespace.year)
    DAY = int(namespace.day)
    session = requests.Session()
    session.headers.update({"User-Agent": AOC_USER_AGENT, "From": AOC_EMAIL})
    download_input(session=session)

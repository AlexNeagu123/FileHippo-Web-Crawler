import json
import logging

from config import configure_logger, cache_file

cache = dict()
logger = logging.getLogger(__name__)
configure_logger(logger)


def extract_cache():
    global cache
    try:
        with open(cache_file, "r") as fp:
            cache = json.load(fp)
    except Exception as err:
        logger.exception(str(err))


def update_cache():
    try:
        global cache
        with open(cache_file, "w") as fp:
            json.dump(cache, fp, indent=4)
    except Exception as err:
        logger.exception(str(err))

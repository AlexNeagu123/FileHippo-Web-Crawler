import logging
import peewee
import re


def check_md5(md5):
    is_md5 = re.findall(r"([a-fA-F\d]{32})", md5)
    if is_md5:
        return True
    return False


def configure_logger(logger):
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('log_file.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def response_object(data_found):
    return {
        "Message": "Found",
        "Data": data_found
    }


db = peewee.PostgresqlDatabase(
    'my_database',
    user='postgres',
    password='crawler_2022'
)

db_fields = ["Name", "Version", "DateAdded", "Languages", "DownloadLink", "Size", "Filename", "sha256"]

not_found = {
    "Message": "Not Found",
    "Data": {}
}

ok_status = {
    "Message": "ok"
}




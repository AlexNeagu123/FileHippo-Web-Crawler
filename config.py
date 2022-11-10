import logging

main_url = "https://filehippo.com"
cache_file = r"C:\Repos\crawler_project\cache.json"
db_fields = ["Name", "Version", "Date Added", "Languages", "Final Download Link", "Size", "Filename"]
all_products = list()
req_count = 0
database_type = '?'
db_connection = None


def configure_logger(logger):
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('log_file.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

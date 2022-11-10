import urllib.request
import urllib.parse
import urllib.error
import re
import logging
import os
import time

import my_cache
import my_database
import peewee_database
import config

logger = logging.getLogger(__name__)
config.configure_logger(logger)


while config.database_type != 'sqlite3' and config.database_type != 'psycopg' and config.database_type != 'peewee':
    config.database_type = input('Enter the database mode you want [sqlite3 | psycopg | peewee]: ')

if config.database_type == 'sqlite3':
    config.db_connection = my_database.SqliteDB(
        db_type='sqlite3', db_name='products', db_path=r'C:\Repos\crawler_project'
    )
elif config.database_type == 'psycopg':
    config.db_connection = my_database.PostgresDB(
        db_type='postgres', db_name='my_database', db_user='postgres', db_password='crawler_2022'
    )
else:
    peewee_database.db.connect()
    peewee_database.db.create_tables([peewee_database.Product])


def update_count(requested_url):
    if config.req_count >= 10:
        terminate_program()
    config.req_count += 1
    if config.req_count % 20 == 0:
        time.sleep(0.1)
    logger.info("Request #{}. {}".format(config.req_count, requested_url))


def find_name(data):
    name_obj = re.compile(r'<h1*.?class="program-header__name".*?>(.*?)</h1>')
    name = name_obj.findall(data)
    if len(name) == 0:
        return None
    return name[0]


def find_version(data):
    version_obj = re.compile(r'<p.*?class="program-header__version".*?>(.*?)</p>')
    version = version_obj.findall(data)
    if len(version) == 0:
        return None
    return version[0]


def find_languages(data):
    languages_obj = re.compile(r'<li.*?class="program-technical__item".*?data-qa="program-technical-available-languages".*?>(.*?)</li>')
    languages = languages_obj.findall(data)
    return languages


def find_date_added(data):
    date_obj = re.compile(r'Date added:.*?<dd.*?data-qa="program-technical-date">(.*?)</dd>')
    date_added = date_obj.findall(data)
    if len(date_added) == 0:
        return None
    return date_added[0]


def find_download_link(data):
    download_obj = re.compile(r'class="program-actions-header__download".*?<a[^>]*title="[^"]*"[^>]*href="(.*?)"')
    download_link = download_obj.findall(data)
    if len(download_link) == 0:
        return None
    return download_link[0]


def find_filename(data):
    base = os.path.basename(data)
    filename = re.findall('&Filename=(.*)', base)
    if len(filename) == 0:
        return None
    return filename[0]


def find_size(headers):
    if "Content-Length" not in headers.keys():
        return None
    value = headers["Content-Length"]
    return value


def find_real_download_link(data):
    regex_object = re.compile(r"downloadIframe\.src = '(.*?)'")
    found = regex_object.findall(data)
    if len(found) == 0:
        return None
    return found[0]


def product_parse(data):
    product_data = {
        "Name": find_name(data),
        "Version": find_version(data),
        "Languages": find_languages(data),
        "Date Added": find_date_added(data)
    }
    raw_link = find_download_link(data)
    update_count(raw_link)

    if raw_link is None:
        return product_data

    try:

        with urllib.request.urlopen(raw_link) as post_download_response:
            actual_link = find_real_download_link(str(post_download_response.read().decode()))
            if actual_link is None:
                return product_data
            update_count(actual_link)

            with urllib.request.urlopen(actual_link) as real_download_response:
                headers = dict(real_download_response.headers)
                product_data.update({"Final Download Link": real_download_response.url})
                product_data.update({"Size": find_size(headers)})
                product_data.update({"Filename": find_filename(real_download_response.url)})

    except urllib.error.HTTPError:
        logger.warning("Not allowed to access download link for this product")
    except Exception as err:
        logger.exception(err)

    return product_data


def page_parse(data):
    name_obj = re.compile(
        r'class="button card-program__button card-program__button--download button--secondary".*?title="(.*?)"'
    )
    products = name_obj.findall(data)
    product_links = list()

    for product in products:
        link_obj = re.compile(r'<a.*?title="' + re.escape(product) + r'".*?href="(.*?)"')
        link = link_obj.findall(data)
        if len(link) > 0:
            product_links.append(link[0])

    return product_links


def explore_products(subcategory_url):
    product_links = list()
    for i in range(1, 2):
        needed_url = subcategory_url + str(i)
        if needed_url not in my_cache.cache:
            update_count(needed_url)
            with urllib.request.urlopen(needed_url) as page_content:
                my_cache.cache[needed_url] = str(page_content.read().decode("UTF-8"))

        current_page = my_cache.cache[needed_url]
        product_links += page_parse(current_page)

    for url in product_links:
        if url not in my_cache.cache:
            update_count(url)
            with urllib.request.urlopen(url) as product_content:
                prod_info = product_parse(str(product_content.read().decode("UTF-8")))
                my_cache.cache[url] = prod_info
        product_info = my_cache.cache[url]
        config.all_products.append(product_info)


def explore_subcategories(data):
    subcategories_obj = re.compile(r'href="([^"]*)"[^>]*data-qa="sub-categories-list-item"')
    subcategories = subcategories_obj.findall(data)
    for subcategory in subcategories:
        explore_products(subcategory)


def explore_categories(data):
    categories_obj = re.compile(r'<a title="[^"]*" data-qa="categories-list-link"[^>]*href=\"(.*?)"')
    categories = categories_obj.findall(data)

    for category in categories:
        if category not in my_cache.cache:
            update_count(category)
            with urllib.request.urlopen(category) as category_content:
                my_cache.cache[category] = str(category_content.read().decode("UTF-8"))

        current_category = my_cache.cache[category]
        explore_subcategories(current_category)


def update_database():
    for product in config.all_products:
        for key in config.db_fields:
            if key not in product.keys():
                product[key] = None

        if config.database_type == 'peewee':
            if not peewee_database.find_product(product):
                peewee_database.insert_product(product)
        else:
            if not config.db_connection.find_product(product):
                config.db_connection.insert_product(product)


def terminate_program():
    logger.warning("Request Limit of 100 achieved")
    update_database()
    my_cache.update_cache()
    if config.database_type == 'peewee':
        peewee_database.db.close()
    quit()


if __name__ == '__main__':
    my_cache.extract_cache()
    try:
        if config.main_url not in my_cache.cache:
            update_count(config.main_url)
            with urllib.request.urlopen(config.main_url) as main_content:
                my_cache.cache[config.main_url] = str(main_content.read().decode("UTF-8"))

        main_page = my_cache.cache[config.main_url]
        explore_categories(main_page)
    except Exception as e:
        logger.exception(e)

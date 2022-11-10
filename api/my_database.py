import peewee
import logging

import api_exceptions
import config

logger = logging.getLogger(__name__)
config.configure_logger(logger)


class Product(peewee.Model):
    Name = peewee.TextField()
    Version = peewee.TextField(null=True)
    DateAdded = peewee.TextField(null=True)
    Languages = peewee.TextField(null=True)
    DownloadLink = peewee.TextField(null=True)
    Size = peewee.IntegerField(null=True)
    Filename = peewee.TextField(null=True)
    md5 = peewee.TextField()
    sha256 = peewee.TextField()

    class Meta:
        database = config.db
        db_table = 'peewee_products'


def serialize_db_response(response_obj):
    serial_response = {
        "Name": response_obj.Name,
        "Version": response_obj.Version,
        "DateAdded": response_obj.DateAdded,
        "Languages": response_obj.Languages,
        "DownloadLink": response_obj.DownloadLink,
        "Size": response_obj.Size,
        "Filename": response_obj.Filename,
        "sha256": response_obj.sha256
    }
    return serial_response


def find_links():
    logger.info("All links are searched")
    # Find all download links in the database
    try:
        links_query = Product.select(Product.DownloadLink)
        links_list = []
        for link_found in links_query:
            links_list.append(link_found.DownloadLink)
        return config.response_object(links_list)
    except Exception as database_error:
        return api_exceptions.database_error


def find_md5(md5):
    logger.info("md5 - {} is searched".format(md5))
    # Check if there are products matching the md5
    try:
        data = Product.get(Product.md5 == md5)
        serialized_data = serialize_db_response(data)
        return config.response_object(serialized_data)
    except peewee.DoesNotExist:
        return config.not_found


def find_download_link(link):
    logger.info("Download Link - {} is searched".format(link))
    try:
        Product.get(Product.DownloadLink == link)
        return config.ok_status
    except peewee.DoesNotExist:
        return config.not_found


def find_first_character(first_character):
    logger.info("first letter {} is searched".format(first_character))
    products_matching = dict()
    like_format = "{}%".format(first_character)

    # Find products matching the pattern
    query = Product.select().where(Product.Name ** like_format)
    for product in query:
        products_matching.update({
                product.Name: serialize_db_response(product)
        })

    # Check if there are products matching the pattern
    if len(products_matching):
        return config.response_object(products_matching)

    return config.not_found


def insert_single_product(product_inserted, product_md5):
    try:
        product_added = Product(**product_inserted, md5=product_md5)
        product_added.save()
    except Exception as database_error:
        logger.exception(database_error)
        return api_exceptions.database_error

    logger.info("Product Added To The Database: {}".format(product_inserted["Name"]))
    return config.ok_status


def update_single_product(fields_updated, product_md5=None, product_link=None):
    try:
        rows_updated = None
        if product_md5:
            rows_updated = Product.update(**fields_updated).where(Product.md5 == product_md5).execute()
        elif product_link:
            rows_updated = Product.update(**fields_updated).where(Product.DownloadLink == product_link).execute()
        logger.info(rows_updated)
    except Exception as database_error:
        logger.exception(database_error)
        return api_exceptions.database_error

    if product_md5:
        logger.info("Product with md5 = {} has been updated".format(product_md5))
    elif product_link:
        logger.info("Product with download link = {} has been updated".format(product_link))

    return config.ok_status


def delete_single_product(product_md5):
    try:
        product_deleted = Product.get(Product.md5 == product_md5)
        product_deleted.delete_instance()
    except Exception as database_error:
        logger.exception(database_error)
        return api_exceptions.database_error

    logger.info("Product with md5 = {} has been deleted".format(product_md5))
    return config.ok_status

import logging
import json
import api_exceptions
from flask import Flask, request, jsonify

import config
import my_database

config.db.connect()
app = Flask(__name__)
logger = logging.getLogger(__name__)
config.configure_logger(logger)


def find_md5(md5):
    try:
        if not config.check_md5(md5):
            return api_exceptions.invalid_md5
        product_found = my_database.find_md5(md5)
        return product_found
    except Exception as e:
        logger.exception(e)
        return api_exceptions.unknown_error


def find_first_character(first_character):
    try:
        if len(first_character) != 1:
            return api_exceptions.invalid_first_character
        found_products = my_database.find_first_character(first_character)
        return found_products
    except Exception as e:
        logger.exception(e)
        return api_exceptions.unknown_error


def invalid_md5_list(md5_list, is_insertion):
    # check if every md5 in this list is valid and there is/isn't a product in the database with the corresponding md5
    for md5 in md5_list:
        if not config.check_md5(md5):
            return api_exceptions.invalid_body_keys
        unique_md5 = my_database.find_md5(md5)
        if is_insertion and unique_md5["Message"] == "Found":
            # in the case of insertion, no product should have this md5
            return api_exceptions.not_unique_md5(md5)
        if not is_insertion and unique_md5["Message"] == "Not Found":
            # in the case of updating/deleting, there should be a product with the corresponding md5
            return api_exceptions.md5_dont_exist(md5)
    return False


def invalid_links_list(links_list):
    for link in links_list:
        found_link = my_database.find_download_link(link)
        if found_link["Message"] == "Not Found":
            return api_exceptions.invalid_link
    return False


def insert_multiple_products(products):
    try:
        # check if the entire body is a JSON Object
        if not isinstance(products, dict):
            return api_exceptions.invalid_body

        # check if md5s are valid
        md5_list_invalid = invalid_md5_list(products.keys(), is_insertion=True)
        if md5_list_invalid:
            return md5_list_invalid

        # check if all the values are json objects
        for inserted_product in products.values():
            if not isinstance(inserted_product, dict):
                return api_exceptions.invalid_body_values

        # insert into the database
        for inserted_product in products.items():
            single_insertion_verdict = my_database.insert_single_product(inserted_product[1], inserted_product[0])
            if single_insertion_verdict["Message"] != "ok":
                return single_insertion_verdict
        return config.ok_status

    except Exception as unknown_error:
        logger.exception(unknown_error)
        return api_exceptions.unknown_error


def update_multiple_products(products, is_md5=False, is_link=False):
    try:
        # check if the entire body is a JSON Object
        if not isinstance(products, dict):
            return api_exceptions.invalid_body

        if is_md5:
            # Check if all keys are valid md5s
            md5_list_invalid = invalid_md5_list(products.keys(), is_insertion=False)
            if md5_list_invalid:
                return md5_list_invalid

        if is_link:
            # Check if the keys are valid download links
            invalid_links = invalid_links_list(products.keys())
            if invalid_links:
                return invalid_links

        # check if all the values are json objects
        for updated_product in products.values():
            if not isinstance(updated_product, dict):
                return api_exceptions.invalid_body_values

        # update the database
        for updated_product in products.items():
            single_update_verdict = None
            if is_md5:
                single_update_verdict = my_database.update_single_product(
                    updated_product[1], product_md5=updated_product[0]
                )
            elif is_link:
                single_update_verdict = my_database.update_single_product(
                    updated_product[1], product_link=updated_product[0]
                )
            if single_update_verdict["Message"] != "ok":
                return single_update_verdict
        return config.ok_status

    except Exception as unknown_error:
        logger.exception(unknown_error)
        return api_exceptions.unknown_error


def delete_multiple_products(products):
    try:
        # check if the request body is a JSON array
        if not isinstance(products, list):
            return api_exceptions.body_not_list

        # check if md5s are valid
        md5_list_invalid = invalid_md5_list(products, is_insertion=False)
        if md5_list_invalid:
            return md5_list_invalid

        # delete products with md5 received from database
        for md5 in products:
            single_deleted_verdict = my_database.delete_single_product(md5)
            if single_deleted_verdict["Message"] != "ok":
                return single_deleted_verdict
        return config.ok_status

    except Exception as unknown_error:
        logger.exception(unknown_error)
        return api_exceptions.unknown_error


@app.route("/all", methods=["GET"])
def get_all_links():
    try:
        links_list = my_database.find_links()
        return links_list
    except Exception as e:
        logger.exception(e)
        return api_exceptions.unknown_error


@app.route("/get", methods=['GET'])
def get_information():
    try:
        if "md5" in request.args.keys():
            md5 = request.args["md5"]
            return find_md5(md5)
        elif "begin_with" in request.args.keys():
            first_character = request.args["begin_with"]
            return find_first_character(first_character)
        else:
            return api_exceptions.invalid_get_format
    except Exception as e:
        logger.exception(e)
        return api_exceptions.unknown_error


@app.route("/add", methods=['POST'])
def add_products():
    try:
        products_added = json.loads(request.data)
        return insert_multiple_products(products_added)
    except KeyError:
        return api_exceptions.invalid_dictionary_keys
    except Exception as e:
        logger.exception(e)
        return api_exceptions.unknown_error


@app.route("/update/md5", methods=['POST'])
def update_products_by_md5():
    try:
        products_updated = json.loads(request.data)
        return update_multiple_products(products_updated, is_md5=True)
    except KeyError:
        return api_exceptions.invalid_dictionary_keys
    except Exception as e:
        logger.exception(e)
        return api_exceptions.unknown_error


@app.route("/update/link", methods=['POST'])
def update_products_by_links():
    try:
        products_updated = json.loads(request.data)
        return update_multiple_products(products_updated, is_link=True)
    except KeyError:
        return api_exceptions.invalid_dictionary_keys
    except Exception as e:
        logger.exception(e)
        return api_exceptions.unknown_error


@app.route("/delete", methods=["POST"])
def delete_products():
    try:
        products_deleted = json.loads(request.data)
        return delete_multiple_products(products_deleted)
    except Exception as e:
        logger.exception(e)
        return api_exceptions.unknown_error


if __name__ == "__main__":
    try:
        app.run(debug=True)
        config.db.close()
    except Exception as err:
        logger.exception(err)

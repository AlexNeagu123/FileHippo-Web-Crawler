import config

invalid_md5 = {
    "Message": "Fail",
    "Status": "Valid md5 expected"
}

invalid_first_character = {
    "Message": "Fail",
    "Status": "Single ASCII Character Expected"
}

invalid_get_format = {
    "Message": "Fail",
    "Status": "only ?md5 and ?begin_with supported"
}

invalid_body_keys = {
    "Message": "Fail",
    "Status": "Keys of the inserted products are expected to be valid md5"
}

invalid_body_values = {
    "Message": "Fail",
    "Status": "Values of the inserted products are expected to be JSON Objects"
}

invalid_body = {
    "Message": "Fail",
    "Status": "The request body is expected to be a JSON Object"
}

invalid_dictionary_keys = {
    "Message": "Fail",
    "Status": "Invalid Status of Keys"
}

name_required = {
    "Message": "Fail",
    "Status": "Name is a mandatory field for an added product"
}

invalid_size_type = {
    "Message": "Fail",
    "Status": "Size field should be a number"
}

body_not_list = {
    "Message": "Fail",
    "Status": "The request body should be a JSON array"
}

unknown_error = {
    "Message": "Fail",
    "Status": "Unknown Error"
}

database_error = {
    "Message": "Fail",
    "Status": "Database Error!"
}

invalid_link = {
    "Message": "Fail",
    "Status": "Download Links should be present in the database"
}


def md5_dont_exist(md5):
    response_dict = {
        "Message": "Fail",
        "Status": "No product in the database has md5 = {}".format(md5)
    }
    return response_dict


def not_unique_md5(md5):
    response_dict = {
        "Message": "Fail",
        "Status": "{} is not a unique md5 in the database".format(md5)
    }
    return response_dict


def invalid_product_key(product_key):
    response_dict = {
        "Message": "Fail",
        "Status": "{} is not a valid product field! Expected {}".format(product_key, config.db_fields)
    }
    return response_dict


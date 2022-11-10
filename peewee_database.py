import peewee
import logging
import json
import hashlib
from config import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)
db = peewee.PostgresqlDatabase(
    'my_database',
    user='postgres',
    password='crawler_2022'
)


class Product(peewee.Model):
    Name = peewee.TextField()
    Version = peewee.TextField(null=True)
    DateAdded = peewee.TextField(null=True)
    Languages = peewee.TextField(null=True)
    DownloadLink = peewee.TextField(null=True)
    Size = peewee.IntegerField(null=True)
    Filename = peewee.TextField(null=True)
    sha256 = peewee.TextField(null=True)
    md5 = peewee.TextField()

    class Meta:
        database = db
        db_table = 'peewee_products'


def insert_product(product):
    logger.info("Product Added To The Database: {}".format(product["Name"]))
    product_added = Product(
        Name=product["Name"],
        Version=product["Version"],
        DateAdded=product["Date Added"],
        Languages=json.dumps(product["Languages"]),
        DownloadLink=product["Final Download Link"],
        Size=product["Size"],
        Filename=product["Filename"],
        md5=hashlib.md5(product["Name"].encode()).hexdigest()
    )
    product_added.save()


def find_product(product):
    try:
        Product.select().where((Product.Name == product['Name'])
                               & (Product.DownloadLink == product["Final Download Link"])).get()
    except peewee.DoesNotExist:
        return False
    return True


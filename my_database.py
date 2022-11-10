import psycopg2
import sqlite3
import os
import json
import logging
import abc

from config import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)
# conn - connection, c - cursor


class DBManager(abc.ABC):
    def __init__(self, db_type, db_name, db_user=None, db_password=None, db_path=None):
        self.db_type = db_type
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_path = db_path
        self.conn = None
        self.cursor = None

        try:
            if self.db_type == 'sqlite3':
                db_filename = os.path.join(db_path, db_name + '.db')
                self.conn = sqlite3.connect(db_filename)
                self.cursor = self.conn.cursor()
            elif self.db_type == 'postgres':
                self.conn = psycopg2.connect(
                    dbname=self.db_name,
                    user=self.db_user,
                    password=self.db_password
                )
                self.cursor = self.conn.cursor()
        except Exception as err:
            logger.exception("Database connection error: ", err)

    def __del__(self):
        try:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

        except Exception as err:
            logger.exception("Database connection error: ", err)

    @abc.abstractmethod
    def find_product(self, product):
        pass

    @abc.abstractmethod
    def insert_product(self, product):
        pass


class SqliteDB(DBManager):
    def find_product(self, product):
        try:
            format_dict = {
                "name": product["Name"],
                "download": product["Final Download Link"],
            }
            with self.conn:
                self.cursor.execute("""SELECT * FROM products WHERE Name = :name
                                                    AND (DownloadLink = :download OR ifnull("DownloadLink", '') = '')""",
                                    format_dict)
        except Exception as err:
            logger.exception(err)
            return False
        else:
            if self.cursor.fetchone():
                return True
            return False

    def insert_product(self, product):
        logger.info("Product Added To The SQLite Database: {}".format(product))
        try:
            format_dict = {
                "name": product["Name"],
                "version": product["Version"],
                "date": product["Date Added"],
                "languages": json.dumps(product["Languages"]),
                "download": product["Final Download Link"],
                "size": product["Size"],
                "filename": product["Filename"]
            }
            with self.conn:
                self.cursor.execute(
                    "INSERT INTO products VALUES (:name, :version, :date, :languages, :download, :size, :filename)",
                    format_dict
                )
        except Exception as err:
            logger.exception(err)


class PostgresDB(DBManager):
    def find_product(self, product):
        try:
            with self.conn:
                self.cursor.execute("""SELECT * FROM products WHERE Name = %s
                                    AND (DownloadLink = %s OR DownloadLink IS NULL)""",
                                    (product["Name"], product["Final Download Link"]))
        except Exception as err:
            logger.exception(err)
            return False
        else:
            if self.cursor.fetchone():
                return True
            return False

    def insert_product(self, product):
        logger.info("Product Added To The Postgres Database: {}".format(product["Name"]))
        try:
            with self.conn:
                self.cursor.execute("""INSERT INTO
                        products (id, Name, Version, DateAdded, Languages, DownloadLink, Size, Filename)
                        VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s)""", (
                    product["Name"], product["Version"], product["Date Added"], json.dumps(product["Languages"]),
                    product["Final Download Link"], product["Size"], product["Filename"]
                ))
        except Exception as err:
            logger.exception(err)

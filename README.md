# FileHippo-Web-Crawler
In the crawler file, I've implemented a web crawler that extracts data about the products available to download from FileHippo.
Specifically, for each product available, the crawler extracts: Name, Version, Date Added, Languages, Download Link, Size, Filename, Md5.
The information mentioned above is stored in a Postgres Database.

In the api file, I've implemented a generic API based on the contents of the database.
The following GET requests might be used:
    /all - Returns all the products from the database
    /get?md5="md5" - Returns the product that has the specified md5 
    /get?begin_with="c" - Returns the products that begin with the specified letter c

The following POST requests might be used (Product data is described in a json request file) :
    /add - Adds a products in the database. 
    /update/md5 - Update a product in the database that has the mentioned md5. 
    /update/link - Update a product in the database that has the mentioned download link.
    /delete - Delete a product from the database (Only md5 of the product should be specified in the json file).


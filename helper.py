import sqlite3

from flask import redirect, url_for


MAX_ITEMS_IN_CART = 10
MAX_COLLECTION_ID = 10
MAX_PRODUCT_ID = 20

collections = []
products = []
num_collections = []
num_products = []


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def db_init():
    db = sqlite3.connect('data.db')
    db.row_factory = dict_factory
    return db


def apology(message):
    return url_for('p404', message=message)


def get_product(db, product_id):
    item = db.execute("SELECT * FROM main.products WHERE id LIKE :code", {'code': product_id}).fetchone()
    images = []
    for i in range(item['images']):
        images.append("../static/images/" + str(item['id']) + "/" + str(i) + ".jpg")
    item['images'] = images
    return item


def get_short_cart(cart_items):
    return str(dict(zip(cart_items.keys(), list(item['quantity'] for item in cart_items.values()))))


def save_cart(db, user_id, cart_items):
    db.execute("UPDATE users SET cart = :items WHERE id = :id", {'items': get_total(cart_items), 'id': user_id})
    db.commit()


def get_total(cart):
    return sum(item['price'] * item['quantity'] for item in cart.values())


def cache():
    db = db_init()
    collections = db.execute("SELECT * FROM collections").fetchall()  # TODO: cache
    products = db.execute("SELECT * FROM products").fetchall()
    num_collections = MAX_COLLECTION_ID * [None]

    for collection in collections:
        num_collections[collection['id']] = collection

    num_products = MAX_PRODUCT_ID * [None]
    for product in products:
        num_products[product['id']] = product
    return collections, products, num_collections, num_products

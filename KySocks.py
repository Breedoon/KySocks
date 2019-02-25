from datetime import datetime
from helper import *
import os
from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from passlib.apps import custom_app_context as pwd_context
import sqlite3
import email_validator
import ast
from flask_jsglue import JSGlue

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)

JSGlue(app)


# TODO: unify data for layout: min-cart html, collections, product images, is empty cart,


@app.route('/')
def index():
    return render_template('index.html', collections=collections, is_index=True)


@app.route('/404')
def p404():
    if request.args.get("message") is None:
        return render_template('404.html', message="404 — Страница не найдена")
    else:
        return render_template('404.html', message=request.args.get("message"))


@app.route('/success')
def success():
    return render_template('success.html', id=request.args.get("id"))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/cart', methods=["GET", "POST"])
def cart():
    if request.method == "POST":
        first_name = request.form.get("first-name")
        last_name = request.form.get("last-name")
        city = request.form.get("city")
        delivery = request.form.get("delivery")
        phone = request.form.get("phone")
        email = request.form.get("email")
        password = request.form.get("password")
        additional = request.form.get("additional")  # TODO additional information
        changes = ast.literal_eval(request.form.get("changes"))

        for id in changes:
            session['cart'][id]['quantity'] += changes[id]
        session['total_cart'] = get_total(session['cart'])
        try:
            v = email_validator.validate_email(email, check_deliverability=False)
            email = v["email"]
        except email_validator.EmailNotValidError as e:
            return apology("Некорректный email: " + str(e))
        if len(first_name) < 1 or len(last_name) < 1 or len(city) < 1 or len(delivery) < 1:
            return apology("Некорректные данные")
        if len(phone) < 8:
            return apology('Некорректный номер телефона')
        db = db_init()
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": email}).fetchall()
        if len(user) == 1:  # TODO: debug save user + make based on id instead of username
            db.execute("UPDATE users SET firstname = :firstname, lastname = :lastname, "
                       "phone = :phone, delivery = :delivery WHERE username = :username",
                       {"firstname": first_name, "lastname": last_name, "phone": phone, "delivery": delivery,
                        "username": email})
        else:
            if password is not None:  # TODO: check if db doesn't contain user already
                db.execute("INSERT INTO users (username, password, firstname, lastname, phone, delivery) "
                           "VALUES(:username, :hash, :firstname, :lastname, :phone, :delivery)",
                           {"username": email, "hash": pwd_context.hash(password),
                            "firstname": first_name, "lastname": last_name, "phone": phone, "delivery": delivery})
        date = str(datetime.now())
        db.execute("INSERT INTO orders "
                   "(email, phone, city, delivery, cart, total_sum, date, additional_information) "
                   "VALUES (:email, :phone, :city, :delivery, :cart, :total, :date, :additional)",
                   {'email': email, 'phone': phone, 'city': city, 'delivery': delivery,
                    'cart': get_short_cart(session['cart']), 'total': session['total_cart'],
                    'date': date, 'additional': additional})
        order = db.execute("SELECT id FROM orders WHERE date IS :date", {'date': date}).fetchone()
        db.commit()
        session['cart'].clear()
        save_cart(db, session['user_id'], session['cart'])
        return url_for('success', id=order['id'])
    else:
        if is_cart_empty():
            col_md = 9
        else:
            col_md = 15
        if session.__contains__('user_id'):
            db = db_init()
            user = get_user_for_checkout(db)
            return render_template('checkout.html', email=user['username'], firstname=user['firstname'], col_md=col_md,
                                   lastname=user['lastname'], city=user['city'], delivery=user['delivery'])
        return render_template('checkout.html', col_md=col_md)


@app.route('/buy', methods=["POST"])
def buy():
    product_id = request.form.get("product_id")
    add = int(request.form.get("add"))
    if add is 0:
        if session.__contains__('cart') and product_id in session['cart']:
            cart = dict(session['cart'])
            cart.pop(product_id, None)
            session['cart'] = cart
        return jsonify({'success': True})
    product_data = num_products[int(product_id)]
    product_data['quantity'] = add
    if session.__contains__('cart'):
        cart = dict(session['cart'])
        if cart.__len__() >= MAX_ITEMS_IN_CART and add > 0:
            return apology('Слишком много вещей в корзине')  # TODO: notify instead of apology
        if cart.__contains__(product_id):
            result = cart[product_id]['quantity'] + add
            if result > MAX_ITEMS_IN_CART or result < 0:
                return apology('Неправильное количество')
            if result is not 0:
                cart[product_id]['quantity'] = result
            else:
                del cart[product_id]
        else:
            if add > 0:
                cart[product_id] = product_data
            else:
                return apology('Нечего удалять')
    elif add > 0:
        cart = {product_id: product_data}
    else:
        return apology('Invalid quality')
    session['total_cart'] = get_total(cart)
    session['cart'] = cart
    if session.__contains__('user_id'):
        db = db_init()
        save_cart(db, session['user_id'], session['cart'])
    return jsonify({'success': True, 'new_mini_cart': render_template('mini_cart.html'),
                    'notify': "Item added successfully"})


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":  # TODO fix redirect
        session.clear()
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        try:
            v = email_validator.validate_email(username, check_deliverability=False)
            username = v["email"]
        except email_validator.EmailNotValidError as e:
            return apology("Некорректная почта: " + str(e))
        if len(username) < 6:
            return apology("Некорректный пароль")
        elif not password == confirmation:
            return apology("Пароли не совпадают")
        db = db_init()
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
        if len(rows.fetchall()) == 1:
            return apology("Пользователь уже зарегистрирован")

        db.execute("INSERT INTO users (username, password) VALUES(:username, :hash)",
                   {"username": username, "hash": password})
        db.commit()
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        session["user_id"] = rows['id']
        return url_for("index")
    else:
        return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.clear()
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            v = email_validator.validate_email(username, check_deliverability=False)
            username = v["email"]
        except email_validator.EmailNotValidError as e:
            return apology(str(e))
        if not username:
            return apology("Must provide valid email")
        elif len(password) < 6:
            return apology("Must provide valid password")

        db = db_init()
        stored_user = db.execute("SELECT * FROM users WHERE username = :username", {'username': username}).fetchone()

        if stored_user is None:
            return apology("Account doesn't exist")

        if password != stored_user['password']:
            return apology("invalid username and/or password")

        session["user_id"] = stored_user['id']
        if stored_user['cart'] is not None:
            ids = ast.literal_eval(stored_user['cart'])
            cart = {}
            total = 0
            for key in ids:
                cart[key] = get_product(db, key)
                cart[key]['quantity'] = ids[key]
                total += cart[key]['price'] * ids[key]
            session['cart'] = cart
            session['total_cart'] = total
        return url_for('index')

    else:
        return render_template('login.html', col_md=7)


@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')


@app.route('/sales')
def sales():
    db = db_init()
    prods = products
    curr_coll = "All"
    if request.args.__contains__('collection_id'):
        prods = db.execute("SELECT * FROM products WHERE collection_id = :collection_id",
                           {'collection_id': request.args.get('collection_id')}).fetchall()
        curr_coll = num_collections[int(request.args.get('collection_id'))]['name']
    return render_template('sales.html', products=prods, collections=collections, current_collection=curr_coll)


@app.route('/single')
def single():
    if not request.args.__contains__('id'):
        return redirect('/')
    db = db_init()
    data = get_product(db, request.args.get('id'))
    related = db.execute("SELECT * FROM products WHERE collection_id = :collection AND id != :id",
                         {'collection': data['collection_id'], 'id': request.args.get('id')})
    return render_template('single.html', data=data, related=related, collections=collections)


if __name__ == '__main__':
    collections, products, num_collections, num_products = cache()
    app.run()

from datetime import datetime
from helper import *
import os
from flask import Flask, redirect, render_template, request, session, url_for
from passlib.apps import custom_app_context as pwd_context
import sqlite3
import email_validator
import ast
from flask_jsglue import JSGlue

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)

JSGlue(app)


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
        product_id = request.form.get("product_id")
        add = int(request.form.get("add"))
        if add is 0:
            return 'Nice.'
        db = db_init()
        product_data = db.execute("SELECT * FROM products WHERE id LIKE :code", {'code': product_id}).fetchone()
        product_data['quantity'] = add
        if session.__contains__('cart'):
            cart = session['cart']
            if cart.__len__() >= MAX_ITEMS_IN_CART and add > 0:
                return apology('Слишком много вещей в корзине')
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
        session['cart'] = session['cart']  # DO NOT REMOVE

        if session.__contains__('user_id'):
            save_cart(db, session['user_id'], session['cart'])
        return "Nice!"

    else:
        return render_template('checkout.html')


@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        city = request.form.get("city")
        delivery = request.form.get("delivery")
        phone = request.form.get("phone")
        email = request.form.get("email")
        password = request.form.get("password")
        additional = request.form.get("additional")  # TODO additional information

        try:
            v = email_validator.validate_email(email, check_deliverability=False)
            email = v["email"]
        except email_validator.EmailNotValidError as e:
            return apology("Некорректный email: " + str(e))
        if len(firstname) < 1 or len(lastname) < 1 or len(city) < 1 or len(delivery) < 1:
            return apology("Некорректные данные")
        if len(phone) < 8:
            return apology('Некорректный номер телефона')
        db = db_init()
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": email}).fetchall()
        if len(user) == 1:
            if not user.__contains__(firstname):
                db.execute("UPDATE users SET firstname = :firstname, lastname = :lastname, "
                           "phone = :phone, delivery = :delivery WHERE username = :username",
                           {"firstname": firstname, "lastname": lastname, "phone": phone, "delivery": delivery,
                            "username": email})
        else:
            if password is not None:
                db.execute("INSERT INTO users (username, password, firstname, lastname, phone, delivery) "
                           "VALUES(:username, :hash, :firstname, :lastname, :phone, :delivery)",
                           {"username": email, "hash": pwd_context.hash(password),
                            "firstname": firstname, "lastname": lastname, "phone": phone, "delivery": delivery})
        date = str(datetime.now())
        db.execute("INSERT INTO orders (email, phone, city, delivery, cart, total_sum, date) VALUES "
                          "(:email, :phone, :city, :delivery, :cart, :total, :date)",
                          {'email': email, 'phone': phone, 'city': city, 'delivery': delivery,
                           'cart': get_short_cart(session['cart']), 'total': session['total_cart'], 'date': date})
        order = db.execute("SELECT id FROM orders WHERE date IS :date", {'date': date}).fetchone()
        db.commit()

        return url_for('success', id=order['id'])

    else:
        if session.__contains__('user_id'):
            db = db_init()
            user = db.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": session['user_id']}).fetchone()
            if user['firstname'] is not None:
                return render_template('checkout.html', email=user['username'], firstname=user['firstname'],
                                       signedin=True,
                                       lastname=user['lastname'], city=user['city'], delivery=user['delivery'])
            else:
                return render_template('checkout.html', email=user['username'], signedin=True)
        return render_template('checkout.html')


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
        return render_template('login.html')


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
    return render_template('single.html', data=data, related=related)


if __name__ == '__main__':
    collections, products, num_collections, num_products = cache()
    app.run()

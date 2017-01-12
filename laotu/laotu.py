# -*- coding: utf-8 -*-
"""
    laotu

"""

import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash
import stripe
import os
from flask_sqlite_admin.core import sqliteAdminBlueprint

from flask.ext.uploads import (UploadSet, configure_uploads, IMAGES,
                              UploadNotAllowed)
from werkzeug import secure_filename
import re
from strings import *


# configuration
#DATABASE = 'C:\\Users\\Milan\\Documents\\Harvard\\fall 2016\\d4d\\LaotuRepo\\laotu\\tmp\\laotu.db'
DATABASE = '/tmp/laotu.db'
#DATABASE = 'C:\\Users\\samzliu\\Desktop\\LaoTu\\LaoTu\\laotu\\tmp\\laotu.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'
UPLOADED_PHOTOS_DEST = 'C:\\Users\\samzliu\\Desktop\\LaoTu\\LaoTu\\laotu\\tmp\\photos'

# test keys right now
stripe_keys = {
  'secret_key': os.environ['SECRET_KEY'],
  'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']


# create our little aWpplication :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('laotu_SETTINGS', silent=True)
sqliteAdminBP = sqliteAdminBlueprint(dbPath = DATABASE)
app.register_blueprint(sqliteAdminBP, url_prefix='/sqlite')

upload_photos = UploadSet('photos', IMAGES)
configure_uploads(app, upload_photos)



if __name__ == '__main__':
    app.run()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def get_user_id(email):
    """Convenience method to look up the id for a email."""
    rv = query_db('select user_id from user where email = ?',
                  [email], one=True)
    return rv[0] if rv else None


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = ?',
                          [session['user_id']], one=True)


#validation functions
def isphone(num):
    if re.match("(\d{3}[-\.\s]??\d{4}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{4}[-\.\s]??\d{4}"
                "|\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\d{4}[-\.\s]??\d{3}[-\.\s]??\d{4})",
                num) == None:
        return False
    else:
        return True


@app.route('/')
def home():
    """Home page"""
    return render_template('home.html')

    

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('home'))
    error = None
    errtype = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            email = ?''', [request.form['email']], one=True)
        if user is None:
            error = ERR_INVALID_EMAIL
            errtype = "email"
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = ERR_INVALID_PWD
            errtype = "password"
        else:
            flash(FLASH_LOGGED)
            session['user_id'] = user['user_id']
            return redirect(url_for('home'))
    return render_template('login.html', error=error, errtype=errtype)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('home'))
    error = None
    errtype = None
    if request.method == 'POST':
        if not request.form['name']:
            error = ERR_NO_NAME
            errtype = 'thename'
        elif not request.form['email']:
            error = ERR_NO_EMAIL
            errtype = 'email'
        elif '@' not in request.form['email'] or '.' not in request.form['email']:
            error = ERR_INVALID_EMAIL
            errtype = 'email'
        elif not request.form['password']:
            error = ERR_NO_PWD
            errtype = 'password1'
        elif not request.form['password2']:
            error = ERR_NO_PWD
            errtype = 'password2'
        elif not request.form['address']:
            error = ERR_NO_ADDRESS
            errtype = 'address'
        elif not request.form['phone']:
            error = ERR_NO_PHONE
            errtype = 'phone'
        elif not isphone(request.form['phone']):
            error = ERR_INVALID_PHONE
            errtype = 'phone'
        elif request.form['password'] != request.form['password2']:
            error = ERR_MISMATCH
            errtype = 'password'
        elif get_user_id(request.form['email']) is not None:
            error = ERR_EMAIL_TAKEN
            errtype = 'email'
        else:
            db = get_db()
            db.execute('''insert into user (
              email, pw_hash, name, address, phone) values (?, ?, ?, ?, ?)''',
              [request.form['email'],
               generate_password_hash(request.form['password']),request.form['name'], request.form['address'], request.form['phone']])
            db.commit()
            flash(FLASH_REGISTERED)
            return redirect(url_for('login'))
    return render_template('register.html', error=error, errtype=errtype)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash(FLASH_UNLOGGED)
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        photo = request.files.get('photo')
        title = request.form.get('title')
        if not (photo and title):
            flash("You must fill in all the fields")
        else:
            try:
                filename = upload_photos.save(photo)
            except UploadNotAllowed:
                flash("The upload was not allowed")
            else:
                #store filename database
                flash("Upload successful")
                return redirect(url_for('home'))
    return render_template('upload.html')   

    
@app.route('/products_list')
def show_products_list():
    return render_template('products_list.html', products_list=query_db('''
    select * from product'''))

@app.route('/products_list/<category>')
def show_products_list_category(category):
    return render_template('products_list.html', products=query_db('''
        select * from product where category = ?''', (category, )))

@app.route('/<int:product_id>')
def show_product(product_id):
    product = query_db('select * from product where product_id = ?', [product_id], one=True)
    producer = query_db('select * from producer where producer_id = ?', str(product['producer_id']), one=True)
    return render_template('product.html', product=product, producer=producer)

@app.route('/<int:product_id>/<int:quantity>/add_product')
def add_product(product_id, quantity=1):
    """Adds a product to the cart."""
    if not g.user:
        flash(FLASH_SIGNIN_NEEDED)
        return redirect(url_for('register'))
    if product_id is None:
        abort(404)
    db = get_db()
    db.execute('''insert into cart (user_id, product_id, quantity) values (?, ?, ?)''', (session['user_id'], product_id, quantity))
    db.commit()
    flash(FLASH_CARTED)
    return redirect(url_for('show_products_list'))

@app.route('/cart')
def get_cart():
    """Displays cart"""
    if not g.user:
        flash(FLASH_SIGNIN_NEEDED)
        return redirect(url_for('register'))
    items=query_db('''select cart.product_id, cart.quantity, product.title, product.price from cart \
    join product on cart.product_id=product.product_id where cart.user_id = ?''',[session['user_id']])
    total = 0
    for item in items:
        total += float(item['quantity']) * float(item['price'])/float(100)
    return render_template('cart.html', items=items, total=total)

@app.route('/<int:product_id>/remove_product')
def remove_product(product_id):
    """Removes a product to the cart."""
    if 'user_id' not in session:
        flash(FLASH_SIGNIN_NEEDED)
        return render_template('login.html')
    if product_id is None:
        abort(404)
    db = get_db()
    db.execute('''delete from cart where user_id = ? and product_id = ?''', (session['user_id'],product_id))
    db.commit()
    flash('The product has been removed from cart.')
    return redirect(url_for('get_cart'))

@app.route('/clear_cart')
def clear_cart():
    """Clears everything from cart"""
    if 'user_id' not in session:
        flash(FLASH_SIGNIN_NEEDED)
        return render_template('login.html')
    db = get_db()
    db.execute('''delete from cart where user_id = ?''', [session['user_id']])
    db.commit()
    flash('The cart has been cleared')
    return redirect(url_for('get_cart'))

@app.route('/<int:product_id>/<int:quantity>/update_product')
def update_product(product_id, quantity):
    """Updates a product from cart"""
    if 'user_id' not in session:
        flash(FLASH_SIGNIN_NEEDED)
        return render_template('login.html')
    db = get_db()
    db.execute('''update cart set quantity = ? where user_id = ? and product_id = ?''', (quantity,session['user_id'], product_id))
    db.commit()
    flash('The cart has been updated')
    return redirect(url_for('get_cart'))

@app.route('/pay')
def pay():
    # change amount here
    amount = query_db('select sum(price) from cart', one=True)[0]
    print amount
    return render_template('pay.html', key=stripe_keys['publishable_key'], amount=amount) # the amount in the cart

@app.route('/charge', methods=['POST'])
def charge():
    # ideally, want to just keep this variable from the pay function
    # also, the currency is in jiao (i.e. Chinese "cents"), so 350 is just 3.50 yuan
    amount = query_db('select sum(price) from cart', one=True)[0]*100

    try:
      charge = stripe.Charge.create(
          amount=amount, # Amount in cents
          currency="cny",
          source=request.form['stripeToken']
      )
    except stripe.error.CardError as e:
      # The Alipay account has been declined
      pass
      flash(FLASH_PURCHASE)
    return redirect(url_for('home'))

@app.route('/search', methods=['POST'])
def search():
    print("here")
    return redirect(url_for('search_results', query=request.form['search']))

@app.route('/search_results/<query>')
def search_results(query):
    products = query_db("""select * from product where title like ? or description like ?""",
        ('%' + query + '%', '%' + query + '%'))
    results = products # this will be more general later
    return render_template('search_results.html', results=results, query=query)

@app.route('/categories')
def categories():
    categories = query_db("""select distinct category from product""")
    return render_template('categories.html', categories=categories)

@app.route('/category/<category>')
def category(category):
    products = query_db("""select * from product where category like ?""", (category,))
    return render_template('products_list.html', products=products)

@app.route('/stories')
def stories():
    return render_template('stories.html')

# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url

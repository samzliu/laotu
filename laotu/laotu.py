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
import re
from flask.ext.uploads import UploadSet, IMAGES, configure_uploads
from datetime import datetime

from strings import *

# configuration
#DATABASE = 'C:\\Users\\Milan\\Documents\\Harvard\\fall 2016\\d4d\\LaotuRepo\\laotu\\tmp\\laotu.db'
DATABASE = '/tmp/laotu.db'
#DATABASE = 'C:\\Users\\samzliu\\Desktop\\LaoTu\\LaoTu\\laotu\\tmp\\laotu.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'
#UPLOADED_PHOTOS_DEST = 'C:\\Users\\samzliu\\Desktop\\LaoTu\\LaoTu\\laotu\\tmp\\photos'
UPLOADED_PHOTOS_DEST = '/tmp/photos'

# test keys right now
stripe_keys = {
  'secret_key': os.environ['SECRET_KEY'],
  'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('laotu_SETTINGS', silent=True)
sqliteAdminBP = sqliteAdminBlueprint(dbPath = DATABASE,
    tables = ['user', 'producer', 'product', 'trans', 'tag', 'product_to_tag'], title = 'Admin Page', h1 = 'Admin Page')
app.register_blueprint(sqliteAdminBP, url_prefix='/admin')

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

def hasStandard(product):
    return product['standard_geo'] or product['standard_producer'] or product['standard_raw'] or \
    product['standard_production'] or product['standard_storage'] or product['standard_tech'] or \
    product['standard_package'] or product['standard_price']

#pages are below .................................................................

@app.route('/')
def home():
    """Home page"""
    return render_template('home.html')



@app.route('/products')
def products():
    """Displays the products."""
    return render_template('products.html')


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

@app.route('/products_list')
def show_products_list():
    return render_template('products_list.html', products_list=query_db('''
    select * from product'''), producer=None)

@app.route('/products_list/<category>')
def show_products_list_category(category):
    return render_template('products_list.html', products_list=query_db('''
        select * from product where category = ?''', (category, )))

@app.route('/<int:product_id>')
def show_product(product_id):
    product = query_db('select * from product where product_id = ?', [product_id], one=True)
    producer = query_db('select * from producer where producer_id = ?', str(product['producer_id']), one=True)
    return render_template('product.html', product=product, producer=producer, hasStandard=hasStandard(product))

@app.route('/del/<int:product_id>')
def del_product(product_id):
    #insert admin authentication
    product = query_db('select * from product where product_id = ?', [product_id], one=True)
    #delete photos
    for i in range(14,21):
        os.remove(os.path.join(UPLOADED_PHOTOS_DEST, product[i]))
    db = get_db()
    db.execute('''delete from product where product_id = ?''', (product_id,))
    db.commit()
        
    
    
    
@app.route('/<int:product_id>/<int:quantity>/add_product')
def add_product(product_id, quantity):
    """Adds a product to the cart."""
    if not g.user:
        flash(FLASH_SIGNIN_NEEDED)
        return redirect(url_for('register'))
    if product_id is None:
        abort(404)
    elif query_db('select 1 from cart where product_id = ?', [product_id], one=True):
        flash(FLASH_CART_PRODUCT)
        return redirect(url_for('show_product', product_id=product_id))
    else:
        db = get_db()
        db.execute('''insert into cart (user_id, product_id, quantity) values (?, ?, ?)''', (session['user_id'], product_id, quantity))
        db.commit()
        flash(FLASH_CARTED)
        return redirect(url_for('show_products_list'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        photo = request.files.get('photo')
        title = request.form.get('title')
        if not (photo and title):
            flash(FLASH_UPLOAD_FIELDS)
        else:
            try:
                filename = upload_photos.save(photo)
            except UploadNotAllowed:
                flash(FLASH_UPLOAD_FORBIDDEN)
            else:
                #store filename database
                flash(FLASH_UPLOAD_SUCCESSFUL)
                return redirect(url_for('home'))
    return render_template('upload.html')

@app.route('/cart')
def get_cart():
    """Displays cart"""
    if not g.user:
        flash(FLASH_SIGNIN_NEEDED)
        return redirect(url_for('register'))
    items=query_db('''select cart.product_id, cart.quantity, product.title, product.price, product.quantity as inventory from cart \
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
    flash(FLASH_UNCARTED)
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
    flash(FLASH_CLEARED)
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
    flash(FLASH_UPDATED)
    return redirect(url_for('get_cart'))

@app.route('/pay')
def pay():
    # check that all items are still in stock
    purchases = query_db('''select cart.product_id, cart.quantity, product.title, product.price, product.quantity as inventory from cart \
    join product on cart.product_id=product.product_id where cart.user_id=?''', [session['user_id']])
    for purchase in purchases:
        if purchase['inventory'] < purchase['quantity']:
            out_of_stock_message = FLASH_OUT_OF_STOCK % (purchase['title'], purchase['title'])
            flash(out_of_stock_message)
            return redirect(url_for('get_cart'))
    amount = query_db('select sum(product.price*cart.quantity) from cart join product on cart.product_id=product.product_id', one=True)[0]
    if amount < 500:
        flash(FLASH_AMOUNT_TOO_SMALL)
        return redirect(url_for('get_cart'))
    return render_template('pay.html', key=stripe_keys['publishable_key'], amount=amount) # the amount in the cart

@app.route('/charge', methods=['POST'])
def charge():
    # ideally, want to just keep this variable from the pay function
    amount = query_db('select sum(product.price*cart.quantity) from cart join product on cart.product_id=product.product_id', one=True)[0]

    try:
      charge = stripe.Charge.create(
          amount=amount, # Amount in cents
          currency="cny",
          source=request.form['stripeToken']
      )
    except stripe.error.CardError as e:
      # The Alipay account has been declined
      pass

    # update all the databases
    purchases = query_db('''select cart.product_id, cart.quantity, product.title, product.price, product.quantity as inventory from cart \
    join product on cart.product_id=product.product_id where cart.user_id=?''', [session['user_id']])
    db = get_db()
    # check that all products are in stock
    for purchase in purchases:
        # add transactions to history, one row for each product
        db.execute('''insert into trans (product_id, user_id, quantity, trans_date, amount) \
        values (?,?,?,?,?)''', (purchase['product_id'], session['user_id'], purchase['quantity'],
        datetime.utcnow(), purchase['price']*purchase['quantity']))
        # update product inventory
        db.execute('''update product set quantity = quantity - ? where product_id = ?''', (purchase['quantity'], purchase['product_id']))
    # clear the cart
    db.execute('''delete from cart where user_id = ?''', [session['user_id']])
    db.commit()
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
    tags = query_db("""select * from tag where importance = 1""")
    return render_template('categories.html', tags=tags)

@app.route('/category/<category>')
def category(category):
    tag_id = query_db("""select tag_id from tag where name=?""", (category,), one=True)[0]
    products_list = query_db("""select * from product
        inner join product_to_tag
        on product.product_id=product_to_tag.product_id
        and product_to_tag.tag_id=?""", (tag_id,))
    # one importance level away
    tags_list = query_db("""select distinct tag.tag_id, tag.name, tag.importance from 
        tag
        inner join product
        inner join product_to_tag
        on product.product_id=product_to_tag.product_id
        and product_to_tag.tag_id=?
        where tag.importance=?+1""", (tag_id, tag_id))
    if len(tags_list) > 0:
        return render_template('products_list.html', products_list=products_list, tags_list=tags_list)

    # multiple importance levels away
    tags_list = query_db("""select distinct tag.tag_id, tag.name, tag.importance from 
        tag
        inner join product
        inner join product_to_tag
        on product.product_id=product_to_tag.product_id
        and product_to_tag.tag_id=?
        where tag.importance>?""", (tag_id, tag_id))
    return render_template('products_list.html', products_list=products_list, tags_list=tags_list)


@app.route('/stories')
def stories():
    return render_template('stories.html')

@app.route('/<int:producer_id>/show_farmer')
def show_farmer(producer_id):
    producer_products = query_db('select * from product where producer_id= ?', [producer_id])
    producer = query_db('select * from producer where producer_id=?', [producer_id], one=True)
    return render_template('products_list.html', products_list=producer_products, producer=producer)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product_db():
    """Add a product to the database."""
    print "Hello there!"
    error = None
    errtype = None
    # check if a string is an integer
    def is_int(s):
        try:
            int(s)
            return True 
        except ValueError:
            return False
            
    if request.method == 'POST':
        print "Made it here."
        print request.form
        if not request.form['title']:
            error = ERR_NO_PROD_TITLE
            errtype = 'title'
        elif not request.form['quantity']:
            error = ERR_NO_PROD_QUANTITY
            errtype = 'quantity'
        elif not is_int(request.form['quantity']):
            error = ERR_INVALID_PROD_QUANTITY
            errtype = 'quantity'
        elif not request.form['price']:
            error = ERR_NO_PROD_PRICE
            errtype = 'price'
        elif not is_int(request.form['price']):
            error = ERR_INVALID_PROD_PRICE
            errtype = 'price'
        elif not request.form['description']:
            error = ERR_NO_PROD_DESCRIPTION
            errtype = 'description'
        elif not request.form['producerid']:
            error = ERR_NO_PROD_PRODUCER_ID
            errtype = 'producerid'
        elif len(query_db('''select * from producer where producer_id=?''', \
            (request.form['producerid'],))) == 0:
            error = ERR_INVALID_PROD_PRODUCER_ID
            errtype = 'producerid'
        elif not request.form['standard_geo']:
            error = ERR_NO_STANDARD_GEO
            errtype = 'standard_geo'
        elif not request.form['standard_producer']:
            error = ERR_NO_STANDARD_PRODUCER
            errtype = 'standard_producer'
        elif not request.form['standard_raw']:
            error = ERR_NO_STANDARD_RAW
            errtype = 'standard_raw'
        elif not request.form['standard_production']:
            error = ERR_NO_STANDARD_PRODUCTION
            errtype = 'standard_production'
        elif not request.form['standard_storage']:
            error = ERR_NO_STANDARD_STORAGE
            errtype = 'standard_storage'
        elif not request.form['standard_tech']:
            error = ERR_NO_STANDARD_TECH
            errtype = 'standard_tech'
        elif not request.form['standard_package']:
            error = ERR_NO_STANDARD_PACKAGE
            errtype = 'standard_price'
        elif not request.form['standard_price']:
            error = ERR_NO_STANDARD_PRICE
            errtype = 'standard_price'
        else:
            db = get_db()
            db.execute('''insert into product (
              title, quantity, price, description, producer_id, standard_geo, 
              standard_producer, standard_raw, standard_production, standard_storage, 
              standard_tech, standard_package, standard_price) 
              values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              [request.form['title'], int(request.form['quantity']), \
                  int(request.form['price']), request.form['description'], \
                  int(request.form['producerid']), request.form['standard_geo'],\
                  request.form['standard_producer'], request.form['standard_raw'],\
                  request.form['standard_production'], request.form['standard_storage'],\
                  request.form['standard_tech'], request.form['standard_package'],\
                  request.form['standard_price']])
            db.commit()
            flash(FLASH_PROD_ADD_SUCCESSFUL)
            error = None
            errtype = errtype
    return render_template('add_product.html', error=error, errtype=errtype)


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url

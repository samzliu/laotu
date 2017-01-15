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
from flask.ext.uploads import UploadSet, IMAGES, configure_uploads, UploadNotAllowed
from datetime import datetime
from threading import Timer

from strings import *

from functools import wraps

from flask_mail import Mail, Message

from threading import Thread


# configuration
#DATABASE = 'C:\\Users\\Milan\\Documents\\Harvard\\fall 2016\\d4d\\LaotuRepo\\laotu\\tmp\\laotu.db'
DATABASE = '/tmp/laotu.db'
#DATABASE = 'C:\\Users\\samzliu\\Desktop\\LaoTu\\LaoTu\\laotu\\tmp\\laotu.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

#UPLOADED_PHOTOS_DEST = 'C:\\Users\\Milan\\Documents\\Harvard\\fall 2016\\LaotuRepo\\laotu\\tmp\\photos'
UPLOADED_PHOTOS_DEST = '/tmp/photos'
UPLOADED_PHOTOS_DEST = '/tmp/photos'
DEFAULT_IMPORTANCE = 100

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('laotu_SETTINGS', silent=True)

# mail config
# gmail config:
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'natsapptester@gmail.com'
app.config['MAIL_PASSWORD'] = 'securepassword123'
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# available config options:
# MAIL_SERVER : default ‘localhost’
# MAIL_PORT : default 25
# MAIL_USE_TLS : default False
# MAIL_USE_SSL : default False
# MAIL_DEBUG : default app.debug
# MAIL_USERNAME : default None
# MAIL_PASSWORD : default None
# MAIL_DEFAULT_SENDER : default None
# MAIL_MAX_EMAILS : default None
# MAIL_SUPPRESS_SEND : default app.testing
# MAIL_ASCII_ATTACHMENTS : default False


# keys to connect to the Stripe API, specify via command line
# test keys:
# PUBLISHABLE_KEY=pk_test_haUn12yj5cA394KQd0K37hzh
# SECRET_KEY=sk_test_52QkxEpzwiy1p4bNKTX18Vy7
# to view dashboard: https://dashboard.stripe.com/test/dashboard
stripe_keys = {
  'secret_key': os.environ['SECRET_KEY'],
  'publishable_key': os.environ['PUBLISHABLE_KEY']
}
stripe.api_key = stripe_keys['secret_key']


# create our BIGGGGG application >:^)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('laotu_SETTINGS', silent=True)


upload_photos = UploadSet('photos', IMAGES)
configure_uploads(app, upload_photos)
timer_on = False


if __name__ == '__main__':
    app.run()

# admin authentication ........................................................

def admin_required(f):
    """
    Decorate routes to require admin login. Add @admin_required below @app.route
    for any endpoint that should require admin authentication

    decorators: http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user or 'admin' not in session or not session['admin']:
            return redirect(url_for("adminauth", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

sqliteAdminBP = sqliteAdminBlueprint(dbPath = DATABASE,
     tables = ['user', 'admin', 'producer', 'product', 'trans', 'tag', 'product_to_tag'],
     title = 'Admin Page', h1 = 'Admin Page',
     decorator = admin_required)
app.register_blueprint(sqliteAdminBP, url_prefix='/admin')

# other decorators ............................................................
def async(f):
    """
    runs f asynchronously
    https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xi-email-support

    make f asynchronous by adding @async above definition

    """
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

# mailing functions ...........................................................

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to, subject, message, html, sender="natsapptester@gmail.com"):
    """
    to: a list of strings
    subject: a string
    message: a string
    sender: an address string or a touple (name, address)

    """
    msg = Message(subject, sender=sender, recipients=to)
    msg.body = message
    msg.html = html
    send_async_email(app, msg)

# IM NOT SURE IF THIS IS LIKE... ASYNC BUT I HOPE IT IS
def send_bulk_mail(to, message, sender=("Laotu Noreply", "noreply@laotu.com")):
    """
    Opens connection to email host that is automatically closed once all emails
    are sent.

    https://pythonhosted.org/Flask-Mail/

    to: a list of user objects with 'name' and 'email' attributes
    message: a string
    sender: an address string or a touple (name, address)

    """

    with mail.connect() as conn:
        for user in users:
            subject = "hello, %s" % user['name']
            msg = Message(recipients=[user['email']],
                      body=message,
                      subject=subject,
                      sender=sender)
            conn.send(msg)

# missing implementations: send mail with attachment.

# helper functions ............................................................
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
    """Creates default admin account
       user
       pass: securepassword123"""
    db = get_db()
    db.execute('''insert into user (
        email, pw_hash, name, address, phone) values (
        'admin@default.com', 'pbkdf2:sha1:1000$zEFlrwdw$a613c128baebdd9d626da88b053e9bc7e3c68a96', 'admin default', '-', '0000000000')''')
    db.execute('''insert into admin (user_id) values (1)''')
    db.commit()
    print('Created default admin account.\n user: admin@default.com \n pass: securepassword123')

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

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = ?',
                          [session['user_id']], one=True)

### Validation functions ###
def isphone(num):
    if re.match("(\d{3}[-\.\s]??\d{4}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{4}[-\.\s]??\d{4}"
                "|\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\d{4}[-\.\s]??\d{3}[-\.\s]??\d{4})",
                num) == None:
        return False
    else:
        return True

def hasStandard(product):
    return product['standard_geo'] or product['standard_producer'] or \
            product['standard_raw'] or product['standard_production'] or \
            product['standard_storage'] or product['standard_tech'] or \
            product['standard_package'] or product['standard_price']



### Basic pages ###
@app.route('/')
def home():
    """Home page"""
    return render_template('home.html')

@app.route('/about')
def about():
    """Shows the About page."""
    return render_template('about.html')



### User account pages ###
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
            session['admin'] = False
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
                generate_password_hash(request.form['password']),
                request.form['name'],
                request.form['address'],
                request.form['phone']])
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



### Product, tag, and miscellaneous pages ###

def render_listing(products_list=None, tags_list=None, specific_tag=None, message=None, 
        tag_limit=True):
    overflow = (tags_list and len(tags_list) > 3 and tag_limit)
    if overflow:
        tags_list = tags_list[0:3]
    return render_template('listing.html', \
        products_list=products_list,\
        tags_list=tags_list,\
        overflow=overflow,\
        specific_tag=specific_tag,\
        message=message)


# show a listing of all products
@app.route('/products_list')
def show_products_list():
    """Displays the list of products."""
    products_list=query_db('''select * from product''')
    message="All products!"
    return render_listing(products_list=products_list, message=message)


# show a listing of products under tag, and related categories
@app.route('/products_list/<tag>')
def show_products_list_tag(tag):
    tag = query_db("""select * from tag where name=?""", (tag,), one=True)
    tag_id = tag['tag_id']
    products_list = query_db("""select * from product
        inner join product_to_tag
        on product.product_id=product_to_tag.product_id
        and product_to_tag.tag_id=?""", (tag_id,))
    tags_list = query_db("""select distinct tag.tag_id, tag.name, tag.importance from
        tag
        inner join product
        inner join product_to_tag
        on product.product_id=product_to_tag.product_id
        and product_to_tag.tag_id=?
        where tag.importance>?
        order by importance""", (tag_id, tag_id))
    message="Products and tags related to \"" + tag['name'] + "\":"

    return render_listing(products_list=products_list, tags_list=tags_list,\
        specific_tag=tag, message=message)

# show a list of all tags
@app.route('/tags')
def show_tags_list():
    tags = query_db("""select * from tag order by importance asc""")
    message="All tags!"
    return render_listing(tags_list=tags, message=message, tag_limit=False)

# show a list of tags related to a specific tag
@app.route('/tags/<tag>')
def show_tags_list_tag(tag):
    tag = query_db("""select * from tag where name=?""", (tag,), one=True)
    tag_id = tag['tag_id']
    tags_list = query_db("""select distinct tag.tag_id, tag.name, tag.importance from
        tag
        inner join product
        inner join product_to_tag
        on product.product_id=product_to_tag.product_id
        and product_to_tag.tag_id=?
        where tag.importance>?
        order by importance""", (tag_id, tag_id))
    message="Categories related to \"" + tag['name'] + "\"."
    return render_listing(tags_list=tags_list, message=message, tag_limit=False)

# search reroute
@app.route('/search', methods=['POST'])
def search():
    print("here")
    return redirect(url_for('search_results', query=request.form['search']))

# search results page
@app.route('/search_results/<query>')
def search_results(query):
    products = query_db("""select distinct product.* from
        product
        inner join tag
        inner join product_to_tag
        on ((product.product_id=product_to_tag.product_id
        and product_to_tag.tag_id=tag.tag_id
        and tag.name like ?)
        or product.title like ?
        or product.description like ?)""",
        ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
    tags = query_db("""select distinct tag.* from tag 
        inner join product
        inner join product_to_tag
        on ((product.product_id=product_to_tag.product_id
        and product_to_tag.tag_id=tag.tag_id
        and (product.title like ?
        or product.description like ?))
        or tag.name like ?)""",
        ('%' + query + '%','%' + query + '%','%' + query + '%'))
    message="Search results for \"" + query + "\":"
    return render_listing(products_list=products, tags_list=tags, message=message)



### Individual product page ###
@app.route('/<int:product_id>')
def show_product(product_id):
    """Displays a single product in detail."""
    product = query_db('select * from product where product_id = ?',
                        [product_id], one=True)
    producer = query_db('select * from producer where producer_id = ?',
                        str(product['producer_id']), one=True)
    photos = [product['product_photo_filename_1'],
                        product['product_photo_filename_2'],
                        product['product_photo_filename_3']]
    stories = [product['laotu_book_photo_filename_1'],
                        product['laotu_book_photo_filename_2'],
                        product['laotu_book_photo_filename_3'],
                        product['laotu_book_photo_filename_4']]
    return render_template('product.html', product=product, producer=producer,
        hasStandard=hasStandard(product), photos=photos, stories=stories)



### Cart pages ###
@app.route('/cart')
def get_cart():
    """Displays cart."""
    # user musts be logged in to access cart functionality
    if 'user_id' not in session:
        flash(FLASH_SIGNIN_NEEDED)
        return redirect(url_for('register'))
    items = query_db('''select cart.product_id, cart.quantity, product.title, \
                        product.price, product.quantity as inventory from cart \
                        join product on cart.product_id=product.product_id \
                        where cart.user_id = ?''',[session['user_id']])
    total = 0
    for item in items:
        total += float(item['quantity']) * float(item['price'])/float(100)
    return render_template('cart.html', items=items, total=total)

@app.route('/<int:product_id>/<int:quantity>/add_product')
def add_product(product_id, quantity):
    """Adds a product to the cart."""
    # user musts be logged in to access cart functionality
    if 'user_id' not in session:
        flash(FLASH_SIGNIN_NEEDED)
        return redirect(url_for('register'))
    # if the product has no product_id
    if product_id is None:
        abort(404)
    # if product is already in the user's cart, flash a message
    elif query_db('select 1 from cart where product_id = ?', [product_id], one=True):
        flash(FLASH_CART_PRODUCT)
        return redirect(url_for('show_product', product_id=product_id))
    # otherwise add to cart
    else:
        db = get_db()
        db.execute('''insert into cart (user_id, product_id, quantity) values
                    (?, ?, ?)''', (session['user_id'], product_id, quantity))
        db.commit()
        flash(FLASH_CARTED)
        return redirect(url_for('show_products_list'))

@app.route('/<int:product_id>/remove_product')
def remove_product(product_id):
    """Removes a product to the cart."""
    # user musts be logged in to access cart functionality
    if 'user_id' not in session:
        flash(FLASH_SIGNIN_NEEDED)
        return render_template('login.html')
    if product_id is None:
        abort(404)
    db = get_db()
    db.execute('''delete from cart where user_id = ? and product_id = ?''',
                (session['user_id'],product_id))
    db.commit()
    flash(FLASH_UNCARTED)
    return redirect(url_for('get_cart'))

@app.route('/clear_cart')
def clear_cart():
    """Clears everything in cart"""
    # user musts be logged in to access cart functionality
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
    """Updates a product's quantity in cart"""
    # user musts be logged in to access cart functionality
    if 'user_id' not in session:
        flash(FLASH_SIGNIN_NEEDED)
        return render_template('login.html')
    db = get_db()
    db.execute('''update cart set quantity = ? where user_id = ? and \
                product_id = ?''', (quantity,session['user_id'], product_id))
    db.commit()
    flash(FLASH_UPDATED)
    return redirect(url_for('get_cart'))




### Payment functions ###
@app.route('/pay')
def pay():
    """Displays the pay page with the Stripe Checkout Button."""
    global timer_on
    # get all the user's purchases
    purchases = query_db('''select cart.product_id, cart.quantity, \
                            product.title, product.price, \
                            product.quantity as inventory from cart \
                            join product on cart.product_id=product.product_id \
                            where cart.user_id=?''', [session['user_id']])
    # if there are no purchases, go back to cart
    if len(purchases)==0:
        flash(FLASH_NO_PURCHASES)
        return redirect(url_for('get_cart'))
    # check that all items are still in stock
    for purchase in purchases:
        # if the user wishes to purchase more than is in stock, flash message
        if purchase['inventory'] < purchase['quantity']:
            out_of_stock_message = FLASH_OUT_OF_STOCK % (purchase['title'],
                                                         purchase['title'])
            flash(out_of_stock_message)
            return redirect(url_for('get_cart'))
    # if all items are still in stock, put all items on hold while user pays
    if not timer_on:
        print "Putting on hold"
        db = get_db()
        cursor = db.cursor()
        transaction_ids = []
        for purchase in purchases:
            print "going through purchase"
            # add transactions to history, one row for each product
            cursor.execute('''insert into trans (
                            product_id, user_id, quantity, trans_date, amount)
                            values (?,?,?,?,?)''',
                            (purchase['product_id'], session['user_id'],
                            purchase['quantity'], datetime.utcnow(),
                            purchase['price']*purchase['quantity']))
            # keep track of the transaction id for each product in the cart
            transaction_ids.append(cursor.lastrowid)
            # update product inventory
            db.execute('''update product set quantity = quantity - ? where
                product_id = ?''', (purchase['quantity'], purchase['product_id']))
        db.commit()
        print "hold complete"
        # store the transaction_ids in the session
        session['transaction_ids'] = transaction_ids
        timer_on = True
        Timer(60, undo_hold, [session['transaction_ids']]).start()
    # store the amount the user must pay in the session
    session['amount'] = query_db('''select sum(product.price*cart.quantity)
                                    from cart join product on cart.product_id=
                                    product.product_id''', one=True)[0]
    # if the user is spending less than 5 yuan, flash message
    if session['amount'] < 500:
        flash(FLASH_AMOUNT_TOO_SMALL)
        return redirect(url_for('get_cart'))
    print "before render"
    return render_template('pay.html', key=stripe_keys['publishable_key'],
                            amount=session['amount'],
                            transaction_ids=session['transaction_ids'])

def undo_hold(transaction_ids):
    """Undo the hold on products that was initiated during checkout."""
    global timer_on
    print "in undo_hold"
    with app.app_context():
            db = get_db()
            for trans_id in transaction_ids:
                # get the transaction details
                purchase = query_db('select * from trans where trans_id=?',[trans_id])[0]
                # if the purchase was unconfirmed
                if purchase['confirmed']==0:
                    print "product put back"
                    # Put products back into product table
                    db.execute('''update product set quantity=quantity + ? where
                            product_id=?''', (purchase['quantity'], purchase['product_id']))
                # Do nothing to the transactions (they remain there as uncomfirmed).
            db.commit()
    timer_on = False
    print "undo_hold over"
    # if make_new_context:
    #     with app.test_request_context():
    #         db = get_db()
    #         for trans_id in transaction_ids:
    #             # get the transaction details
    #             purchase = query_db('select * from trans where trans_id=?',[trans_id])[0]
    #             # Put products back into product table
    #             db.execute('''update product set quantity=quantity + ? where
    #                     product_id=?''', (purchase['quantity'], purchase['product_id']))
    #             # Do nothing to the transactions (they remain there as uncomfirmed).
    #         db.commit()
    # else:
    #     db = get_db()
    #     for trans_id in transaction_ids:
    #         # get the transaction details
    #         purchase = query_db('select * from trans where trans_id=?',[trans_id])[0]
    #         # Put products back into product table
    #         db.execute('''update product set quantity=quantity + ? where
    #                 product_id=?''', (purchase['quantity'], purchase['product_id']))
    #         # Do nothing to the transactions (they remain there as uncomfirmed).
    #     db.commit()
    # print 'undone'
    # return False

@app.route('/charge', methods=['POST'])
def charge():
    """Charge the user."""
    global timer_on
    try:
        charge = stripe.Charge.create(
            amount=session['amount'], # Amount in cents
            currency="cny",
            source=request.form['stripeToken'])
    # for any exception, undo the hold and flash a message
    except stripe.error.CardError as e:
        # The account has been declined
        undo_hold(session['transaction_ids'])
        flash(FLASH_PAYMENT_ERROR)
    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        undo_hold(session['transaction_ids'])
        flash(FLASH_PAYMENT_ERROR)
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        undo_hold(session['transaction_ids'])
        flash(FLASH_PAYMENT_ERROR)
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        undo_hold(session['transaction_ids'])
        flash(FLASH_PAYMENT_ERROR)
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        undo_hold(session['transaction_ids'])
        flash(FLASH_PAYMENT_ERROR)
    except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        undo_hold(session['transaction_ids'])
        flash(FLASH_ERROR)
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        undo_hold(session['transaction_ids'])
        flash(FLASH_CARD_FAILURE)

    # if charge successful, then change the transactions to confirmed
    else:
        timer_on = False
        print "timer_on is now ", timer_on
        db = get_db()
        for trans_id in session['transaction_ids']:
            # confirm the transaction
            db.execute('update trans set confirmed=1 where trans_id=?', [trans_id])
        # empty the cart
        db.execute('''delete from cart where user_id = ?''', [session['user_id']])
        db.commit()
        # remove the variables amount, transaction_ids, and timer from session
        session.pop('amount', None)
        session.pop('transaction_ids', None)
        # flash message that purchase was succesful
        flash(FLASH_PURCHASE)
    return redirect(url_for('home'))




### Farmer Pages ###
@app.route('/stories')
def stories():
    """Display the stories page."""
    return render_template('stories.html')

@app.route('/<int:producer_id>/show_farmer')
def show_farmer(producer_id):
    """Show details of the farmer, including all his products."""
    producer_products = query_db('select * from product where producer_id= ?',
                                [producer_id])
    producer = query_db('select * from producer where producer_id=?',
                        [producer_id], one=True)
    return render_template('products_list.html',
                            products_list=producer_products, producer=producer)



### Admin pages ###
@app.route('/add_product', methods=['GET', 'POST'])
@admin_required
def add_product_db():
    """Add a product to the database."""
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
        photos = request.files
        if not request.form['producerid']:
            error = ERR_NO_PROD_PRODUCER_ID
            errtype = 'producerid'
        elif len(query_db('''select * from producer where producer_id=?''', \
            (request.form['producerid'],))) == 0:
            error = ERR_INVALID_PROD_PRODUCER_ID
            errtype = 'producerid'
        else:
            try:
                filenames = [None]*7
                i = 0
                for photo in photos:
                    if len(photos.get(photo).filename) != 0:
                        filenames[i] = upload_photos.save(photos.get(photo))
                    i = i + 1
            except UploadNotAllowed:
                error = FLASH_UPLOAD_FORBIDDEN
                errtype = 'uploaderror'
                return render_template('add_product.html', error=error, errtype=errtype)

            #store filename database
            db = get_db()
            print(filenames)
            db.execute('''insert into product (
                title, quantity, price, description, producer_id, standard_geo,
                standard_producer, standard_raw, standard_production, standard_storage,
                standard_tech, standard_package, standard_price,
                product_photo_filename_1, product_photo_filename_2, product_photo_filename_3,
                laotu_book_photo_filename_1, laotu_book_photo_filename_2, laotu_book_photo_filename_3, laotu_book_photo_filename_4)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?)''',
                [request.form['title'], int(request.form['quantity']), \
                    int(request.form['price']), request.form['description'], \
                    int(request.form['producerid']), request.form['standard_geo'],\
                    request.form['standard_producer'], request.form['standard_raw'],\
                    request.form['standard_production'], request.form['standard_storage'],\
                    request.form['standard_tech'], request.form['standard_package'],\
                    request.form['standard_price']] + filenames)
            db.execute('''insert into standards (organic_cert_1, organic_cert_2, organic_cert_3,
                organic_cert_4, organic_cert_5, organic_cert_6, organic_cert_7, organic_cert_8,
                quality_cert_1, quality_cert_2, producer_benifit_1, producer_benifit_2,
                producer_benifit_3, producer_benifit_4, producer_benifit_5, producer_benifit_6,
                consumer_benifit_1, local_1, local_2, local_3, package_1, package_2, ethnic_1,
                ethnic_2, ethnic_3, ethnic_4, ethnic_5, ethnic_6, ethnic_7, ethnic_8, ethnic_9,
                ethnic_10, production_1, production_2, production_3, production_4, production_5,
                craft_1, craft_2, craft_3, craft_4) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', [(standard in request.form) for
                standard in
                ["ORGANIC_CERT_1","ORGANIC_CERT_2","ORGANIC_CERT_3","ORGANIC_CERT_4",
                "ORGANIC_CERT_5","ORGANIC_CERT_6","ORGANIC_CERT_7", "ORGANIC_CERT_8",
                "QUALITY_CERT_1","QUALITY_CERT_2","PRODUCER_BENIFIT_1", "PRODUCER_BENIFIT_2",
                "PRODUCER_BENIFIT_3","PRODUCER_BENIFIT_4","PRODUCER_BENIFIT_5",
                "PRODUCER_BENIFIT_6", "CONSUMER_BENIFIT_1", "LOCAL_1","LOCAL_2","LOCAL_3","PACKAGE_1",
                "PACKAGE_2","ETHNIC_1","ETHNIC_2","ETHNIC_3","ETHNIC_4","ETHNIC_5","ETHNIC_6",
                "ETHNIC_7","ETHNIC_8","ETHNIC_9","ETHNIC_10","PRODUCTION_1","PRODUCTION_2",
                "PRODUCTION_3","PRODUCTION_4","PRODUCTION_5","CRAFT_1","CRAFT_2","CRAFT_3","CRAFT_4"]])
            db.commit()

            if tag_list.strip() != "":
                tag_list = request.form['tags'].split(';')
                tag_list = [t.strip() for t in tag_list]
                for tag in tag_list:
                    if len(query_db('''select * from tag where name=?''', \
                        (tag,))) == 0:
                        db.execute('''insert into tag (name, importance)
                            values (?, ?)''', [tag, DEFAULT_IMPORTANCE])
                        db.commit()
                    product_id = query_db('''select product_id from product''')[-1][0]
                    print product_id
                    tag_id = query_db('''select tag_id from tag where name=?''', (tag,))[0][0]
                    print tag_id
                    db.execute('''insert into product_to_tag (product_id, tag_id)
                        values (?, ?)''', (product_id, tag_id))
                    db.commit()
            flash(FLASH_PROD_ADD_SUCCESSFUL)
            error = None
            errtype = errtype
    return render_template('add_product.html', error=error, errtype=errtype)

@app.route('/del/<int:product_id>')
@admin_required
def del_product_db(product_id):
    product = query_db('select * from product where product_id = ?', [product_id], one=True)
    #delete photos
    for i in range(14,21):
        os.remove(os.path.join(UPLOADED_PHOTOS_DEST, product[i]))
    db = get_db()
    db.execute('''delete from product where product_id = ?''', (product_id,))
    db.commit()

@app.route('/adminauth', methods=['GET', 'POST'])
def adminauth():
    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            email = ?''', [request.form['email']], one=True)
        # print("NEXT:"),
        # print(request.args.get('next'))
        if user is None:
            error = ERR_INVALID_EMAIL
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = ERR_INVALID_PWD
        elif query_db('''select * from admin where
            user_id = ?''', [user[0]], one=True) is None:
            error = ERR_NOT_ADMIN
        else:
            session['user_id'] = user['user_id']
            session['admin'] = True
            # print(url_for('products')+'?adm=1')
            #alt make a global?
            flash(FLASH_LOGGED_ADMIN)
            return redirect(request.args.get('next'))
    return render_template('adminauth.html', error=error)

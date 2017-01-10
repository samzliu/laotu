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

# configuration
DATABASE = '/tmp/laotu.db'
#DATABASE = '/Users/nataliapacheco-tallaj/Documents/TITW/laotu.db'
# DATABASE = 'C:\\Users\\samzliu\\Desktop\\LaoTu\\LaoTu\\laotu\\tmp\\laotu.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'


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
sqliteAdminBP = sqliteAdminBlueprint(dbPath = '/tmp/laotu.db')
app.register_blueprint(sqliteAdminBP, url_prefix='/sqlite')

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

#pages are below .................................................................

@app.route('/')
def home():
    """Home page"""
    return render_template('home.html')


"""
Login page
registration page

Blog homepage
blog -> external interface...


"""




@app.route('/timeline')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('public_timeline'))
    return render_template('timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id and (
            user.user_id = ? or
            user.user_id in (select whom_id from follower
                                    where who_id = ?))
        order by message.pub_date desc limit ?''',
        [session['user_id'], session['user_id'], PER_PAGE]))


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    return render_template('timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?''', [PER_PAGE]))


@app.route('/<email>')
def user_timeline(email):
    """Display's a users tweets."""
    profile_user = query_db('select * from user where email = ?',
                            [email], one=True)
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        followed = query_db('''select 1 from follower where
            follower.who_id = ? and follower.whom_id = ?''',
            [session['user_id'], profile_user['user_id']],
            one=True) is not None
    return render_template('timeline.html', messages=query_db('''
            select message.*, user.* from message, user where
            user.user_id = message.author_id and user.user_id = ?
            order by message.pub_date desc limit ?''',
            [profile_user['user_id'], PER_PAGE]), followed=followed,
            profile_user=profile_user)


@app.route('/<email>/follow')
def follow_user(email):
    """Adds the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(email)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('insert into follower (who_id, whom_id) values (?, ?)',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are now following "%s"' % email)
    return redirect(url_for('user_timeline', email=email))


@app.route('/<email>/unfollow')
def unfollow_user(email):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(email)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('delete from follower where who_id=? and whom_id=?',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are no longer following "%s"' % email)
    return redirect(url_for('user_timeline', email=email))


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        db = get_db()
        db.execute('''insert into message (author_id, text, pub_date)
          values (?, ?, ?)''', (session['user_id'], request.form['text'],
                                int(time.time())))
        db.commit()
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            email = ?''', [request.form['email']], one=True)
        if user is None:
            error = 'Invalid email'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['name']:
            error = 'You have to enter a name'
        elif not request.form['address']:
            error = 'You have to enter an address'
        elif not request.form['phone']:
            error = 'You have to enter a phone number'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['email']) is not None:
            error = 'The email is already taken'
        else:
            db = get_db()
            db.execute('''insert into user (
              email, pw_hash, name, address, phone) values (?, ?, ?, ?, ?)''',
              [request.form['email'],
               generate_password_hash(request.form['password']),request.form['name'], request.form['address'], request.form['phone']])
            db.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products_list')
def show_products_list():
    return render_template('products_list.html', products=query_db('''
    select * from product'''))

@app.route('/<int:product_id>')
def show_product(product_id):
    product = query_db('select * from product where product.product_id = ?', [product_id], one=True)
    return render_template('product.html', product=product)

@app.route('/<int:product_id>/add_product')
def add_product(product_id):
    """Adds a product to the cart."""
    if product_id is None:
        abort(404)
    price, title = query_db('select price, title from product where product_id = ?', [product_id], one=True)
    print price
    db = get_db()
    db.execute('''insert into cart (product_id, title, price) values (?, ?, ?)''', (str(product_id), title, str(price)))
    db.commit()
    # not showing up on the page
    flash.keep('The product has been added to the cart.')
    return redirect(url_for('show_products_list'))

@app.route('/cart')
def cart():
    #select product_id, quantity from cart where user_id = asdfsaf;
    return render_template('cart.html', items=query_db('select * from cart'))

#delete all elements in cart
    #delete from cart where user_id = safdsafsaf;

#update card
    #delete from card where user_id= sdfsaf and product_id = safsadf;
    #update cart set quantity = safsafsafsa where user_id = safdsafd and product_id = safsadf;

@app.route('/cart')
def get_cart():
    """Displays cart"""
    if not g.user:
        flash('You need to sign in first to access this functionality')
        return redirect(url_for('public_timeline'))
    return render_template('cart.html', messages=query_db('''
       select product_id, quantity from cart where user_id = ?''',
        [session['user_id']]))

@app.route('/remove_product', methods=['POST'])
def remove_from_cart():
    """Removes a product from cart"""
    if 'user_id' not in session:
        flash('You need to sign in first to access this functionality')
        return render_template('login.html')
    if request.form['text']:
        db = get_db()
        db.execute('''delete from cart where user_id = ? and product_id = ?''', (session['user_id'],session['product_id']))
        db.commit()
        flash('The product has been removed from cart.')
    return redirect(url_for('cart'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    """Removes a product from cart"""
    if 'user_id' not in session:
        flash('You need to sign in first to access this functionality')
        return render_template('login.html')
    if request.form['text']:
        db = get_db()
        db.execute('''delete from cart where user_id = ?''', (session['user_id']))
        db.commit()
        flash('The cart has been cleared')
    return redirect(url_for('cart'))
>>>>>>> 59cedbc9ef63d7737226d1238804308cbb3a8ea2

@app.route('/update_product', methods=['POST'])
def update_cart():
    """Updates a product from cart"""
    if 'user_id' not in session:
        return render_template('login.html')
    if request.form['text']:
        db = get_db()
        db.execute('''update cart set quantity = ? where user_id = ? and product_id = ?''', (session['quantity'],session['user_id'],session['product_id']))
        db.commit()
        flash('The cart has been updated')
    return redirect(url_for('cart'))


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
      flash.keep('Your purchase was successful.')
    return redirect(url_for('timeline'))

# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url

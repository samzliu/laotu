# laotu

~ To use:

1. Install anaconda: https://docs.continuum.io/anaconda/install

2. Create a python 2.7 virtual environment

conda create -n yourenvname python=x.x anaconda flask=0.11.1

3. Initialize a python 2.7 virtual environment using

source activate yourenvname

4. Change directory to where you cloned the laotu repo

5. Install the app from the root of the project directory (don't forget the ".")

pip install --editable .

6. Initialize the db, tell flask about the app, and run the app on localhost:

make

the application will greet you onhttp://localhost:5000/

(Copied from previous readme)
~ Is it tested?

You betcha.  Run the `python setup.py test` file to
see the tests pass.


Tasks:


Broken
    - cart: delete, update, add to card even if stuff is already in cart, checkout button

    - add_product photos
    - heroku

High prority:


    - remaining Chinese translation
    - blog/splashpage
    - blog formating with images
    - better product formating
    - wechat
    - conversion and rollout
    - emails
    -   Fix up order confirmation email templates (.txt and .html) to look how the laotu people want them to (also maybe include links for the item pages on the .html template)
    -   probably Laotu or the producer should also get an email when someone places an order so they...know...to...proceed...with delivery?
    -   setup the emails to get sent from an actual laotu email address (which one tho)


Low priority:
    - 404 page
    - guest checkout
    - producer registration
    - next page  over flow
    - download csv of transactions from admin page
    - user transaction history

Pending testing:
    - test order confirmation email with an actual transaction? how? idk but

For mail functionality pip install flask_mail==0.9.0

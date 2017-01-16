# laotu

~ To use:

2. install the app from the root of the project directory

pip install --editable .

3. tell flask about the right application:

export FLASK_APP=laotu

4. fire up a shell and run this:

python -m flask initdb

5. now you can run application in test mode:

PUBLISHABLE_KEY=pk_test_haUn12yj5cA394KQd0K37hzh SECRET_KEY=sk_test_52QkxEpzwiy1p4bNKTX18Vy7 python -m flask run

the application will greet you onhttp://localhost:5000/

~ Is it tested?

You betcha.  Run the `python setup.py test` file to
see the tests pass.



Tasks:


High prority:

    - images (Sam)

    - remaining Chinese translation (Nat)
    - product page (Carl)
    - multiple categories (Carl)
    - blog/splashpage (Sam)
    - add product seperate page 
    
    - formatting and translation
    - wechat
    - conversion and rollout
    - Fix up order confirmation email templates (.txt and .html) to look how the laotu people want them to (also maybe include links for the item pages on the .html template)
    - probably Laotu or the producer should also get an email when someone places an order so they...know...to...proceed...with delivery?
    - setup the emails to get sent from an actual laotu email address (which one tho)


Low priority:
    - 404 page
    - guest checkout
    - producer registration
    - next page 
    - download csv of transactions from admin page 
    - user transaction history 

Pending testing:
    - test order confirmation email with an actual transaction? how? idk but

For mail functionality pip install flask_mail==0.9.0 



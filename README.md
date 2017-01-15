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
    - anyone wanna give admin autologout a shot? (i.e. setting session['admin'] to False after loading an admin page) here's a ref on func decorators http://thecodeship.com/patterns/guide-to-python-function-decorators/
    - transaction and confirmation emails (Nat will humbly attempt)
    - add product seperate page 
    
    - formatting and translation
    - wechat
    - conversion and rollout


Low priority:
    - 404 page
    - guest checkout
    - producer registration
    - next page 
    - download csv of transactions from admin page 
    - user transaction history 

For mail functionality pip install flask_mail==0.9.0 



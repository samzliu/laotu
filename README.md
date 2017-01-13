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
    - translate to Chinese (Nat)
    - product page (Carl)
    - multiple categories (Carl)
    - blog/splashpage (Sam)
    - database updates: show transactions, decrease quantity (Lily)
    - admin authentication 
    - 
    
    - formatting
    - wechat
    - conversion and rollout


Low priority:
    - guest checkout
    - producer registration



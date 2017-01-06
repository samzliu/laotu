# laotu

~ To use:

2. install the app from the root of the project directory

pip install --editable .

3. tell flask about the right application:

export FLASK_APP=minitwit

4. fire up a shell and run this:

python -m flask initdb

5. now you can run minitwit:

python -m flask run

the application will greet you on
http://localhost:5000/

~ Is it tested?

You betcha.  Run the `python setup.py test` file to
see the tests pass.
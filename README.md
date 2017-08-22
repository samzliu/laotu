# Laotu

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

the application will greet you on http://localhost:5000/

### Tasks
High prority:   
    - deploy to heroku  
    - Laotu and producer should receive email after a user makes a purchase    
    - setup the emails to get sent from a laotu email address   

Low priority:   
    - guest checkout    
    - download csv of transactions from admin page  

For mail functionality pip install flask_mail==0.9.0

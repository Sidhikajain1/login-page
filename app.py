from flask import Flask, session, redirect, url_for, render_template, request, abort
from authlib.integrations.flask_client import OAuth
from flask import make_response
import os
import requests
import secrets
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(50)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'  
    }
)

# MongoDB Connection
connection_string = os.getenv("MONGO_CONNECTION_STRING")
client = MongoClient(connection_string)
db = client['auth_db']  
test_users_collection = db['test_users']  

# Route for login
@app.route('/login')
def login():
    session.clear()  
    return render_template('login.html')

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login/google')
def google_login():
    return google.authorize_redirect(
        redirect_uri=url_for('google_authorize', _external=True),
        prompt='select_account'
    )

@app.route('/login/google/authorize')
def google_authorize():
    token = google.authorize_access_token()

    token_verification = requests.get(
        'https://oauth2.googleapis.com/tokeninfo',
        params={'access_token': token['access_token']}
    )

    if token_verification.status_code != 200:
        print("Error: Token verification failed.")
        return abort(403) 

    token_info = token_verification.json()

    user_email = token_info.get('email')
    if not token_info.get('email_verified', False):
        print(f"Access denied: Email not verified for {user_email}")
        return abort(403)

    if not is_test_user(user_email):
        print(f"Access denied: Unauthorized email {user_email}")
        return abort(403)

    session['logged_in'] = True
    # session['email'] = user_email
    # print(f"Access granted: {user_email}")
    return redirect(url_for('home'))


def is_test_user(user_email):
    test_user = test_users_collection.find_one({"email": user_email})
    return test_user is not None  


@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    response = make_response(render_template('home.html'))

    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # For development only
    #os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run()

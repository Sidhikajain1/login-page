from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os
from functools import wraps
import secrets

app = Flask(__name__)
secret_key = secrets.token_urlsafe(50)
app.secret_key = secret_key  # Change this to a secure random key

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
# OAuth 2 client setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,# Replace with your Google Client Secret
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:  # Check if user is in session
            return render_template('home.html')
        #redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_authorize', _external=True)
    #https://sso-testing.azurewebsites.net/callback
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorize')
def google_authorize():
    try:
        # Get the access token from Google
        token = google.authorize_access_token()
        
        # Skip fetching user info for now and just set a placeholder if needed
        # session['user'] = {'name': 'User'}  # Uncomment if you want to set a dummy user
        
        # Redirect to home page after successful login
        return redirect(url_for('home'))
    except Exception as e:
        print(f"Error during Google authorization: {e}")
        return redirect(url_for('home'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')  # No need to pass user info for now

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

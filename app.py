from flask import Flask, render_template, request, redirect, url_for, session
import msal
import secrets  # Import secrets for generating a strong secret key
from app_config import B2C_TENANT, CLIENT_ID, REDIRECT_URI, SIGN_UP_SIGN_IN_POLICY, AUTHORITY

app = Flask(__name__)

# Generate a strong secret key (you can also hardcode this after generation)
app.secret_key = secrets.token_hex(16)  # Generates a random 32-character hex string

@app.route('/')
def index():
    return render_template('login.html')  # Render the login page

@app.route('/login')
def login_redirect():
    msal_app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY)
    return redirect(msal_app.get_authorization_request_url(
        scope=["openid", "offline_access"],
        redirect_uri=REDIRECT_URI,
    ))

@app.route('/getAToken')
def get_token():
    if 'error' in request.args:
        return f"Error: {request.args['error']}"

    if 'code' in request.args:
        msal_app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY)
        result = msal_app.acquire_token_by_authorization_code(
            request.args['code'],
            scopes=["openid", "offline_access"],
            redirect_uri=REDIRECT_URI,
        )

        if "access_token" in result:
            session['user'] = result.get("id_token_claims")  # Store user info in session
            return redirect(url_for('home'))
        else:
            return f"Could not acquire token: {result.get('error_description')}"

    return "No code found in request."

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('index'))  # Redirect to login if not authenticated

    return render_template('home.html', user=session['user'])  # Pass user info to home template

if __name__ == '__main__':
    app.run(debug=True)
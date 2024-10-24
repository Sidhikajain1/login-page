from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Route for login page
@app.route('/')
def login():
    return render_template('login.html')

# Route to handle login form submission
@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form['username']
    password = request.form['password']

    # Check if the provided username and password match the credentials
    if username == 'admin' and password == 'admin123':
        session['logged_in'] = True  # Set session variable
        return redirect(url_for('home'))
    else:
        return "Invalid login credentials, try again!"

# Route for the home page
@app.route('/home')
def home():
    # Check if the user is logged in, if not redirect to the login page
    if 'logged_in' in session and session['logged_in']:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

# Route to log out
@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove logged_in session variable
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

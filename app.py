from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Route for login page
@app.route('/')
def login():
    return render_template('login.html')

# Route to handle login form submission
@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'admin123':
        return redirect(url_for('home'))
    else:
        return "Invalid login credentials, try again!"

# Route for the home page
@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)

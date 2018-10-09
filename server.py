from jinja2 import StrictUndefined

from flask import (Flask, render_template, jsonify, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.secret_key = "ABC"

@app.route('/login')
def login():
    """ login page."""
    return render_template("login.html")

@app.route('/login', methods = ["POST"])
def logged_in():

    email = request.form.get("email")
    password = request.form.get("password")


    # user = User.query.filter_by(email = email).first()

    # if not user:
    #     flash("No such user")
    #     return redirect("/login")

    # if user.password == password:
    #     session['user_id']= user.user_id
    #     return redirect('/homepage')
    # else:
    #     flash("Incorrect password")
    #     return redirect("/login")

    return render_template('homepage.html')

@app.route('/sign_up')
def sign_up():

    return render_template("sign_up.html")


@app.route('/add_another')
def add_another():

    return render_template("add_another.html")

@app.route('/homepage')
def home():
    return render_template('/homepage.html')


@app.route('/homepage', methods = ["POST"])
def homepage():

    dogname = request.form.get("dogname")
    return render_template("homepage.html", dogname = dogname)
    

@app.route('/all_dogs')
def all_dogs():

    return render_template('all_dogs.html')

# @app.route('/sign_up', methods = ["POST"])
# def signed_up():

#     # fname = request.form.get("fname")
#     # lname = request.form.get("lname")
#     # email = request.form.get("email")
#     # password = request.form.get("password")
#     # age = request.form.get("age")
#     dogname = request.form.get("dogname")

#     return render_template("homepage.html", dogname = dogname)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
   
    app.jinja_env.auto_reload = app.debug

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
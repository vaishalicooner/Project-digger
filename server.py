from jinja2 import StrictUndefined

from flask import (Flask, render_template, jsonify, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Dog, Log, connect_to_db, db

app = Flask(__name__)

app.secret_key = "ABC"

@app.route('/')
def login():
    """ login page."""
    return render_template("login.html")

@app.route('/login', methods = ["POST"])
def logged_in():

    email = request.form.get("email")
    password = request.form.get("password")


    user = User.query.filter_by(email = email).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password == password:
        session['user_id']= user.user_id
        return redirect('/homepage')
    else:
        flash("Incorrect password")
        return redirect("/login")

    return render_template('homepage.html')

@app.route('/sign_up')
def sign_up():

    return render_template("sign_up.html")

@app.route('/sign_up', methods = ["POST"])
def signed_up():

    fname = request.form.get("fname")
    lname = request.form.get("lname")
    apt = request.form.get("apt")
    email = request.form.get("email")
    password = request.form.get("password")
    dogname = request.form.get("dogname")
    age = request.form.get("age")
    breed = request.form.get("breed")
    gender = request.form.get("gender")
    size = request.form.get("size")
    pic = request.form.get("pic")
    
    user_email = User.query.filter_by(email == "email")
    if user_email == email:
        flash("User already exists.")
        return redirect('/login')

    user_add = User(fname=fname, lname=lname, apt=apt, email=email,
        password=password)
    dog_add = Dog(dogname=dogname, age=age, breed=breed, 
        gender=gender, size=size, pic=pic, user=user_add)
    db.session.add(user_add)
    db.session.add(dog_add)
    db.session.commit()

    return redirect('/login')


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

    dogs_from_db = Dog.query.all()
    return render_template('all_dogs.html', dogs = dogs_from_db)


@app.route('/activity_log')
def activity_log():

    logs_from_db = Log.query.all()
    return render_template('activity_log.html', logs = logs_from_db)


@app.route('/profile')
def profile():

    profile_data = User.query.options(db.joinedload('dogs')).get(session['user_id'])

    return render_template('profile.html', profiles=profile_data)


@app.route("/logout")
def logged_out():
    
    # session.pop('user_id')
    flash("Logged-out")
    
    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
   
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
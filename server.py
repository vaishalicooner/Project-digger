from jinja2 import StrictUndefined
import os
import json
import pytz
import requests
from flask import (Flask, render_template, jsonify, redirect, request, flash, session, url_for, send_from_directory)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Dog, Log, connect_to_db, db
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = 'static/upload'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# app.jinja_env.undefined = StrictUndefined

# weather_api_key = os.environ['WEATHERs_API']
# url = 'http://api.openweathermap.org/data/2.5/weather?q=Sunnyvale'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "ABC"

@app.route('/')
def login():
    """ login page."""
    return render_template("login.html")

@app.route('/login', methods = ["POST"])
def logged_in():

    email = request.form.get("email")
    password = request.form.get("password")

    # user_name = User.query.get(session['user_id'])
    user = User.query.filter_by(email = email).first()
    
    if not user:
        flash("No such user")
        return redirect("/")

    if user.password == password:
        session['user_id']= user.user_id
        return redirect('/homepage')
        # return redirect('/homepage')
    else:
        flash("Incorrect password")
        return redirect("/")

@app.route('/forgot_password')
def forgot_password():

    email = request.args.get('email')
    session['email'] = email
    if email is None:
        flash("This user does not exist. Please sign up!")
        return render_template('sign_up.html')

    user = User.query.filter(User.email == email).first()
    print("Your password is {}".format(User.password))   
    return render_template('/')

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
    
    if User.query.filter_by(email=email).first() is not None:
        flash("User already exists.")
        return redirect('/')

    user_add = User(fname=fname, lname=lname, apt=apt, email=email,
        password=password)

    db.session.add(user_add)
    db.session.commit()
    flash('Successfully signed up')
    return render_template('/login.html')


@app.route('/add_dog')
def add_dog():

    return render_template("add_dog.html")

@app.route('/add_dog', methods=['POST'])
def added_another():

    dogname = request.form.get("dogname")
    age = request.form.get("age")
    breed = request.form.get("breed")
    gender = request.form.get("gender")
    size = request.form.get("size")

    user = User.query.get(session['user_id'])
    dog_add = Dog(dogname=dogname, age=age, breed=breed, 
        gender=gender, size=size, user=user)

    db.session.add(dog_add)
    db.session.commit()

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect('/add_dog')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(dog_add.dog_id)+filename))
    
    dog_add.pic = str(dog_add.dog_id)+file.filename

    db.session.commit()
    flash('Picture added')
    return redirect('/homepage')


@app.route('/homepage')
def home():

    present_log = Log.query.options(db.joinedload('dog')).filter(Log.checkout.is_(None)).all()
    weather = get_weather()
    profile_data = User.query.options(db.joinedload('dogs')).get(session['user_id'])

    dog = db.session.query(Dog.pic)
    return render_template('homepage.html', logs=present_log, dog_profiles=profile_data, 
        weather=weather, dog=dog)


# @app.route('/homepage', methods = ["POST"])
# def homepage():

#     present_log = Log.query.options(db.joinedload('dog')).filter(Log.checkout.is_(None)).all()
#     # profile_data = User.query.options(db.joinedload('dogs')).get(session['user_id'])
    
#     weather = get_weather()
#     # return render_template('homepage.html', logs=present_log, dog_profiles=profile_data, weather=weather)
#     return render_template("homepage.html", logs=present_log, weather=weather)


@app.route('/all_dogs')
def all_dogs():

    dogs_from_db = Dog.query.all()
    return render_template('all_dogs.html', dogs = dogs_from_db)


@app.route('/activity_log')
def activity_log():

    logs_from_db = Log.query.all()
    dogs_from_db = Dog.query.all()
    # logs_from_db = Log.query.options(db.joinedload('logs')).get(session['dog_id'])
    return render_template('activity_log.html', logs=logs_from_db, dogs=dogs_from_db)


@app.route('/profile')
def profile():

    profile_data = User.query.options(db.joinedload('dogs')).get(session['user_id'])

    return render_template('profile.html', profiles=profile_data)

@app.route('/checkin', methods=['POST'])
def checkin():

    dogs = request.form.getlist('dog')
    print(dogs);
    
    pacific = pytz.timezone('US/Pacific')
    in_time = datetime.now(tz=pacific)
    
    
    for dog_id in dogs:
        check_in_time = Log(checkin=in_time, dog_id=int(dog_id))
        db.session.add(check_in_time)
        db.session.commit()
    
    return jsonify({'check_in_time': in_time})
    # return jsonify({'check_in_time': in_time}, {'dog_id': dog_id})


@app.route('/checkout', methods=['POST'])
def checkout():

    dogs = request.form.getlist('dog')
    print(dogs)
    pacific = pytz.timezone('US/Pacific')
    out_time = datetime.now(tz=pacific)
    profile_data = User.query.options(db.joinedload('dogs')).get(session['user_id'])
    
    log_data = Log.query.filter_by(dog_id=profile_data.dogs[0].dog_id, checkout=None).one()

    log_data.checkout = out_time
    db.session.commit()

    # for dog_id in dogs:

    #     log_data.checkout = out_time
       
    #     db.session.commit()
    
    return jsonify({'check_out_time': out_time})

@app.route("/logout")
def logged_out():
    
    session.pop('user_id')
    flash("Logged-out")
    
    return redirect('/')


def get_weather():

    # user = User.query.filter_by(email=session["email"]).first()

    # weather = requests.get("http://api.openweathermap.org/data/2.5/weather?q=Sunnyvale")
    # weather_json = weather.text 
    weather_json = open("weather.json").read()

    weather_info = json.loads(weather_json)
    weather_dis = weather_info["weather"][0]["description"]
    # weather_icon = weather_info["weather"][0]["icon"]

    temp = weather_info["main"]["temp"]
    weather_temp = round((1.8 * (temp - 273)) +32)

    weather_dict = {"description": weather_dis, "temp": weather_temp}

    return weather_dict


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension

    app.debug = True
   
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
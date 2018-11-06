from jinja2 import StrictUndefined
import os
import json
import hashlib
import pytz
import requests
from flask import (Flask, render_template, jsonify, redirect, request, flash, session, url_for, send_from_directory)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Dog, Log, connect_to_db, db
from werkzeug.utils import secure_filename
from datetime import datetime
from pytz import timezone

UPLOAD_FOLDER = 'static/upload'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

weather_api_key = os.environ['WEATHER_API']
url = 'http://api.openweathermap.org/data/2.5/weather?q=Sunnyvale'

app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "ABC"

@app.route('/')
def login():
    """ Login page"""

    return render_template("login.html")

@app.route('/login', methods = ["POST"])
def logged_in():
    """Checks user email and password and if it's correct, checks them in"""

    email = request.form.get("email")
    password = request.form.get("password")
    password = password.encode() # converts into byte code
    user_hash_pwd = hashlib.sha256(password) # create a SHA-256 hash object
    user_hash_pwd = user_hash_pwd.hexdigest()  #digest is returned as a string 
                                                #object of double length, containing 
                                                #only hexadecimal digits.

    print(user_hash_pwd)

    user = User.query.filter_by(email = email).first()
    
    if not user:
        flash("No such user")
        return redirect("/")

    if user.password == user_hash_pwd:
        session['user_id']= user.user_id
        return redirect('/homepage')
    else:
        flash("Incorrect password")
        return redirect("/")

# @app.route('/forgot_password')
# def forgot_password():

#     email = request.args.get('email')
#     session['email'] = email
#     if email is None:
#         flash("This user does not exist. Please sign up!")
#         return render_template('sign_up.html')

#     user = User.query.filter(User.email == email).first()
#     print("Your password is {}".format(User.password))   
#     return render_template('/')

@app.route('/sign_up')
def sign_up():
    """Takes user info to sign-up"""

    return render_template("sign_up.html")

@app.route('/sign_up', methods = ["POST"])
def signed_up():
    """Takes user sign-up info and saves it to database"""

    fname = request.form.get("fname")
    lname = request.form.get("lname")
    apt = request.form.get("apt")
    email = request.form.get("email")
    password = request.form.get("password")
    password = password.encode()
    user_hash_pwd = hashlib.sha256(password)
    user_hash_pwd = user_hash_pwd.hexdigest()
    
    # Check if a user already exists
    if User.query.filter_by(email=email).first() is not None:
        flash("User already exists.")
        return redirect('/')

    
    user_add = User(fname=fname, lname=lname, apt=apt, email=email,
        password=user_hash_pwd)

    # add user to database
    db.session.add(user_add)
    # commit to save changes
    db.session.commit()
    flash('Successfully signed up')
    return render_template('/login.html')


@app.route('/add_dog')
def add_dog():
    """ Add dog info"""

    return render_template("add_dog.html")

@app.route('/add_dog', methods=['POST'])
def added_another():
    """Add dog info and save it to database"""

    dogname = request.form.get("dogname")
    age = request.form.get("age")
    breed = request.form.get("breed")
    gender = request.form.get("gender")
    size = request.form.get("size")

    # add dog for a particular user who's logged in
    user = User.query.get(session['user_id'])
    dog_add = Dog(dogname=dogname, age=age, breed=breed, 
        gender=gender, size=size, user=user)

    # add dog info to database
    db.session.add(dog_add)
    # commit to save changes
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

    # add dog pic to database along with it's id to avoid duplicates
    dog_add.pic = str(dog_add.dog_id)+file.filename

    db.session.commit()
    flash('Picture added')
    return redirect('/homepage')


@app.route('/homepage')
def home():
    """ Homepage """

    # get dogs which are present at the dog park at the moment.
    present_log = Log.query.options(db.joinedload('dog')).filter(Log.checkout.is_(None)).all()

    # getting weather API info
    weather = get_weather()

    # get all dogs for a user 
    profile_data = User.query.options(db.joinedload('dogs')).get(session['user_id'])

    # get dogs pictures from database
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
    """Get all dogs"""

    # get all dogs from database who have signed_up 
    dogs_from_db = Dog.query.all()
    return render_template('all_dogs.html', dogs = dogs_from_db)


@app.route('/peak_time.json')
def peak_time():
    """ graph to show number of dogs in park in a time frame"""

    checkin_data = {}
    checkout_data = {}

    logs_from_db = Log.query.options(db.joinedload('dog')).all()

    for log in logs_from_db:
        log.checkin = log.checkin.astimezone(timezone('US/Pacific'))
        # This gets trick when a dog is not checked out
        # log.checkout = log.checkout.astimezone(timezone('US/Pacific'))


    for hour in range(0, 25):
        for log in logs_from_db:
            if log.checkin.hour == hour:
                checkin_data[hour] = checkin_data.get(hour, 0) + 1
            # if log.checkout.hour == hour:
            #     checkout_data[hour] = checkout_data.get(hour, 0) + 1

    data = [0] * 17
    for key in checkin_data:
        idx = max(key - 6, 0) # make sure hour doesn't go below zero
        data[idx] = checkin_data[key]
    print(data)
    return jsonify(data)
    # return jsonify({'checkin_data': checkin_data, 'checkout_data': checkout_data})

    
@app.route('/activity_log')
def activity_log():
    """Activity log page showing dog check-in and check-out time"""

    # get all log data from database
    logs_from_db = Log.query.options(db.joinedload('dog')).all()
    date_format = '%m/%d/%Y %H:%M %p'

    for log in logs_from_db:
        log.checkin = log.checkin.astimezone(timezone('US/Pacific')).strftime(date_format)
        log.checkout = log.checkout.astimezone(timezone('US/Pacific')).strftime(date_format)
    
    return render_template('activity_log.html', logs=logs_from_db)


@app.route('/profile')
def profile():
    """User profile """

    # get user info from database including their dogs info
    profile_data = User.query.options(db.joinedload('dogs')).get(session['user_id'])

    return render_template('profile.html', profiles=profile_data)

@app.route('/checkin', methods=['POST'])
def checkin():
    """Checkin information"""


    date_format = '%m/%d/%Y %H:%M %p'
    # convert timezone from GMT to pacific timezone
    in_time = datetime.now(tz=pytz.timezone('US/Pacific'))
    print(in_time)
    
    # get dogs for the logged in user
    dogs = request.form.getlist('dog')
    dog_info = []

    message = "OK"

    for dog_id in dogs:

        dog = Dog.query.get(dog_id)
        checkedin = Log.query.filter_by(dog_id=dog_id).filter(Log.checkout.is_(None)).first()

        if checkedin:
            message = "You are already checked in."
        else:
            check_in_time = Log(checkin=in_time, dog=dog)
            dog_info.append({'name': dog.dogname, 'id': dog.dog_id})
            db.session.add(check_in_time)
            db.session.commit()

    in_time = in_time.strftime(date_format)
    # checkin_dogs = Dog.query.join(Log).filter(Log.checkout.is_(None))
    # checkedin_dogs = [ {'name': dog.dogname, 'id': dog.dog_id} for dog in checkin_dogs ]
    # return jsonify({'check_in_time': in_time, 'dog_names': dog_names, 'checkedin_dogs': checkedin_names}) 
    return jsonify({'check_in_time': in_time, 'dogs': dog_info, 'message': message})

@app.route('/checkout', methods=['POST'])
def checkout():
    """Checkout information"""

    dog_ids = request.form.getlist('dog')
    date_format = '%m/%d/%Y %H:%M %p'
    # convert timezone from GMT to pacific timezone
    out_time = datetime.now(tz=pytz.timezone('US/Pacific'))

    for dog_id in dog_ids:
        log_data = Log.query.filter_by(dog_id=int(dog_id), checkout=None).one()
        log_data.checkout = out_time
        db.session.commit()

    out_time = out_time.strftime(date_format)

    return jsonify({'check_out_time': out_time, 'dog_ids': dog_ids})

@app.route("/logout")
def logged_out():
    """Logout"""
    
    # delete user form session
    session.pop('user_id')
    flash("Logged-out")
    
    return redirect('/')


def get_weather():
    """Weather API"""

    headers = {'x-api-key': weather_api_key}
    response = requests.get(url, headers=headers)
    weather_info = response.json()

    # print(weather_info)
    #if offline use json file 
    # weather_json = open("weather.json").read()
    # weather_info = json.loads(weather_json)

    weather_dis = weather_info["weather"][0]["description"]
    weather_icon = weather_info["weather"][0]["icon"]

    temp = weather_info["main"]["temp"]
    weather_temp = round((1.8 * (temp - 273)) +32)

    weather_dict = {"description": weather_dis, "temp": weather_temp, "icon": weather_icon}


    return weather_dict


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension

    # app.debug = True
   
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
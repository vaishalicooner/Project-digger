DIGGER
Digger user Python/Flask framework that talks to a Postgres database via SQLAlchemy.Uers can signup/login and check their dogs in/out of the park using checkin/checkout button. Digger plots this activity log into graphs using chart.js. List of dogs in the park helps users decide whether they really want to take their dogs to the park.

Table of Contents:
    Tech Stack
    Features
    Setup/Installation
    To-Do
    License

Tech Stack:

Frontend: HTML%, Javascript, AJAX, jQuery, Bootstrap
Backend: Python, Flask, PostgreSQL, SQLAlchemy
Graph: Chart.js
API: openWeatherMap

Features:
User can Sign_up or if they have an account they can login to the Homepage.
Checkin/Checkout button lets user check their dogs in/out of the park.
When user clicks checkin it updates the database and from their list of dogs in the park. 
List of dogs helps user decide whether they really want to take their dogs to the park.
Users can also plan their visit based on the dog activity log.

Setup/Installation

To run Digger:
Install PostgreSQL (Mac OSX)
Clone this repo:
https://github.com/vaishalicooner/Project-digger.git

Create and activate virtual environment inside your Digger directory:
$ virtualenv env
source env/bin/activate

Install the dependencies:
pip3 install -r requirements.txt

Sign up to use OpenWeatherMap API.

Save your API keys in a file called secrets.sh using this format:

export WEATHER_API="YOUR_KEY_HERE"

Source your keys from your secrets.sh file into your virtual environment:
source secrets.sh

Set up the database:

createdb digger
python model.py
python seed.py
psql digger < digger.sql

Run the app:
python3 server.py

You can now navigate to 'localhost:5000/' to access Digger.

About the Developer:
Vaishali Cooner is a Software Engineer in the Bay Area. For more information visit https://www.linkedin.com/in/vaishalicooner/


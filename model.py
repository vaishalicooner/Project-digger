from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

# Model definitions

class User(db.Model):
    """User of Dog."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    apt = db.Column(db.Integer, nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User {} {} Apt no.{}>".format(self.fname, self.lname, self.apt_no)


class Dog(db.Model):


    __tablename__ = "dogs"

    dog_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    dogname = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    breed = db.Column(db.String(25), nullable=True)
    gender = db.Column(db.String(7), nullable=True)
    size = db.Column(db.String(7), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pic = db.Column(db.String(100), nullable=True)


    user = db.relationship('User', backref = 'dogs')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Dog {} Age {} Breed {} Gender {} Size {}>".format(self.dogname
        , self.age, self.breed, self.gender, self.size)

class Log(db.Model):

    __tablename__ = "logs"

    log_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # date = db.Column(db.DateTime, nullable=False)
    dog_id = db.Column(db.Integer, db.ForeignKey('dogs.dog_id'), nullable=False)
    checkin = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    checkout = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    dog = db.relationship('Dog', backref = 'logs')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Log: Check-in {} Check-out {}>".format(self.checkin, self.checkout)



def connect_to_db(app, db_uri='postgresql:///digger'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.
    from server import app
    connect_to_db(app)
    print("Connected to DB.")

from sqlalchemy import func
from model import User
from model import Dog
from model import Log

from model import connect_to_db, db
from server import app
import datetime


def load_users():
    """Load users from u.user into database."""

    print("Users")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    Log.query.delete()
    Dog.query.delete()
    User.query.delete()

    user1 = User(fname="Vaishali", lname="Cooner", email="vc@gmail.com", 
        password=123, apt=1)
    user2 = User(fname="Heather", lname="Mahan", email="hm@gmail.com", 
        password=123, apt=1)

    # We need to add to the session or it won't ever be stored
    db.session.add_all([user1, user2])

    print("dogs")

    dog1 = Dog(dogname="fluffy", age=3, breed="havanese", gender="female", 
        size="small", pic="abc", user=user1)
    dog2 = Dog(dogname="boris", age=2, breed="minpin", gender="male",
        size="small", pic="def", user=user2)

    # We need to add to the session or it won't ever be smovies (movie_id, title, released_at, imdb_url) VALUES (%(movie_id)s, %(title)s, %(released_at)s, %(imdb_url)s)'] [parameters: ({'movie_id': '1', 'title': None, 'released_at': datetime.datetime(1995, 1, 1, 0, 0), 'imdb_url': None}, {'movie_id': '2', 'title': None, 'released_at': datetime.datetime(1995, 1, 1, 0, 0), 'imdb_url': None}, {'movie_id': '3', 'title': None, 'released_at': datetime.datetime(1995, 1, 1, 0, 0), 'imdb_url': None}, {'movie_id': '4', 'title': None, 'released_at': datetime.datetime(1995, 1, 1, 0, 0), 'imdb_url': None}, {'movie_id': '5', 'title': None, 'released_at': datetime.datetime(1995, 1, 1, 0, 0), 'imdb_url': None}, {'movie_id': '6', 'title': None, 'released_at': datetime.datetime(1995, 1, 1, 0, 0), 'imdb_url': None}, {'movie_id': '7', 'title': None, 'released_at': datetime.datetime(1995, 1, 1, 0, 0), 'imdb_url': None}, {'movie_id': '8', 'title': None, 'released_at': datetime.datetime(1995, 1, 1, 0, 0), 'imdb_url': None}  ... displaying 10 of 1681 total bound parameter sets ...  {'movie_id': '1681', 'title': None, 'released_at': datetime.datetime(1994, 1, 1, 0, 0), 'imdb_url': None}, {'movie_id': '1682tored
    db.session.add_all([dog1,dog2])

    print("logs")

    log1 = Log(checkin='2018-10-09 2:40:10 PM', checkout='2018-10-09 2:30:10 PM', dog=dog1)
    log2 = Log(checkin='2018-10-09 2:42:20 PM', checkout='2018-10-09 2:58:10 PM', dog=dog2)
    # We need to add to the session or it won't ever be stored
    db.session.add_all([log1, log2])

    # Once we're done, we should commit our work
    db.session.commit()


if __name__ == "__main__":

    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
   
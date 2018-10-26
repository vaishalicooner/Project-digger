import server
import unittest
from io import BytesIO
from server import app
from model import db, connect_to_db
from seed import load_users


class ProjectTests(unittest.TestCase):
    """Tests for my routes."""

    def setUp(self):
        """Code to run before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        #check session
        app.config['SECRET_KEY'] = 'key'

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1


    def test_login_page(self):
        """Can we reach the login page?"""

        result = self.client.get("/")
        self.assertIn(b"Email:", result.data)


    def test_sign_up(self):
        """Can we reach sign_up page."""

        result = self.client.get("/sign_up")
        self.assertIn(b"fname", result.data)
        self.assertNotIn(b"dogname", result.data)


    def test_add_dog(self):
        """Can we reach the Add dog page?"""

        result = self.client.get("/add_dog")
        self.assertIn(b"Dog Name:", result.data)
        self.assertNotIn(b"fname", result.data)


    def test_logout(self):
        """Can we logout?"""

        result = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"Email:", result.data)
        self.assertNotIn(b"Welcome to Digger. Your dogs playground!", 
            result.data)


class TestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        load_users()
        
        def _mock_get_weather():

            return "Weather"
            server.get_weather = _mock_get_weather


    def test_login(self):
        """Can we reach the homepage?"""
        
        result = self.client.post("/login", data = {"email": "vaishalicooner@gmail.com", 
            "password": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"}, follow_redirects=True)
        self.assertIn(b"Welcome to Digger. Your dogs playground!", result.data)
        self.assertNotIn(b"Email:", result.data)


    def test_wrong_email(self):
        """Test if user enters wrong email or user doesn't exist."""

        result = self.client.post("/login", data={"email": "hello@gmail.com", 
                                "password": "abc"}, follow_redirects=True)
        self.assertIn(b"No such user", result.data)
        self.assertNotIn(b"Welcome to Digger. Your dogs playground!", result.data)


    def test_wrong_password(self):
        """Test if user enters wrong password."""

        result = self.client.post("/login", data={"email": "vc@gmail.com",
                                "password": "abc"}, follow_redirects=True)
        self.assertIn(b"Incorrect password", result.data)
        self.assertNotIn(b"Welcome to Digger. Your dogs playground!", result.data)


    def test_user_exist(self):
        """Test if user already exists."""

        result = self.client.post("/sign_up", data={"email": "vc@gmail.com", 
                                "password": "123"}, follow_redirects=True)
        self.assertIn(b"User already exists.", result.data)
        self.assertIn(b"Email:", result.data)
        self.assertNotIn(b"Successfully signed up", result.data)



    def test_user_signup(self):
        """Test if user is able to sign_up."""

        result = self.client.post("/sign_up", data={"fname": "Vaishali", 
                                "lname": "Cooner","apt": "1", 
                                "email": "vc@gmail.com", "password": "123"}, 
                                follow_redirects=True)
        self.assertIn(b"Email:", result.data)
        self.assertNotIn(b"Welcome to Digger. Your dogs playground!", result.data)


    def test_add_dog(self):
        """Can we Add dog?"""

        result = self.client.post("/add_dog", content_type='multipart/form-data',
                                data = {"dogname": "Fluffy", 
                                "age": "3", "breed": "Havanese", 
                                "gender": "Female", "size": "Small",
                                "file": (BytesIO(b"abc"), '3fluffy.jpg'), "user": 3}, 
                                follow_redirects=True)
        self.assertIn(b"Welcome to Digger.", result.data)
        # self.assertIn(b"List of dogs at present!", result.data)
        self.assertNotIn(b"Dog Name:", result.data)


    def test_all_dogs(self):
        """Test if we are getting all dogs from the database"""

        result = self.client.get("/all_dogs", follow_redirects=True)
        self.assertIn(b"All Dogs", result.data)
        self.assertIn(b"Fluffy", result.data)
        self.assertIn(b"Boris", result.data)


    def test_profile(self):
        """test if we are loading user profile."""

        result = self.client.get("/profile", follow_redirects=True)
        self.assertIn(b"Profile", result.data)
        self.assertIn(b"Vaishali", result.data)
        self.assertIn(b"Fluffy", result.data)


    # def _mock_get_weather():

    #     return "Weather"
    #     server.get_weather = _mock_get_weather

          
    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()


if __name__ == "__main__":
    unittest.main()
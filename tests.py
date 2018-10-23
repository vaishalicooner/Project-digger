import server
import unittest

from server import app
from model import db, connect_to_db
from seed import load_users

class ProjectTests(unittest.TestCase):
    """Tests for my routes."""

    def setUp(self):
        """Code to run before every test."""

        self.client = server.app.test_client()
        server.app.config['TESTING'] = True

    def test_login_page(self):
        """Can we reach the login page?"""

        result = self.client.get("/")
        self.assertIn(b"Email:", result.data)

    def test_sign_up(self):
        """Can we reach sign_up page."""

        result = self.client.get("/sign_up")
        self.assertIn(b"fname", result.data)

    def test_add_dog(self):
        """Can we reach the Add dog page?"""

        result = self.client.get("/add_dog")
        self.assertIn(b"dogname", result.data)

    def test_all_dogs(self):

        result = self.client.get("/all_dogs")
        self.assertIn(b"All dogs", result.data)


class TestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        load_users()

    def test_login(self):
        """Can we reach the homepage?"""
        
        result = self.client.post("/login", data = {"email": "vc@gmail.com", "password": "123"},
            follow_redirects=True)
        self.assertIn(b"Welcome to Digger. Your dogs playground!", result.data)
        self.assertNotIn(b"Email:", result.data)

    def test_add_dog(self):
        """Can we reach the Add dog page?"""

        result = self.client.get("/add_dog", data = {"dogname": "Fluffy", "age": "3", 
            "breed": "havanese", "gender": "Female", "size": "Small"},
            follow_redirects=True)
        self.assertIn(b"Dog Name:", result.data)

    
    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()




if __name__ == "__main__":
    unittest.main()
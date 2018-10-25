import server
import unittest
from server import app
from model import db, connect_to_db
from seed import load_users


class _mock_get_weather(unittest.Testcase):
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
        example_data()


        def _mock_get_weather():

        server.get_weather = _mock_get_weather

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()



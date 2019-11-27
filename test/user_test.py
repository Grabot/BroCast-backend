import unittest
from app import create_app, db
from app.view.models.user import User
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        bro = User(username='bro')
        bro.set_password('secret')
        self.assertFalse(bro.check_password('hacker'))
        self.assertTrue(bro.check_password('secret'))

    def test_bros(self):
        bro1 = User(username='bro1')
        bro2 = User(username='bro2')
        db.session.add(bro1)
        db.session.add(bro2)
        db.session.commit()
        # test to see if the bros both have 0 bros
        self.assertEqual(bro1.bros.all(), [])
        self.assertEqual(bro2.bros.all(), [])

        bro1.add_bro(bro2)
        db.session.commit()
        self.assertTrue(bro1.get_bro(bro2))
        self.assertEqual(bro1.bros.count(), 1)
        self.assertEqual(bro1.bros.first().username, 'bro2')
        self.assertEqual(bro2.user_bros.count(), 1)
        self.assertEqual(bro2.user_bros.first().username, 'bro1')


if __name__ == '__main__':
    unittest.main()

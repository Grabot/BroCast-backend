import unittest
from app import create_app, db
from app.view.models.bro import Bro
from config import Config
from sqlalchemy import func
from config import TestConfig


class BroModelTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        bro = Bro(bro_name='bro')
        bro.set_password('secret')
        self.assertFalse(bro.check_password('hacker'))
        self.assertTrue(bro.check_password('secret'))

    def test_bros(self):
        bro1 = Bro(bro_name='bro1')
        bro2 = Bro(bro_name='bro2')
        db.session.add(bro1)
        db.session.add(bro2)
        db.session.commit()
        # test to see if the bros both have 0 bros
        self.assertEqual(bro1.bros.all(), [])
        self.assertEqual(bro2.bros.all(), [])

        bro1.add_bro(bro2)
        db.session.commit()
        # First we test that when a bro adds another bro that there is a one way connection
        self.assertTrue(bro1.get_bro(bro2))
        self.assertEqual(bro1.bros.count(), 1)
        self.assertEqual(bro1.bro_bros.count(), 0)
        self.assertEqual(bro1.bros.first().bro_name, 'bro2')
        self.assertEqual(bro2.bro_bros.count(), 1)
        self.assertEqual(bro2.bros.count(), 0)
        self.assertEqual(bro2.bro_bros.first().bro_name, 'bro1')

        # If the bro adds the other bro back the connection should be both ways!
        bro2.add_bro(bro1)
        self.assertTrue(bro1.get_bro(bro2))
        self.assertTrue(bro2.get_bro(bro1))
        self.assertEqual(bro1.bros.count(), 1)
        self.assertEqual(bro1.bro_bros.count(), 1)
        self.assertEqual(bro1.bros.first().bro_name, 'bro2')
        self.assertEqual(bro2.bro_bros.count(), 1)
        self.assertEqual(bro2.bros.count(), 1)
        self.assertEqual(bro2.bro_bros.first().bro_name, 'bro1')

    def test_multiple_bros(self):
        bro3 = Bro()

    def test_bro_login(self):
        bro4 = Bro(bro_name="bro4")
        db.session.add(bro4)
        bro = Bro.query.filter(func.lower(Bro.bro_name) == func.lower("bro4")).first()
        self.assertEqual(bro, bro4)


if __name__ == '__main__':
    unittest.main()

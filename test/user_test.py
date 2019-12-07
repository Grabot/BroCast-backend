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

    def test_bro_add(self):
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
        self.assertEqual(len(bro1.bros.all()), 1)
        self.assertEqual(len(bro1.bro_bros.all()), 0)

        # We test that the correct
        brosbro = bro1.bros.first()
        self.assertNotEqual(brosbro, None)

        # Take the bros from the brosbro association table and test if they are correct
        test_bro1 = Bro.query.filter_by(id=brosbro.bro_id).first()
        test_bro2 = Bro.query.filter_by(id=brosbro.bros_bro_id).first()
        self.assertEqual(test_bro1.bro_name, 'bro1')
        self.assertEqual(test_bro2.bro_name, 'bro2')

        # Test that the other bro is also correctly set now.
        self.assertEqual(len(bro2.bros.all()), 0)
        self.assertEqual(len(bro2.bro_bros.all()), 1)

        # The association table should be the same but it should be contacted from the other Bro.
        brosbro = bro2.bro_bros.first()
        self.assertNotEqual(brosbro, None)

        # Again check the brosbro. It should be the same object.
        test_bro1 = Bro.query.filter_by(id=brosbro.bro_id).first()
        test_bro2 = Bro.query.filter_by(id=brosbro.bros_bro_id).first()
        self.assertEqual(test_bro1.bro_name, 'bro1')
        self.assertEqual(test_bro2.bro_name, 'bro2')

        # For the other bro there should be no brosbro connection
        # TODO: Possibly this will change. When a bro is added both paths are created with an active indication (maybe)
        self.assertEqual(bro2.bros.first(), None)
        # # If the bro adds the other bro back the connection should be both ways!
        bro2.add_bro(bro1)
        db.session.commit()

        self.assertTrue(bro1.get_bro(bro2))
        self.assertTrue(bro2.get_bro(bro1))

        self.assertEqual(len(bro1.bros.all()), 1)
        self.assertEqual(len(bro1.bro_bros.all()), 1)
        self.assertEqual(len(bro2.bros.all()), 1)
        self.assertEqual(len(bro2.bro_bros.all()), 1)

        brosbro = bro2.bros.first()
        self.assertNotEqual(brosbro, None)

        # This should now be a new associate table row
        test_bro1 = Bro.query.filter_by(id=brosbro.bro_id).first()
        test_bro2 = Bro.query.filter_by(id=brosbro.bros_bro_id).first()
        self.assertEqual(test_bro1.bro_name, 'bro2')
        self.assertEqual(test_bro2.bro_name, 'bro1')

        # Now the first bro should have the same associate table as the previous one.
        brosbro = bro1.bro_bros.first()
        self.assertNotEqual(brosbro, None)

        # This should now be a new associate table row
        test_bro1 = Bro.query.filter_by(id=brosbro.bro_id).first()
        test_bro2 = Bro.query.filter_by(id=brosbro.bros_bro_id).first()
        self.assertEqual(test_bro1.bro_name, 'bro2')
        self.assertEqual(test_bro2.bro_name, 'bro1')

    def test_bro_login(self):
        bro3 = Bro(bro_name="bro3")
        db.session.add(bro3)
        db.session.commit()
        bro = Bro.query.filter(func.lower(Bro.bro_name) == func.lower("bro3")).first()
        self.assertEqual(bro, bro3)

    def test_bro_search(self):
        # The bro that we will search fro
        bro4 = Bro(bro_name="bro4")
        db.session.add(bro4)
        db.session.commit()

        bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower('unknown_bro_name'))
        potential_bros = []
        for bro in bros:
            potential_bros.append({'bro_name': bro.bro_name, 'id': bro.id})
        self.assertEqual(potential_bros, [])

        bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro4.bro_name))
        potential_bros = []
        for bro in bros:
            potential_bros.append({'bro_name': bro.bro_name, 'id': bro.id})
        self.assertEqual(len(potential_bros), 1)
        self.assertEqual(potential_bros[0]['bro_name'], "bro4")
        # TODO @Sander: expand when users can have the same bro_name with different emotion

    def test_bro_delete(self):
        bro5 = Bro(bro_name="bro5")
        bro6 = Bro(bro_name="bro6")
        db.session.add(bro5)
        db.session.add(bro6)
        db.session.commit()
        bro5.add_bro(bro6)
        db.session.commit()
        self.assertTrue(bro5.get_bro(bro6))
        # We have added the bro and we know that this works because of previous tests. We now delete it
        bro5.remove_bro(bro6)
        db.session.commit()
        self.assertFalse(bro5.get_bro(bro6))


if __name__ == '__main__':
    unittest.main()

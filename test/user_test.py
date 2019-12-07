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

        # self.assertEqual(bro1.bros.first().bro_name, 'bro2')
        # self.assertEqual(bro2.bro_bros.count(), 1)
        # self.assertEqual(bro2.bros.count(), 1)
        # self.assertEqual(bro2.bro_bros.first().bro_name, 'bro1')

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

    def test_add_bro_api(self):
        # The bro wants to add his bro
        # so bros_bro should be added to bro's bro_bros and it should not be equal to bro
        bro = Bro(bro_name="bro5")
        bros_bro = Bro(bro_name="bro6")
        db.session.add(bro)
        db.session.add(bros_bro)
        db.session.commit()
        # test to see if the bros both have 0 bros
        self.assertEqual(bro.bros.all(), [])
        self.assertEqual(bros_bro.bros.all(), [])

        print("bro %s wants to add %s as a bro" % (bro.bro_name, bros_bro.bro_name))
        # We expect there to be only 1 but we don't do the 'first' call on the query
        # because we want it to fail if there are multiple results found for the bro_name
        logged_in_bro = Bro.query.filter(func.lower(Bro.bro_name) == func.lower("bro5"))
        index = 0
        for br in logged_in_bro:
            index += 1
        if index != 1:
            # The bro's should both be found within the database so this will give an error!
            return {'results': False}
        # We now no FOR SURE that it only found 1
        logged_in_bro = logged_in_bro.first()
        self.assertEqual(logged_in_bro, bro)

        bro_to_be_added = Bro.query.filter(func.lower(Bro.bro_name) == func.lower("bro6"))
        index = 0
        for br in bro_to_be_added:
            index += 1
        if index != 1:
            # The bro's should both be found within the database so this will give an error!
            return {'results': False}

        bro_to_be_added = bro_to_be_added.first()
        self.assertEqual(bro_to_be_added, bros_bro)

        logged_in_bro.add_bro(bro_to_be_added)
        db.session.commit()
        # First we test that when a bro adds another bro that there is a one way connection
        self.assertTrue(logged_in_bro.get_bro(bro_to_be_added))
        self.assertEqual(logged_in_bro.bros.count(), 1)
        self.assertEqual(logged_in_bro.bro_bros.count(), 0)
        self.assertEqual(logged_in_bro.bros.first().bro_name, 'bro6')
        self.assertEqual(bro_to_be_added.bro_bros.count(), 1)
        self.assertEqual(bro_to_be_added.bros.count(), 0)
        self.assertEqual(bro_to_be_added.bro_bros.first().bro_name, 'bro5')



if __name__ == '__main__':
    unittest.main()

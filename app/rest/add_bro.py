from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import jsonify
from app.view.models.bro import Bro
from app.view.models.bro_bros import BroBros
from sqlalchemy import func
from app import db


class AddBro(Resource):
    def get(self, bro, bros_bro):
        print("bro %s wants to add %s as a bro" % (bro, bros_bro))
        # We expect there to be only 1 but we don't do the 'first' call on the query
        # because we want it to fail if there are multiple results found for the bro_name
        logged_in_bro = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro))
        # TODO @Sander: I know this is bad. But I'm to lazy to fix it now. But you should make it better at some point
        index = 0
        for b in logged_in_bro:
            index += 1
        if index != 1:
            # The bro's should both be found within the database so this will give an error!
            return {'result': False}
        # We now no FOR SURE that it only found 1
        logged_in_bro = logged_in_bro.first()
        bro_to_be_added = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bros_bro))
        index = 0
        for b in bro_to_be_added:
            index += 1
        if index != 1:
            # The bro's should both be found within the database so this will give an error!
            return {'result': False}
        bro_to_be_added = bro_to_be_added.first()

        print("test association 1")
        # It is possible that the connection is already made. First look for the connection
        bro_association_1 = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bro_to_be_added.id).first()
        if bro_association_1 is not None:
            # TODO: maybe not False. Fix it.
            return {'result': False}

        print("test association 2")
        # Test the other way around!
        bro_association_2 = BroBros.query.filter_by(bro_id=bro_to_be_added.id, bros_bro_id=logged_in_bro.id).first()
        if bro_association_2 is not None:
            bro_association_2.set_accepted(True)
            db.session.commit()
            return {'result': True}

        print("create association")
        # If there is no association in the database we will create one.
        logged_in_bro.add_bro(bro_to_be_added)
        db.session.commit()
        return {'result': True}

    def put(self, bro, bros_bro):
        pass

    def delete(self, bro, bros_bro):
        pass

    def post(self, bro, bros_bro):
        pass


api = Api(app_api)
api.add_resource(AddBro, '/api/v1.0/add/<string:bro>/<string:bros_bro>', endpoint='add_bro')


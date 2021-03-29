from app.models.bro_bros import BroBros
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from app.models.bro import Bro
from sqlalchemy import func
from app import db


class Add(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        json_data = request.get_json(force=True)
        token = json_data["token"]
        bros_bro_bro_name = json_data["bros_bro_bro_name"]
        bros_bro_bromotion = json_data["bros_bro_bromotion"]
        logged_in_bro = Bro.verify_auth_token(token)
        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        print("bro %s wants to add %s %s as a bro" % (logged_in_bro.bro_name, bros_bro_bro_name, bros_bro_bromotion))
        bro_to_be_added = Bro.query.filter(
            func.lower(Bro.bro_name) == func.lower(bros_bro_bro_name),
            Bro.bromotion == bros_bro_bromotion)

        if bro_to_be_added.count() != 1:
            # The bro's should both be found within the database so this will give an error!
            return {
                "result": False,
                "message": "The Bro could not be added"
            }
        bro_to_be_added = bro_to_be_added.first()
        print(bro_to_be_added.serialize)

        bro_association_1 = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bro_to_be_added.id).first()
        if bro_association_1 is not None:
            return {
                "result": True,
                "message": "You're already bros with the selected bro!"
            }

        bro_association_2 = BroBros.query.filter_by(bro_id=bro_to_be_added.id, bros_bro_id=logged_in_bro.id).first()
        if bro_association_2 is not None:
            db.session.commit()
            return {
                "result": True,
                "message": "You're already bros with the selected bro!"
            }

        print("create association")
        # If there is no association in the database we will create one.
        logged_in_bro.add_bro(bro_to_be_added)
        db.session.commit()
        return {
            "result": True,
            "message": "You and bro %s %s are now bros!" % (bro_to_be_added.bro_name, bro_to_be_added.bromotion)
        }


api = Api(app_api)
api.add_resource(Add, '/api/v1.0/add', endpoint='add')

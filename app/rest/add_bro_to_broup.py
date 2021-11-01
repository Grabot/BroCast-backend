from app.models.bro import Bro
from app import db
from app.models.broup import Broup
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from json import loads
from sqlalchemy import func
import random


class AddBroToBroup(Resource):

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
        logged_in_bro = Bro.verify_auth_token(token)
        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        broup_id = json_data["broup_id"]
        bro_id = json_data["bro_id"]

        broup_objects = Broup.query.filter_by(broup_id=broup_id)
        if broup_objects is None:
            return {
                "result": False,
                "message": "Could not find broup."
            }
        else:
            for broup in broup_objects:
                db.session.add(broup)

            db.session.commit()

        return {
            'result': True,
            "message": "Congratulations, the bro was added"
        }, 200


api = Api(app_api)
api.add_resource(AddBroToBroup, '/api/v1.2/add_bro_to_broup', endpoint='add_bro_to_broup')

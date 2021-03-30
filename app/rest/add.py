from flask import request
from flask_restful import Api
from flask_restful import Resource

from app import db
from app.models.bro import Bro
from app.rest import app_api


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
        bros_bro_id = json_data["bros_bro_id"]
        logged_in_bro = Bro.verify_auth_token(token)
        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        bro_to_be_added = Bro.query.filter_by(id=bros_bro_id).first()
        if bro_to_be_added is None:
            return {
                "result": False,
                "message": "Could not find your bro"
            }

        logged_in_bro.add_bro(bro_to_be_added)
        bro_to_be_added.add_bro(logged_in_bro)
        db.session.commit()

        return {
            "result": True,
            "message": "You and bro %s %s are now bros!" % (bro_to_be_added.bro_name, bro_to_be_added.bromotion)
        }


api = Api(app_api)
api.add_resource(Add, '/api/v1.0/add', endpoint='add')

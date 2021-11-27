from app import db
from flask import request
from flask_restful import Api
from flask_restful import Resource

from app.models.bro import Bro
from app.models.bro_bros import BroBros
from app.rest import app_api


class RemoveBro(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        json_data = request.get_json(force=True)
        bros_bro_id = json_data["bros_bro_id"]
        token = json_data["token"]
        logged_in_bro = Bro.verify_auth_token(token)
        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }
        if not bros_bro_id:
            return {
                "result": False,
                "message": "Bro not found."
            }

        chat = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bros_bro_id).first()
        if chat is None:
            return {
                "result": False,
                "message": "Chat not found."
            }
        chat.bro_removed()
        chat.block_chat(True)
        db.session.add(chat)
        db.session.commit()

        return {
                "result": True,
                "chat": chat.serialize
            }


api = Api(app_api)
api.add_resource(RemoveBro, '/api/v1.1/remove/bro', endpoint='remove_bro')

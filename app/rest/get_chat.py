from flask import request
from flask_restful import Api
from flask_restful import Resource

from app.models.bro_bros import BroBros
from app.rest import app_api


class GetChat(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        json_data = request.get_json(force=True)
        bro_id = json_data["bro_id"]
        bros_bro_id = json_data["bros_bro_id"]
        if not bro_id or not bros_bro_id:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        chat = BroBros.query.filter_by(bro_id=bro_id, bros_bro_id=bros_bro_id).first()
        if chat is None:
            return {
                "result": False,
                "message": "Chat not found."
            }

        return {
                "result": True,
                "chat": chat.serialize
            }


api = Api(app_api)
api.add_resource(GetChat, '/api/v1.0/get/chat', endpoint='get_chat')

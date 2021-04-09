from flask import request
from flask_restful import Api
from flask_restful import Resource

from app.models.bro import Bro
from app.models.bro_bros import BroBros
from app.models.message import Message
from app.rest import app_api


class GetMessages(Resource):
    def get(self, page):
        pass

    def put(self, page):
        pass

    def delete(self, page):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self, page):
        json_data = request.get_json(force=True)
        token = json_data["token"]
        bros_bro_id = json_data["bros_bro_id"]
        logged_in_bro = Bro.verify_auth_token(token)
        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        # Find the association between the bros only 1 way can exist, 2 or none should not be possible,
        # but an error should be given nonetheless
        messages = Message.query.filter_by(sender_id=logged_in_bro.id, recipient_id=bros_bro_id).\
            union(Message.query.filter_by(sender_id=bros_bro_id, recipient_id=logged_in_bro.id)).\
            order_by(Message.timestamp.desc()).paginate(1, 20 * page, False).items

        if messages is None:
            return {'result': False}

        return {
            "result": True,
            "message_list": [message.serialize for message in messages]
        }


api = Api(app_api)
api.add_resource(GetMessages, '/api/v1.0/get/messages/<int:page>', endpoint='get_messages')

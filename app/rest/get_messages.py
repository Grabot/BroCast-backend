from flask import request
from flask_restful import Api
from flask_restful import Resource

from app.models.bro import Bro
from app.models.bro_bros import BroBros
from app.sock.last_read_time import get_last_read_time_other_bro
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

        other_chat = BroBros.query.filter_by(bro_id=bros_bro_id, bros_bro_id=logged_in_bro.id).first()
        if other_chat is None:
            return {
                "result": False,
                "message": "Chat not found."
            }

        messages = Message.query.filter_by(sender_id=logged_in_bro.id, recipient_id=bros_bro_id).\
            union(Message.query.filter_by(sender_id=bros_bro_id, recipient_id=logged_in_bro.id)).\
            order_by(Message.timestamp.desc()).paginate(1, 20 * page, False).items

        if other_chat.has_been_blocked():
            print("this user has been blocked! don't show messages send while blocked")

        if messages is None:
            return {'result': False}

        last_read_time = get_last_read_time_other_bro(logged_in_bro.id, bros_bro_id)
        return {
            "result": True,
            "last_read_time_bro": last_read_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            "message_list": [message.serialize for message in messages]
        }


api = Api(app_api)
api.add_resource(GetMessages, '/api/v1.0/get/messages/<int:page>', endpoint='get_messages')

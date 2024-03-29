from flask import request
from flask_restful import Api
from flask_restful import Resource

from app.models.bro import Bro
from app.models.bro_bros import BroBros
from app.sock.last_read_time import get_last_read_time_other_bro
from app.models.message import Message
from app.rest import app_api
from datetime import datetime


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

        chat = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bros_bro_id).first()
        if chat is None:
            return {
                "result": False,
                "message": "Chat not found."
            }

        messages = Message.query.filter_by(sender_id=logged_in_bro.id, recipient_id=bros_bro_id).\
            union(Message.query.filter_by(sender_id=bros_bro_id, recipient_id=logged_in_bro.id)).\
            order_by(Message.timestamp.desc()).paginate(page, 20, False).items

        if chat.has_been_blocked():
            blocked_timestamps = chat.get_blocked_timestamps()
            for b in range(0, len(blocked_timestamps), 2):
                block_1 = blocked_timestamps[b]
                block_2 = datetime.utcnow()
                if b < len(blocked_timestamps) - 1:
                    block_2 = blocked_timestamps[b+1]
                # We go over the block timestamp pairs.
                # If the user is currently blocked, the last pair will be the block time and now
                messages = [message for message in messages if not block_1 <= message.get_timestamp() <= block_2]

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

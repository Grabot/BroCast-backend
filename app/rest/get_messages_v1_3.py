from flask import request
from flask_restful import Api
from flask_restful import Resource
from datetime import timedelta
from app.models.bro import Bro
from app.models.bro_bros import BroBros
from app.sock.last_read_time import get_last_read_time_other_bro
from app.models.message import Message
from app.rest import app_api
from datetime import datetime


class GetMessages_v1_3(Resource):
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

        chat = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bros_bro_id).first()
        if chat is None:
            return {
                "result": False,
                "message": "Chat not found."
            }

        # We will retrieve all messages available on the server after the bro's last read time. Even our own.
        messages = Message.query.filter_by(sender_id=logged_in_bro.id, recipient_id=bros_bro_id) \
            .union(Message.query.filter_by(sender_id=bros_bro_id, recipient_id=logged_in_bro.id)) \
            .filter(Message.timestamp >= (chat.last_message_read_time_bro - timedelta(minutes=5)))\
            .order_by(Message.timestamp.desc())\
            .all()

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
api.add_resource(GetMessages_v1_3, '/api/v1.3/get/messages', endpoint='get_messages_v1_3')

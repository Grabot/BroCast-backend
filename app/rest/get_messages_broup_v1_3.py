from datetime import datetime
from datetime import timedelta
from flask import request
from flask_restful import Api
from flask_restful import Resource
from app.models.bro import Bro
from app.models.broup import Broup
from app.models.broup_message import BroupMessage
from app.sock.last_read_time import get_lowest_read_time_broup
from app.rest import app_api


class GetMessagesBroup_v1_3(Resource):
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
        broup_id = json_data["broup_id"]
        logged_in_bro = Bro.verify_auth_token(token)
        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        chat = Broup.query.filter_by(broup_id=broup_id, bro_id=logged_in_bro.id).first()
        if chat is None:
            return {
                "result": False,
                "message": "Chat not found."
            }

        # We subtract a little from the last message read time. This is in case the user has the chat open and leaves
        # Sometimes not all the messages are received, we will receive them the next time
        messages = BroupMessage.query\
            .filter_by(broup_id=broup_id) \
            .filter(BroupMessage.timestamp >= (chat.last_message_read_time_bro - timedelta(minutes=5)))\
            .order_by(BroupMessage.timestamp.desc())\
            .all()

        if messages is None:
            return {'result': False}

        last_read_time = get_lowest_read_time_broup(broup_id, datetime.now())
        return {
            "result": True,
            "last_read_time_bro": last_read_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            "message_list": [message.serialize for message in messages]
        }


api = Api(app_api)
api.add_resource(GetMessagesBroup_v1_3, '/api/v1.3/get/messages/broup', endpoint='get_messages_broup_v1_3')

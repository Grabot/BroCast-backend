from datetime import datetime
from flask import request
from flask_restful import Api
from flask_restful import Resource
from app.models.bro import Bro
from app.models.broup import Broup
from app.models.broup_message import BroupMessage
from app.sock.last_read_time import get_lowest_read_time_broup
from app.rest import app_api


class GetMessagesBroup(Resource):
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

        messages = BroupMessage.query.filter_by(broup_id=broup_id).\
            order_by(BroupMessage.timestamp.desc()).paginate(page, 20, False).items

        if messages is None:
            return {'result': False}

        last_read_time = get_lowest_read_time_broup(broup_id, datetime.now())
        return {
            "result": True,
            "last_read_time_bro": last_read_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            "message_list": [message.serialize for message in messages]
        }


api = Api(app_api)
api.add_resource(GetMessagesBroup, '/api/v1.2/get/messages/broup/<int:page>', endpoint='get_messages_broup')

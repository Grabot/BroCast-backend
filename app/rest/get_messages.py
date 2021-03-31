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
        message_bro = Bro.query.filter_by(id=bros_bro_id).first()
        if message_bro is None:
            return {
                'result': False,
                'Message': 'The bro is not known'
            }

        # Find the association between the bros only 1 way can exist, 2 or none should not be possible,
        # but an error should be given nonetheless
        bro_association_1 = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=message_bro.id).first()
        bro_association_2 = BroBros.query.filter_by(bro_id=message_bro.id, bros_bro_id=logged_in_bro.id).first()
        messages = None
        if bro_association_1 is not None and bro_association_2 is not None:
            messages = Message.query.filter_by(bro_bros_id=bro_association_1.id).\
                union(Message.query.filter_by(bro_bros_id=bro_association_2.id)).\
                order_by(Message.timestamp.desc()).paginate(1, 20 * page, False).items
        else:
            return {
                'result': False,
                'Message': 'An unknown error has occurred'
            }

        if messages is None:
            return {'result': False}

        # print(messages)
        return {
            "result": True,
            "message_list": [message.serialize for message in messages]
        }


api = Api(app_api)
api.add_resource(GetMessages, '/api/v1.0/get/messages/<int:page>', endpoint='get_messages')

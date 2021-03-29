from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from flask import jsonify
from app.models.bro import Bro
from app.models.bro_bros import BroBros
from app.models.message import Message
from sqlalchemy import func
from app import db


class SendMessage(Resource):
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
        message = json_data["message"]
        logged_in_bro = Bro.verify_auth_token(token)
        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        bro_associate = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bros_bro_id)
        if bro_associate.first() is None:
            bro_associate = BroBros.query.filter_by(bro_id=bros_bro_id, bros_bro_id=logged_in_bro.id)
            if bro_associate.first() is None:
                return {
                    'result': False
                }

        bro_message = Message(
            sender_id=logged_in_bro.id,
            recipient_id=bros_bro_id,
            bro_bros_id=bro_associate.first().id,
            body=message
        )

        db.session.add(bro_message)
        db.session.commit()
        return {
            'result': True,
            'message': 'message send to bro: %s' % message
        }


api = Api(app_api)
api.add_resource(SendMessage, '/api/v1.0/send/message', endpoint='send_message')

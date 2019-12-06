from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from app.view.models.bro import Bro
from app.view.models.message import Message
from sqlalchemy import func
from app import db


class GetMessage(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    def post(self):
        json = request.get_json()
        print(json)
        # We will test each argument. If one of them is not available we send an error and not send the message.
        if len(json['bro']) == 0 or \
                len(json['bros_bro']) == 0 or \
                len(json['message']) == 0:
            return {'result': False}

        bro = json['bro']
        bros_bro = json['bros_bro']
        message = json['message']

        logged_in_bro = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro))
        index = 0
        for b in logged_in_bro:
            index += 1
        if index != 1:
            # The bro's should both be found within the database so this will give an error!
            return {'result': False}
        # We now no FOR SURE that it only found 1
        logged_in_bro = logged_in_bro.first()
        bro_to_be_added = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bros_bro))
        index = 0
        for b in bro_to_be_added:
            index += 1
        if index != 1:
            # The bro's should both be found within the database so this will give an error!
            return {'result': False}
        bro_to_be_added = bro_to_be_added.first()

        bro_message = Message(
            sender_id=logged_in_bro.id,
            recipient_id=bro_to_be_added.id,
            body=message
        )

        db.session.add(bro_message)
        db.session.commit()
        return {'result': True}


api = Api(app_api)
api.add_resource(GetMessage, '/api/v1.0/message', endpoint='get_message')


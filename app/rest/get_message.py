from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from app.view.models.bro import Bro
from app.view.models.message import Message
from sqlalchemy import func
from sqlalchemy import or_
from app import db


class GetMessage(Resource):
    def get(self, bro, bros_bro):
        print("getting messages")
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

        messages = Message.query.filter_by(sender_id=logged_in_bro.id, recipient_id=bro_to_be_added.id)
        for m in messages:
            print(m.body)
        return {'result': True}

    def put(self, bro, bros_bro):
        pass

    def delete(self, bro, bros_bro):
        pass

    def post(self, bro, bros_bro):
        json = request.get_json()
        # If there is no message we give an error.
        if len(json['message']) == 0:
            return {'result': False}

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
api.add_resource(GetMessage, '/api/v1.0/message/<string:bro>/<string:bros_bro>', endpoint='get_message')


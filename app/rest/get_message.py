from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from flask import jsonify
from app.view.models.bro import Bro
from app.view.models.bro_bros import BroBros
from app.view.models.message import Message
from sqlalchemy import func
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
        message_list = []
        for m in messages:
            message_list.append(m.body)
        return jsonify({'result': True,
                        'message_list': message_list})

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

        bro_associate_1 = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bro_to_be_added.id)
        if bro_associate_1 is None:
            return {'result': False}

        bro_message = Message(
            sender_id=logged_in_bro.id,
            recipient_id=bro_to_be_added.id,
            bro_bros_id=bro_associate_1.first().id,
            body=message
        )

        db.session.add(bro_message)
        db.session.commit()
        return {'result': True}


api = Api(app_api)
api.add_resource(GetMessage, '/api/v1.0/message/<string:bro>/<string:bros_bro>', endpoint='get_message')


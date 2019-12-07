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

        # The messages. We will fill the messages based on how the association is linked
        messages = None
        # Find the association between the bros only 1 way can exist, 2 or none should not be possible,
        # but an error should be given nonetheless
        bro_association_1 = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bro_to_be_added.id).first()
        if bro_association_1 is not None:
            messages = Message.query.filter_by(bro_bros_id=bro_association_1.id)


        bro_association_2 = BroBros.query.filter_by(bro_id=bro_to_be_added.id, bros_bro_id=logged_in_bro.id).first()
        if bro_association_2 is not None:
            messages = Message.query.filter_by(bro_bros_id=bro_association_2.id)

        if messages is None:
            return {'result': False}

        message_list = []
        for m in messages:
            sender = True
            if m.recipient_id == logged_in_bro.id:
                sender = not sender
            message_list.append({'sender': sender, 'body': m.body})
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

        # TODO: It is possible that this does not find anything, but that the relationship is the other way around.
        #  The relationship the other way around should be found to save and later find all the messages.
        bro_associate = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bro_to_be_added.id)
        if bro_associate.first() is None:
            # If the association does not exist it should exist in the other way around.
            # If this is not the case than we will show an error.
            bro_associate = BroBros.query.filter_by(bro_id=bro_to_be_added.id, bros_bro_id=logged_in_bro.id)
            if bro_associate.first() is None:
                return {'result': False}

        bro_message = Message(
            sender_id=logged_in_bro.id,
            recipient_id=bro_to_be_added.id,
            bro_bros_id=bro_associate.first().id,
            body=message
        )

        db.session.add(bro_message)
        db.session.commit()
        return {'result': True}


api = Api(app_api)
api.add_resource(GetMessage, '/api/v1.0/message/<string:bro>/<string:bros_bro>', endpoint='get_message')


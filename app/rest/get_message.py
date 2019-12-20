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
from app.rest.notification import send_notification


class GetMessage(Resource):
    def get(self, bro, bromotion, bros_bro, bros_bromotion, page):
        logged_in_bro = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro)).filter_by(bromotion=bromotion)
        index = 0
        for b in logged_in_bro:
            index += 1
        if index != 1:
            # The bro's should both be found within the database so this will give an error!
            return {'result': False}
        # We now no FOR SURE that it only found 1
        logged_in_bro = logged_in_bro.first()
        bro_to_be_added = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bros_bro)).filter_by(bromotion=bros_bromotion)
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
            messages = Message.query.filter_by(bro_bros_id=bro_association_1.id).\
                order_by(Message.timestamp.desc()).paginate(1, 20*page, False).items

        bro_association_2 = BroBros.query.filter_by(bro_id=bro_to_be_added.id, bros_bro_id=logged_in_bro.id).first()
        if bro_association_2 is not None:
            messages = Message.query.filter_by(bro_bros_id=bro_association_2.id).\
                order_by(Message.timestamp.desc()).paginate(1, 20*page, False).items

        if messages is None:
            return {'result': False}

        message_list = []
        for m in messages:
            sender = True
            if m.recipient_id == logged_in_bro.id:
                sender = not sender
            # We'll only send the hours, minutes and seconds. Our plan is to remove old messages automatically
            message_list.append({'sender': sender, 'body': m.body, 'timestamp': m.timestamp.strftime("%H:%M:%S")})
        return jsonify({'result': True,
                        'message_list': message_list})

    def put(self, bro, bromotion, bros_bro, bros_bromotion, page):
        pass

    def delete(self, bro, bromotion, bros_bro, bros_bromotion, page):
        pass

    def post(self, bro, bromotion, bros_bro, bros_bromotion, page):
        json = request.get_json()
        # If there is no message we give an error.
        if len(json['message']) == 0:
            return {'result': False}

        message = json['message']

        logged_in_bro = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro)).filter_by(bromotion=bromotion)
        index = 0
        for b in logged_in_bro:
            index += 1
        if index != 1:
            # The bro's should both be found within the database so this will give an error!
            return {'result': False}
        # We now no FOR SURE that it only found 1
        logged_in_bro = logged_in_bro.first()
        bro_to_send_to = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bros_bro)).filter_by(bromotion=bros_bromotion)
        index = 0
        for b in bro_to_send_to:
            index += 1
        if index != 1:
            # The bro's should both be found within the database so this will give an error!
            return {'result': False}
        bro_to_send_to = bro_to_send_to.first()

        # TODO: It is possible that this does not find anything, but that the relationship is the other way around.
        #  The relationship the other way around should be found to save and later find all the messages.
        bro_associate = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bro_to_send_to.id)
        if bro_associate.first() is None:
            # If the association does not exist it should exist in the other way around.
            # If this is not the case than we will show an error.
            bro_associate = BroBros.query.filter_by(bro_id=bro_to_send_to.id, bros_bro_id=logged_in_bro.id)
            if bro_associate.first() is None:
                return {'result': False}

        # TODO: if there are too many messages automatically remove 1
        bro_message = Message(
            sender_id=logged_in_bro.id,
            recipient_id=bro_to_send_to.id,
            bro_bros_id=bro_associate.first().id,
            body=message
        )

        db.session.add(bro_message)
        db.session.commit()

        send_notification(bro_to_send_to, "you have a new message from " + str(bro) + " " + str(bromotion), message)

        return {'result': True}


api = Api(app_api)
api.add_resource(GetMessage, '/api/v1.0/message/<string:bro>/<string:bromotion>/<string:bros_bro>/<string:bros_bromotion>/<int:page>', endpoint='get_message')


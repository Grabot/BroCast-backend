from app import db
from flask import request
from flask_restful import Api
from flask_restful import Resource
from datetime import datetime
import json

from app.models.bro import Bro
from app.models.bro_bros import BroBros
from app.models.log import Log
from app.models.message import Message
from app.rest import app_api


class ReportBro(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        json_data = request.get_json(force=True)
        bros_bro_id = json_data["bros_bro_id"]
        token = json_data["token"]
        logged_in_bro = Bro.verify_auth_token(token)
        bro_that_is_reported = Bro.query.filter_by(id=bros_bro_id).first()

        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        if not bro_that_is_reported:
            return {
                "result": False,
                "message": "Bro not found."
            }

        chat = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bros_bro_id).first()
        if chat is None:
            return {
                "result": False,
                "message": "Chat not found."
            }

        chat.bro_removed()
        chat.block_chat(True)

        # We take the last 40 messages from these bros to log.
        messages = Message.query.filter_by(sender_id=logged_in_bro.id, recipient_id=bros_bro_id). \
            union(Message.query.filter_by(sender_id=bros_bro_id, recipient_id=logged_in_bro.id)). \
            order_by(Message.timestamp.desc()).paginate(1, 40, False).items

        message_log = []
        for message in messages:
            message_log.append(json.dumps(message.serialize))

        log = Log(
            report_from=json.dumps(logged_in_bro.serialize),
            report_to=json.dumps(bro_that_is_reported.serialize),
            messages=message_log,
            report_date=datetime.utcnow()
        )

        db.session.add(chat)
        db.session.add(log)
        db.session.commit()

        return {
                "result": True,
                "chat": chat.serialize
            }


api = Api(app_api)
api.add_resource(ReportBro, '/api/v1.1/report/bro', endpoint='report_bro')

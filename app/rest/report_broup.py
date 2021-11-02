from app import db
from flask import request
from flask_restful import Api
from flask_restful import Resource
from datetime import datetime
import json
from app.models.bro import Bro
from app.models.broup import Broup
from app.models.broup_message import BroupMessage
from app.models.log import Log
from app.rest import app_api


def remove_last_occur(old_string, bromotion):
    new_string = ''
    length = len(old_string)

    for i in range(length-1, 0, -1):
        if old_string[i] == bromotion:
            new_string = old_string[0:i] + old_string[i + 1:length]
            break
    return new_string


class ReportBroup(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        json_data = request.get_json(force=True)
        broup_id = json_data["broup_id"]
        token = json_data["token"]
        logged_in_bro = Bro.verify_auth_token(token)

        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        broup_that_is_reported = Broup.query.filter_by(broup_id=broup_id, bro_id=logged_in_bro.id).first()
        broup_objects = Broup.query.filter_by(broup_id=broup_id)
        remove_bro = Bro.query.filter_by(id=logged_in_bro.id).first()
        if not broup_that_is_reported or not broup_objects or not remove_bro:
            return {
                "result": False,
                "message": "Broup not found."
            }

        # We take the last 100 messages from this broup to log.
        messages = BroupMessage.query.filter_by(broup_id=broup_id).\
            order_by(BroupMessage.timestamp.desc()).paginate(1, 100, False).items

        message_log = []
        for message in messages:
            message_log.append(json.dumps(message.serialize))

        log = Log(
            report_from=json.dumps(logged_in_bro.serialize),
            report_to=json.dumps(broup_that_is_reported.serialize),
            messages=message_log,
            report_date=datetime.utcnow()
        )

        db.session.add(log)

        remove_bromotion = remove_bro.get_bromotion()
        for broup in broup_objects:
            broup_name = remove_last_occur(broup.get_broup_name(), remove_bromotion)
            broup.set_broup_name(broup_name)
            broup.remove_bro(logged_in_bro.id)
            db.session.add(broup)

        # It's possible, that the user left the broup and that there are no more bros left.
        # In this case we will remove all the messages
        if len(broup_that_is_reported.get_participants()) == 0:
            messages = BroupMessage.query.filter_by(broup_id=broup_id)
            for message in messages:
                db.session.delete(message)
            db.session.add(broup_that_is_reported)
        broup_that_is_reported.mute_broup(True)
        broup_that_is_reported.broup_removed()

        db.session.add(broup_that_is_reported)
        db.session.commit()

        return {
                "result": True,
            }


api = Api(app_api)
api.add_resource(ReportBroup, '/api/v1.2/report/broup', endpoint='report_broup')

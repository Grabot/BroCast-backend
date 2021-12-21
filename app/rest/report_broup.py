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
from app.util.util import remove_last_occur


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

        if not broup_that_is_reported.has_left():
            remove_bromotion = remove_bro.get_bromotion()
            for broup in broup_objects:
                broup_name = remove_last_occur(broup.get_broup_name(), remove_bromotion)
                broup.set_broup_name(broup_name)
                broup.remove_bro(logged_in_bro.id)
                db.session.add(broup)

            # It's possible that the user who left was the only admin in the broup at the moment.
            # When there are no admins left we randomly assign a user to be admin.
            if len(broup_that_is_reported.get_admins()) == 0:
                # In this special event we will make everyone remaining an admin.
                for broup in broup_objects:
                    if not broup.has_left() and not broup.is_removed():
                        new_admin_id = broup.bro_id
                        for broup2 in broup_objects:
                            broup2.add_admin(new_admin_id)
                            db.session.add(broup2)
            # It's possible, that the user left the broup and that there are no more bros left.
            # In this case we will remove all the messages
            if len(broup_that_is_reported.get_participants()) == 0:
                messages = BroupMessage.query.filter_by(broup_id=broup_id)
                for message in messages:
                    db.session.delete(message)
            broup_that_is_reported.leave_broup()

        broup_that_is_reported.mute_broup(True)
        broup_that_is_reported.broup_removed()

        db.session.add(broup_that_is_reported)
        db.session.commit()

        return {
                "result": True,
                "chat": broup_that_is_reported.serialize
            }


api = Api(app_api)
api.add_resource(ReportBroup, '/api/v1.2/report/broup', endpoint='report_broup')

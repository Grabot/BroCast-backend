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

        broup_that_is_deleted = Broup.query.filter_by(broup_id=broup_id, bro_id=logged_in_bro.id).first()
        broup_objects = Broup.query.filter_by(broup_id=broup_id)
        remove_bro = Bro.query.filter_by(id=logged_in_bro.id).first()
        if not broup_that_is_deleted or not broup_objects or not remove_bro:
            return {
                "result": False,
                "message": "Broup not found."
            }

        broup_that_is_deleted.mute_broup(True)
        broup_that_is_deleted.broup_removed()

        db.session.add(broup_that_is_deleted)
        db.session.commit()

        return {
                "result": True,
                "chat": broup_that_is_deleted.serialize
            }


api = Api(app_api)
api.add_resource(ReportBroup, '/api/v1.3/delete/broup', endpoint='delete_broup')

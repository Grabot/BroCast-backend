from flask import request
from flask_restful import Api
from flask_restful import Resource
from app.models.bro import Bro
from app.models.broup import Broup
from app.rest import app_api
from app import db


class GetBroup(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        json_data = request.get_json(force=True)
        bro_id = json_data["bro_id"]
        broup_id = json_data["broup_id"]
        if not broup_id or not bro_id:
            return {
                "result": False,
                "message": "Broup not found."
            }

        chat = Broup.query.filter_by(broup_id=broup_id, bro_id=bro_id).first()

        if chat is None:
            return {
                "result": False,
                "message": "Chat not found."
            }

        if chat.check_mute():
            db.session.add(chat)
            db.session.commit()

        return {
                "result": True,
                "chat": chat.serialize
            }


api = Api(app_api)
api.add_resource(GetBroup, '/api/v1.2/get/broup', endpoint='get_broup')

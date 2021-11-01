from flask import request
from flask_restful import Api
from flask_restful import Resource
from app.models.bro import Bro
from app.models.broup import Broup
from app.rest import app_api


class GetBroup(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        print("getting the broup")
        json_data = request.get_json(force=True)
        token = json_data["token"]
        logged_in_bro = Bro.verify_auth_token(token)
        broup_id = json_data["broup_id"]
        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }
        if not broup_id:
            return {
                "result": False,
                "message": "Broup not found."
            }

        chat = Broup.query.filter_by(broup_id=broup_id, bro_id=logged_in_bro.id).first()
        if chat is None:
            return {
                "result": False,
                "message": "Chat not found."
            }

        return {
                "result": True,
                "chat": chat.serialize
            }


api = Api(app_api)
api.add_resource(GetBroup, '/api/v1.2/get/broup', endpoint='get_broup')

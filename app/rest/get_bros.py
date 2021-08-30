from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from app.models.bro import Bro


class GetBros(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        json_data = request.get_json(force=True)
        token = json_data["token"]
        logged_in_bro = Bro.verify_auth_token(token)
        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        bro_list = [bro_bro.serialize for bro_bro in logged_in_bro.get_bros()]
        broup_list = [broup.serialize for broup in logged_in_bro.get_broups()]

        return {
                "result": True,
                "bro_list": bro_list + broup_list
            }


api = Api(app_api)
api.add_resource(GetBros, '/api/v1.0/get/bros', endpoint='get_bros')

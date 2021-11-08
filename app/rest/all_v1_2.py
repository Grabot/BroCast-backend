from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from app.models.bro import Bro
from flask import request

debug_string = ""


class All_v1_2(Resource):

    # noinspection PyMethodMayBeStatic
    def get(self):
        global debug_string
        return {
            "result": True,
            "debug": debug_string,
        }

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        global debug_string
        json_data = request.get_json(force=True)
        debug_string = json_data
        return {
            "result": True,
            "json_data": json_data
        }


api = Api(app_api)
api.add_resource(All_v1_2, '/api/v1.2/all', endpoint='all_v1_2')

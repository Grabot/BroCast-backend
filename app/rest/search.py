from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import jsonify
from flask import request
from app.models.bro import Bro
from sqlalchemy import func


class Search(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        json_data = request.get_json(force=True)
        bro_name = json_data["bro_name"]
        bromotion = json_data["bromotion"]
        # TODO: @Skools Levenhstein distance?
        if bromotion == "":
            bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro_name))
        else:
            bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro_name)).filter_by(bromotion=bromotion)
        bro_list = []
        for bro in bros:
            bro_list.append(bro.serialize)
        return {
            "result": True,
            "bro_list": bro_list
        }


api = Api(app_api)
api.add_resource(Search, '/api/v1.0/search', endpoint='search')

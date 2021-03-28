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
        if bromotion == "None":
            bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro_name))
        else:
            bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro_name)).filter_by(bromotion=bromotion)
        potential_bros = []
        for bro in bros:
            potential_bros.append({'bro_name': bro.bro_name, 'bromotion': bro.bromotion, 'id': bro.id})
        return jsonify({'bros': potential_bros})


api = Api(app_api)
api.add_resource(Search, '/api/v1.0/search', endpoint='search')

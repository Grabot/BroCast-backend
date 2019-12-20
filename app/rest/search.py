from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import jsonify
from app.view.models.bro import Bro
from sqlalchemy import func


class Search(Resource):
    def get(self, bro, bromotion):
        if bromotion == "None":
            bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro))
        else:
            bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro)).filter_by(bromotion=bromotion)
        potential_bros = []
        for bro in bros:
            potential_bros.append({'bro_name': bro.bro_name, 'bromotion': bro.bromotion, 'id': bro.id})
        return jsonify({'bros': potential_bros})

    def put(self, bro, bromotion):
        pass

    def delete(self, bro, bromotion):
        pass

    def post(self, bro, bromotion):
        pass


api = Api(app_api)
api.add_resource(Search, '/api/v1.0/search/<string:bro>/<string:bromotion>', endpoint='search')


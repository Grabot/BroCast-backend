from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import jsonify
from app.view.models.bro import Bro
from sqlalchemy import func


class Search(Resource):
    def get(self, bro):
        bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro))
        potential_bros = []
        for bro in bros:
            potential_bros.append({'bro_name': bro.bro_name, 'id': bro.id})
        return jsonify({'bros': potential_bros})

    def put(self, bro):
        pass

    def delete(self, bro):
        pass

    def post(self, bro):
        pass


api = Api(app_api)
api.add_resource(Search, '/api/v1.0/search/<string:bro>/', endpoint='search')


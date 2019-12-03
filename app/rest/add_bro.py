from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import jsonify
from app.view.models.bro import Bro
from sqlalchemy import func


class AddBro(Resource):
    def get(self, bro, bros_bro):
        bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro))
        bro_names = []
        for bro in bros:
            bro_names.append([bro.bro_name, bro.id])
            print(bro.bro_name)
        return jsonify({'bro names': bro_names})

    def put(self, bro, bros_bro):
        pass

    def delete(self, bro, bros_bro):
        pass

    def post(self, bro, bros_bro):
        pass


api = Api(app_api)
api.add_resource(AddBro, '/api/v1.0/add/<string:bro>/<string:bros_bro>', endpoint='add_bro')


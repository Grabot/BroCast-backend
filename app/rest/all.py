from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from app.models.bro import Bro


class All(Resource):

    def get(self):
        bros = Bro.query.all()
        return {
            "bro_list": [bro.serialize for bro in bros]
        }

    def put(self):
        pass

    def delete(self):
        pass

    def post(self):
        pass


api = Api(app_api)
api.add_resource(All, '/api/v1.0/all', endpoint='all')

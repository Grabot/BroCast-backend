from app import db
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from app.models.bro import Bro


class Register(Resource):

    def get(self, bro_name, bromotion):
        bro = Bro(bro_name=bro_name, bromotion=bromotion)
        db.session.add(bro)
        db.session.commit()
        return {
            'result': True,
            'message': 'Congratulations, you have just added a bro',
            'bro': bro.serialize
        }

    def put(self, bro_name, bromotion):
        pass

    def delete(self, bro_name, bromotion):
        pass

    def post(self, bro_name, bromotion):
        pass


api = Api(app_api)
api.add_resource(Register, '/api/v1.0/register/<string:bro_name>/<string:bromotion>', endpoint='register')

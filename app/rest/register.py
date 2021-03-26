from app import db
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from app.models.bro import Bro
import sys


class Register(Resource):

    def get(self, bro_name, bromotion, password):
        bro = Bro(bro_name=bro_name, bromotion=bromotion)
        bro.hash_password(password)
        db.session.add(bro)
        db.session.commit()
        return {
            'result': True,
            'message': 'Congratulations, you have just added a bro',
            'bro': bro.serialize
        }, 200

    def put(self, bro_name, bromotion, password):
        pass

    def delete(self, bro_name, bromotion, password):
        pass

    def post(self, bro_name, bromotion, password):
        print("another test", flush=True)
        sys.stderr.write("a post on the register")
        sys.stdout.write("this is a quick test")
        json_data = request.get_json(force=True)
        print(json_data)
        pass


api = Api(app_api)
api.add_resource(Register, '/api/v1.0/register/<string:bro_name>/<string:bromotion>/<string:password>', endpoint='register')

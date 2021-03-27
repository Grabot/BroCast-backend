from app import db
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from flask import abort
from app.models.bro import Bro


class Register(Resource):

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
        password = json_data["password"]
        if bro_name is None or bromotion is None or password is None:
            abort(400)  # missing arguments
        if Bro.query.filter_by(bro_name=bro_name, bromotion=bromotion).first() is not None:
            return {
                'result': False,
                'message': "Bro name with bromotion combination is already taken, please provide another one."
            }, 400
        bro = Bro(bro_name=bro_name, bromotion=bromotion)
        bro.hash_password(password)
        db.session.add(bro)
        db.session.commit()
        token = bro.generate_auth_token()
        return {
            'result': True,
            'message': 'Congratulations, you have just added a bro',
            'bro': bro.serialize,
            'token': token.decode('ascii')
        }, 200


api = Api(app_api)
api.add_resource(Register, '/api/v1.0/register', endpoint='register')

from flask import request
from flask_restful import Api
from flask_restful import Resource

from app.models.bro import Bro
from app.rest import app_api
from app import db


class Login(Resource):

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
        token = json_data["token"]
        registration_id = json_data["registration_id"]

        bro = None
        if token is not None and not "":
            bro = Bro.verify_auth_token(token)

        if not bro:
            # The token was wrong (or was expired) Try to log in with username password and generate a new token
            bro = Bro.query.filter_by(bro_name=bro_name, bromotion=bromotion).first()
            if not bro or not bro.verify_password(password):
                return {
                   'result': False,
                   'message': 'The given credentials are not correct!'
                }, 401

        # Valid login, we refresh the token for this user.
        token = bro.generate_auth_token().decode('ascii')
        # update registration key if it's changed
        if bro.get_registration_id() != registration_id and registration_id != "":
            bro.set_registration_id(registration_id)
            db.session.add(bro)
            db.session.commit()

        return {
            'result': True,
            'message': 'Congratulations, you have just logged in',
            'bro': bro.serialize,
            'token': token
        }, 200


api = Api(app_api)
api.add_resource(Login, '/api/v1.0/login', endpoint='login')

from app import db
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from flask import abort
from app.models.bro import Bro
from sqlalchemy import func


class Register_v1_3(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        print("going to register")
        json_data = request.get_json(force=True)
        bro_name = json_data["bro_name"]
        bromotion = json_data["bromotion"]
        password = json_data["password"]
        registration_id = json_data["registration_id"]

        print("bro name: %s" % bro_name)
        if bro_name is None or bromotion is None or password is None or registration_id is None:
            abort(400)
        if Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro_name)).filter_by(bromotion=bromotion).first() is not None:
            return {
                'result': False,
                'message': "Bro name with bromotion combination is already taken, please provide another one."
            }, 400

        bro = Bro(bro_name=bro_name, bromotion=bromotion)
        bro.hash_password(password)
        bro.set_registration_id(registration_id)
        db.session.add(bro)
        db.session.commit()
        token = bro.generate_auth_token().decode('ascii')

        return {
            'result': True,
            'message': 'Congratulations, you have just added a bro',
            'bro': bro.serialize,
            'token': token
        }, 200


api = Api(app_api)
api.add_resource(Register_v1_3, '/api/v1.3/register', endpoint='register_v1_3')

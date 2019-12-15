from app import db
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from app.view.models.bro import Bro
from sqlalchemy import func


class Register(Resource):
    def get(self, bro_name, password, token):
        # First check if there is a bro with that name in the database
        bro_check = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro_name)).first()
        if bro_check is not None:
            return {
                'result': False,
                'message': "bro name is already taken! Please choose another one."
            }
        # If there is no bro with that name we can create a new bro and save it.
        bro = Bro(bro_name=bro_name)
        bro.set_password(password)
        bro.set_registration_id(token)
        db.session.add(bro)
        db.session.commit()
        return {
            'result': True,
            'message': "congratulations! " + bro_name + " is now registerd at BroCast. Happy BroCasting!"
        }

    def put(self, bro_name, password, token):
        pass

    def delete(self, bro_name, password, token):
        pass

    def post(self, bro_name, password, token):
        pass


api = Api(app_api)
api.add_resource(Register, '/api/v1.0/register/<string:bro_name>/<string:password>/<string:token>', endpoint='register')


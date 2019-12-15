from flask_restful import Api
from flask_restful import Resource
from app.rest import app_api
from app.view.models.bro import Bro


class Login(Resource):
    def get(self, bro_name, password):
        # We don't do the case sensitivity test here because the bro should give the proper name
        bro = Bro.query.filter_by(bro_name=bro_name).first()
        if bro is None or not bro.check_password(password):
            return {'result': False,
                    'reason': 'Invalid bro name or password'}

        token = bro.get_registration_id()
        return {'result': True,
                'token': token}

    def put(self, bro_name, password):
        pass

    def delete(self, bro_name, password):
        pass

    def post(self, bro_name, password):
        pass


api = Api(app_api)
api.add_resource(Login, '/api/v1.0/login/<string:bro_name>/<string:password>', endpoint='login')


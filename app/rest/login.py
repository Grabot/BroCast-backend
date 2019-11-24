from flask_restful import Api
from flask_restful import Resource
from app.rest import app_api
from app.view.models.user import User


class Login(Resource):
    def get(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            return {'result': 'failed',
                    'reason': 'Invalid username or password'}
        return {'result': 'success'}

    def put(self, username, password):
        pass

    def delete(self, username, password):
        pass

    def post(self, username, password):
        pass


api = Api(app_api)
api.add_resource(Login, '/api/v1.0/login/<string:username>/<string:password>', endpoint='login')


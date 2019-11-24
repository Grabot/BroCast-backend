from app import db
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from app.view.models.user import User


class Register(Resource):
    def get(self, username, password):
        print("user: " + username + " wants to register! He is using password: " + password)
        user = User(username=username)
        user.set_password(password)
        print("password after encryption is: " + user.get_password())
        db.session.add(user)
        db.session.commit()
        return {
            'message': "congratulations! " + username + " is now registerd at BroCast. Happy BroCasting!",
            'username': username,
            'password': password
        }

    def put(self, username, password):
        pass

    def delete(self, username, password):
        pass

    def post(self, username, password):
        pass


api = Api(app_api)
api.add_resource(Register, '/api/v1.0/register/<string:username>/<string:password>', endpoint='register')


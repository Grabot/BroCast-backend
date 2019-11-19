from app import db
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from app.view.models.user import User


class Register(Resource):
    def get(self, username):
        user = User(username=username)
        user.set_password('temp')
        db.session.add(user)
        db.session.commit()
        return {'message': 'congratulations! ' + username + " is now registerd at BroCast. Happy BroCasting!"}

    def put(self, username):
        pass

    def delete(self, username):
        pass

    def post(self):
        pass


api = Api(app_api)
api.add_resource(Register, '/api/v1.0/register/<string:username>', endpoint='register')


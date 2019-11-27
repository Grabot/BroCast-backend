from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import jsonify
from app.view.models.user import User
from sqlalchemy import func


class AddBro(Resource):
    def get(self, bro):
        users = User.query.filter(func.lower(User.username) == func.lower(bro))
        usernames = []
        for user in users:
            usernames.append([user.username, user.id])
            print(user.username)
        return jsonify({'usernames': usernames})

    def put(self, bro):
        pass

    def delete(self, bro):
        pass

    def post(self, bro):
        pass


api = Api(app_api)
api.add_resource(AddBro, '/api/v1.0/add/<string:bro>/', endpoint='add_bro')


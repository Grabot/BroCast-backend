from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import jsonify
from app.view.models.user import User
from sqlalchemy import func


class Search(Resource):
    def get(self, bro):
        users = User.query.filter(func.lower(User.username) == func.lower(bro))
        usernames = []
        for user in users:
            usernames.append(user.username)
            print(user.username)
        return jsonify({'usernames': usernames})

    def put(self, username):
        pass

    def delete(self, username):
        pass

    def post(self, username):
        pass


api = Api(app_api)
api.add_resource(Search, '/api/v1.0/search/<string:bro>/', endpoint='search')


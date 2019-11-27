from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import jsonify
from app.view.models.user import User
from sqlalchemy import func


class Search(Resource):
    def get(self, bro):
        users = User.query.filter(func.lower(User.username) == func.lower(bro))
        bros = []
        for user in users:
            bros.append({'username': user.username, 'id': user.id})
        return jsonify({'bros': bros})

    def put(self, bro):
        pass

    def delete(self, bro):
        pass

    def post(self, bro):
        pass


api = Api(app_api)
api.add_resource(Search, '/api/v1.0/search/<string:bro>/', endpoint='search')


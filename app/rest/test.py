from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from flask import jsonify


class PostTest(Resource):

    def get(self):
        print("get test post")

    def put(self):
        print("put test post")

    def delete(self):
        print("delete test post")

    def post(self):
        print("post test post")
        json = request.get_json()
        print(json)
        if len(json['bericht']) == 0:
            return jsonify({'error': 'invalid input'})

        return jsonify({'brocast bericht': json['bericht']})


api = Api(app_api)
api.add_resource(PostTest, '/api/post_test', endpoint='post_test')


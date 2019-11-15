from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource


class TaskListAPI3(Resource):

    def get(self):
        return {'tests': "test1"}

    def post(self):
        pass


api = Api(app_api)
api.add_resource(TaskListAPI3, '/test', endpoint='tasks')


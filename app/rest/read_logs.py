from app.config import Config
from flask_restful import Api
from flask_restful import Resource

from app.models.log import Log
from app.rest import app_api


class ReadLogs(Resource):

    # noinspection PyMethodMayBeStatic
    def get(self, password):
        if password != Config.LOG_READ_PASSWORD:
            return {
                "result": True,
                "log_list": ["no logs"]
            }
        logs = Log.query.all()
        return {
            "result": True,
            "log_list": [log.serialize for log in logs]
        }

    def put(self):
        pass

    def delete(self):
        pass

    def post(self):
        pass


api = Api(app_api)
api.add_resource(ReadLogs, '/api/v1.1/read/logs/<string:password>', endpoint='read_logs')

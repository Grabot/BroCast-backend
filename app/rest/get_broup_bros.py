from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from json import loads
from app.models.bro import Bro


class GetBroupBros(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        print("getting broup bros")
        json_data = request.get_json(force=True)
        token = json_data["token"]
        logged_in_bro = Bro.verify_auth_token(token)
        if not logged_in_bro:
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        participants = loads(json_data["participants"])

        if not participants:
            return {
                "result": False,
                "message": "Something went wrong."
            }

        print("filling list %s" % participants)
        bros = []
        for part in participants:
            bro_for_broup = Bro.query.filter_by(id=part).first()
            if bro_for_broup is None:
                return {
                    'result': False
                }
            bros.append(bro_for_broup)

        print(bros)
        bro_list = [bro.serialize for bro in bros]
        print(bro_list)
        return {
                "result": True,
                "bro_list": bro_list
            }


api = Api(app_api)
api.add_resource(GetBroupBros, '/api/v1.2/get/broup_bros', endpoint='get_broup_bros')

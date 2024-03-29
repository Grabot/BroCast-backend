from app.models.bro_bros import BroBros
from app.models.broup import Broup
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from app.models.bro import Bro
from flask import request


class All(Resource):

    # noinspection PyMethodMayBeStatic
    def get(self):
        amount_of_bros = len(Bro.query.all())
        amount_of_bro_chats = len(BroBros.query.all())
        amount_of_broup_chats = len(Broup.query.all())
        return {
            "result": True,
            "amount_of_bros": amount_of_bros,
            "amount_of_bro_chats": amount_of_bro_chats,
            "amount_of_broup_chats": amount_of_broup_chats,
        }

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        json_data = request.get_json(force=True)
        token = json_data["token"]
        bro = Bro.verify_auth_token(token)
        if not bro:
            return {
                "result": False,
                "message": "You're not authorized to view this. Please make an account at BroCast!"
            }
        else:
            bros = Bro.query.all()
            return {
                "result": True,
                "bro_list": [bro.serialize for bro in bros]
            }


api = Api(app_api)
api.add_resource(All, '/api/v1.0/all', endpoint='all')

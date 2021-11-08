from app.models.bro_bros import BroBros
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from app.models.bro import Bro
from sqlalchemy import func


class Search_v1_2(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        json_data = request.get_json(force=True)
        bro_name = json_data["bro_name"]
        token = json_data["token"]
        bromotion = json_data["bromotion"]
        searching_bro = Bro.verify_auth_token(token)
        if not searching_bro:
            return {
                "result": False,
                "message": "You're not authorized to view this. Please make an account at BroCast!"
            }
        else:
            if bromotion == "":
                bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro_name))
            else:
                bros = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro_name)).filter_by(bromotion=bromotion)
            bro_list = []
            for bro in bros:
                # Also check that the other bro hasn't blocked or removed this bro.
                chat = BroBros.query.filter_by(bro_id=bro.id, bros_bro_id=searching_bro.id).first()
                if chat is None:
                    # If the object don't exist they weren't friends before
                    bro_list.append(bro.serialize)

            return {
                "result": True,
                "bro_list": bro_list
            }


api = Api(app_api)
api.add_resource(Search_v1_2, '/api/v1.2/search', endpoint='search_v1_2')

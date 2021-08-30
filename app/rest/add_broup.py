from app.models.bro import Bro
from app import db
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from json import loads


class AddBroup(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        print("adding a new broup")
        json_data = request.get_json(force=True)

        token = json_data["token"]
        logged_in_bro = Bro.verify_auth_token(token)
        if not logged_in_bro:
            print("there was a problem")
            return {
                "result": False,
                "message": "Your credentials are not valid."
            }

        print("checking participants")
        participants = loads(json_data["participants"])
        broup_name = "broup_1"
        broup_name += " " + logged_in_bro.bromotion
        bro_ids = []
        broup = [logged_in_bro]
        for part in participants:
            bro_for_broup = Bro.query.filter_by(id=part).first()
            if bro_for_broup is None:
                return {
                    'result': False
                }
            broup.append(bro_for_broup)
            broup_name += " " + bro_for_broup.bromotion
            bro_ids.append(bro_for_broup.id)

        for bro in broup:
            bro.add_broup(broup_name, bro_ids)
            print(bro.serialize)

        db.session.commit()

        print("all good")
        return {
            'result': True,
            "message": "Congratulations, a broup was created"
        }, 200


api = Api(app_api)
api.add_resource(AddBroup, '/api/v1.2/add_broup', endpoint='add_broup')

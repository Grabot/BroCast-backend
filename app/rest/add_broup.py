from app.models.bro import Bro
from app import db
from app.models.broup import Broup
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import request
from json import loads
from sqlalchemy import func


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

        participants = loads(json_data["participants"])

        broup_name = json_data["broup_name"]
        broup_name += " " + logged_in_bro.bromotion

        max_broup_id = db.session.query(func.max(Broup.broup_id)).scalar()
        if max_broup_id is None:
            max_broup_id = 0
        broup_id = max_broup_id + 1

        bro_ids = [logged_in_bro.id]
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
            bro.add_broup(broup_name, broup_id, bro_ids)

        db.session.commit()

        return {
            'result': True,
            "message": "Congratulations, a broup was created"
        }, 200


api = Api(app_api)
api.add_resource(AddBroup, '/api/v1.2/add_broup', endpoint='add_broup')

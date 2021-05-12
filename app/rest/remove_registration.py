from flask import request
from flask_restful import Api
from flask_restful import Resource

from app import db
from app.models.bro import Bro
from app.rest import app_api


class RemoveRegistration(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    # noinspection PyMethodMayBeStatic
    def post(self):
        json_data = request.get_json(force=True)
        bro_to_remove_registration = Bro.query.filter_by(id=json_data["bro_id"]).first()
        if bro_to_remove_registration is None:
            return {'result': False}
        bro_to_remove_registration.set_registration_id("")
        db.session.add(bro_to_remove_registration)
        db.session.commit()
        return {
            "result": True,
            "message": "bro %s has successfully removed registration" % bro_to_remove_registration.bro_name
        }


api = Api(app_api)
api.add_resource(RemoveRegistration, '/api/v1.0/remove/registration', endpoint='removeRegistration')

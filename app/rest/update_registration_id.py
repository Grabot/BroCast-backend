from app import db
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from app.view.models.bro import Bro
from sqlalchemy import func


class UpdateRegistrationId(Resource):
    def get(self, bro, token):
        logged_in_bro = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro))
        index = 0
        for b in logged_in_bro:
            index += 1
        if index != 1:
            # The bro's should both be found within the database so this will give an error!
            return {'result': False}
        # We now no FOR SURE that it only found 1
        logged_in_bro = logged_in_bro.first()
        logged_in_bro.set_registration_id(token)
        db.session.add(logged_in_bro)
        db.session.commit()
        return {'result': True}

    def put(self, bro, token):
        pass

    def delete(self, bro, token):
        pass

    def post(self, bro, token):
        pass


api = Api(app_api)
api.add_resource(UpdateRegistrationId, '/api/v1.0/update/token/<bro>/<token>', endpoint='update_registration')


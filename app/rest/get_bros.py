from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import jsonify
from app.view.models.bro import Bro
from sqlalchemy import func


class GetBros(Resource):
    def get(self, bro):
        logged_in_bro = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro))
        index = 0
        for b in logged_in_bro:
            index += 1
        if index != 1:
            # The bro's should both be found within the database so this will give an error!
            return {'result': False}
        # We now no FOR SURE that it only found 1
        logged_in_bro = logged_in_bro.first()
        bros = logged_in_bro.bros
        bro_list = []
        for b in bros:
            bros_bro = Bro.query.filter_by(id=b.bros_bro_id).first()
            # We don't expect this to not return anything but we have a check anyway
            if bros_bro is not None:
                bro_list.append({'bro_name': bros_bro.bro_name, 'id': bros_bro.id})

        # We also want the bros that are in his list via invitation rather than being invitation or other way around.
        bro_bros = logged_in_bro.bro_bros
        for b in bro_bros:
            bros_bro = Bro.query.filter_by(id=b.bro_id).first()
            # We don't expect this to not return anything but we have a check anyway
            if bros_bro is not None:
                bro_list.append({'bro_name': bros_bro.bro_name, 'id': bros_bro.id})
        return jsonify({'result': True,
                        'bro_list': bro_list})

    def put(self, bro):
        pass

    def delete(self, bro):
        pass

    def post(self, bro):
        pass


api = Api(app_api)
api.add_resource(GetBros, '/api/v1.0/get/bros/<string:bro>', endpoint='get_bros')


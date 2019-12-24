from app import db
from app.rest import app_api
from flask_restful import Api
from flask_restful import Resource
from flask import jsonify
from app.view.models.bro import Bro
from sqlalchemy import func
from datetime import datetime
import time


class GetBros(Resource):
    def get(self, bro, bromotion):
        logged_in_bro = Bro.query.filter(func.lower(Bro.bro_name) == func.lower(bro)).filter_by(bromotion=bromotion)
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
                # Get the unread message count
                message_count = logged_in_bro.get_message_count(bros_bro)
                # We pass the time, we send it in unix time because we only use it to sort the list in correct order.
                last_message_time = logged_in_bro.get_last_message_time(bros_bro)
                time_unix = time.mktime(last_message_time.timetuple())
                bro_list.append({'bro_name': bros_bro.bro_name, 'bromotion': bros_bro.bromotion, 'message_count': message_count, 'last_message_time': time_unix, 'id': bros_bro.id})

        # We also want the bros that are in his list via invitation rather than being invitation or other way around.
        bro_bros = logged_in_bro.bro_bros
        for b in bro_bros:
            bros_bro = Bro.query.filter_by(id=b.bro_id).first()
            # We don't expect this to not return anything but we have a check anyway
            if bros_bro is not None:
                # Get the unread message count
                message_count = logged_in_bro.get_message_count(bros_bro)
                last_message_time = logged_in_bro.get_last_message_time(bros_bro)
                time_unix = time.mktime(last_message_time.timetuple())
                bro_list.append({'bro_name': bros_bro.bro_name, 'bromotion': bros_bro.bromotion, 'message_count': message_count, 'last_message_time': time_unix, 'id': bros_bro.id})

        # Before we send the bro list back we will update the last logging time.
        # This way we check new messages next time the user goes to the home screen
        logged_in_bro.last_message_read_time = datetime.utcnow()
        db.session.add(logged_in_bro)
        db.session.commit()
        return jsonify({'result': True,
                        'bro_list': bro_list})

    def put(self, bro, bromotion):
        pass

    def delete(self, bro, bromotion):
        pass

    def post(self, bro, bromotion):
        pass


api = Api(app_api)
api.add_resource(GetBros, '/api/v1.0/get/bros/<string:bro>/<string:bromotion>', endpoint='get_bros')


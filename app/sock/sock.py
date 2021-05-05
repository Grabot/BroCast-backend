from flask_socketio import Namespace
from flask_socketio import join_room
from flask_socketio import leave_room
from flask_socketio import emit
from flask import request
from app import socks
from app import db
from app.models.bro import get_a_room_you_two, Bro
from app.sock.message import send_message
from app.sock.last_read_time import update_read_time


class NamespaceSock(Namespace):

    # noinspection PyMethodMayBeStatic
    def on_connect(self):
        print('A client has connected!')

    # noinspection PyMethodMayBeStatic
    def on_disconnect(self):
        print('A client has disconnected :(')

    # noinspection PyMethodMayBeStatic
    def on_message_event(self, data):
        print("client send message: %s" % data)

    # noinspection PyMethodMayBeStatic
    def on_join(self, data):
        bro_id = data["bro_id"]
        bros_bro_id = data["bros_bro_id"]
        room = get_a_room_you_two(bro_id, bros_bro_id)
        print("joining room %s" % room)
        join_room(room)
        update_read_time(bro_id, bros_bro_id, room)
        emit("message_event", 'User has entered room %s' % room, room=room)

    # noinspection PyMethodMayBeStatic
    def on_leave(self, data):
        bro_id = data["bro_id"]
        bros_bro_id = data["bros_bro_id"]
        room = get_a_room_you_two(bro_id, bros_bro_id)
        print("leaving room %s" % room)
        leave_room(room)
        emit("message_event", 'User has left room %s' % room, room=room)

    # noinspection PyMethodMayBeStatic
    def on_message(self, data):
        message = send_message(data)
        if message is False:
            print("something has gone wrong")
        else:
            bro_id = data["bro_id"]
            bros_bro_id = data["bros_bro_id"]
            room = get_a_room_you_two(bro_id, bros_bro_id)
            print("send a message in room %s" % room)
            emit("message_event_send", message.serialize, room=room)

    # noinspection PyMethodMayBeStatic
    def on_message_read(self, data):
        bro_id = data["bro_id"]
        bros_bro_id = data["bros_bro_id"]
        room = get_a_room_you_two(bro_id, bros_bro_id)
        update_read_time(bro_id, bros_bro_id, room)

    # noinspection PyMethodMayBeStatic
    def on_bromotion_change(self, data):
        token = data["token"]
        logged_in_bro = Bro.verify_auth_token(token)
        print("trying to change bromotion")

        if logged_in_bro is None:
            emit("message_event_bromotion_change", "token authentication failed", room=request.sid)
        else:
            print("trying to change bromotion harder")
            new_bromotion = data["bromotion"]
            print("new bromotion ")
            print(new_bromotion)
            if Bro.query.filter_by(bro_name=logged_in_bro.bro_name, bromotion=new_bromotion).first() is not None:
                emit("message_event_bromotion_change", "broName bromotion combination taken", room=request.sid)
            else:
                logged_in_bro.set_bromotion(new_bromotion)

                db.session.add(logged_in_bro)
                db.session.commit()
                emit("message_event_bromotion_change", "bromotion change successful", room=request.sid)

    # noinspection PyMethodMayBeStatic
    def on_password_change(self, data):
        token = data["token"]
        logged_in_bro = Bro.verify_auth_token(token)
        print("trying to change password")

        if logged_in_bro is None:
            emit("message_event_password_change", "password change failed", room=request.sid)
        else:
            print("trying to change password harder")
            new_password = data["password"]
            logged_in_bro.hash_password(new_password)

            db.session.add(logged_in_bro)
            db.session.commit()
            emit("message_event_password_change", "password change successful", room=request.sid)


socks.on_namespace(NamespaceSock('/api/v1.0/sock'))

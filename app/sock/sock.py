from flask_socketio import Namespace
from flask_socketio import join_room
from flask_socketio import leave_room
from flask_socketio import emit
from flask import request
from app import socks
from app import db
from app.models.bro import get_a_room_you_two, Bro
from app.sock.message import send_message, send_message_broup
from app.sock.last_read_time import update_read_time
from app.sock.last_read_time import update_read_time_broup
from app.sock.chat_details import change_chat_details
from app.sock.chat_details import change_chat_alias
from app.sock.chat_details import change_chat_colour
from app.sock.chat_details import change_broup_details
from app.sock.chat_details import change_broup_alias
from app.sock.chat_details import change_broup_colour
from app.sock.chat_details import change_bromotion
from app.sock.chat_details import mute_broup
from app.sock.chat_details import mute_chat
from app.sock.chat_admins import change_broup_add_admin
from app.sock.chat_admins import change_broup_dismiss_admin
from app.sock.sock_add import change_broup_remove_bro
from app.sock.sock_add import add_bro
from app.sock.sock_add import add_broup
from app.sock.sock_add import add_bro_to_broup


class NamespaceSock(Namespace):

    # noinspection PyMethodMayBeStatic
    def on_connect(self):
        pass

    # noinspection PyMethodMayBeStatic
    def on_disconnect(self):
        pass

    # noinspection PyMethodMayBeStatic
    def on_message_event(self, data):
        pass

    # noinspection PyMethodMayBeStatic
    def on_join(self, data):
        bro_id = data["bro_id"]
        bros_bro_id = data["bros_bro_id"]
        room = get_a_room_you_two(bro_id, bros_bro_id)
        join_room(room)
        update_read_time(bro_id, bros_bro_id, room)
        emit("message_event", 'User has entered room %s' % room, room=room)

    # noinspection PyMethodMayBeStatic
    def on_join_solo(self, data):
        bro_id = data["bro_id"]
        room = "room_%s" % bro_id
        join_room(room)

        emit("message_event", 'User has entered room %s' % room, room=room)

    # noinspection PyMethodMayBeStatic
    def on_join_broup(self, data):
        bro_id = data["bro_id"]
        broup_id = data["broup_id"]
        broup_room = "broup_%s" % broup_id
        join_room(broup_room)
        update_read_time_broup(bro_id, broup_id, broup_room)
        emit("message_event", 'User has entered room %s' % broup_room, room=broup_room)

    # noinspection PyMethodMayBeStatic
    def on_leave(self, data):
        bro_id = data["bro_id"]
        bros_bro_id = data["bros_bro_id"]
        room = get_a_room_you_two(bro_id, bros_bro_id)
        leave_room(room)
        emit("message_event", 'User has left room %s' % room, room=room)

    # noinspection PyMethodMayBeStatic
    def on_leave_broup(self, data):
        bro_id = data["bro_id"]
        broup_id = data["broup_id"]
        broup_room = "broup_%s" % broup_id
        leave_room(broup_room)
        emit("message_event", 'User has left room %s' % broup_room, room=broup_room)

    # noinspection PyMethodMayBeStatic
    def on_leave_solo(self, data):
        bro_id = data["bro_id"]
        room = "room_%s" % bro_id
        leave_room(room)
        emit("message_event", 'User has entered room %s' % room, room=room)

    # noinspection PyMethodMayBeStatic
    def on_message(self, data):
        send_message(data)

    # noinspection PyMethodMayBeStatic
    def on_message_broup(self, data):
        send_message_broup(data)

    # noinspection PyMethodMayBeStatic
    def on_message_read(self, data):
        bro_id = data["bro_id"]
        bros_bro_id = data["bros_bro_id"]
        room = get_a_room_you_two(bro_id, bros_bro_id)
        update_read_time(bro_id, bros_bro_id, room)

    # noinspection PyMethodMayBeStatic
    def on_message_read_broup(self, data):
        bro_id = data["bro_id"]
        broup_id = data["broup_id"]
        broup_room = "broup_%s" % broup_id
        update_read_time_broup(bro_id, broup_id, broup_room)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_chat_details(self, data):
        change_chat_details(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_chat_alias(self, data):
        change_chat_alias(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_chat_colour(self, data):
        change_chat_colour(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_broup_details(self, data):
        change_broup_details(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_broup_alias(self, data):
        change_broup_alias(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_broup_colour(self, data):
        change_broup_colour(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_broup_add_admin(self, data):
        change_broup_add_admin(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_broup_dismiss_admin(self, data):
        change_broup_dismiss_admin(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_broup_remove_bro(self, data):
        change_broup_remove_bro(data)

    # noinspection PyMethodMayBeStatic
    def on_bromotion_change(self, data):
        change_bromotion(data)

    # noinspection PyMethodMayBeStatic
    def on_password_change(self, data):
        token = data["token"]
        logged_in_bro = Bro.verify_auth_token(token)

        if logged_in_bro is None:
            emit("message_event_password_change", "password change failed", room=request.sid)
        else:
            new_password = data["password"]
            logged_in_bro.hash_password(new_password)

            db.session.add(logged_in_bro)
            db.session.commit()
            emit("message_event_password_change", "password change successful", room=request.sid)

    # noinspection PyMethodMayBeStatic
    def on_message_event_add_bro(self, data):
        add_bro(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_add_broup(self, data):
        add_broup(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_add_bro_to_broup(self, data):
        add_bro_to_broup(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_broup_mute(self, data):
        mute_broup(data)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_chat_mute(self, data):
        mute_chat(data)


socks.on_namespace(NamespaceSock('/api/v1.0/sock'))

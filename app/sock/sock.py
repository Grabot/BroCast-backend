from flask_socketio import Namespace
from flask_socketio import join_room
from flask_socketio import leave_room
from flask_socketio import emit
from flask import request
from app import socks
from app import db
from app.models.bro import get_a_room_you_two, Bro
from app.models.bro_bros import BroBros
from app.sock.message import send_message, send_message_broup
from app.sock.last_read_time import update_read_time
from app.sock.last_read_time import update_read_time_broup
from app.sock.chat_details import change_chat_details
from app.sock.chat_details import change_chat_alias
from app.sock.chat_details import change_chat_colour
from app.sock.chat_details import change_broup_details
from app.sock.chat_details import change_broup_alias
from app.sock.chat_details import change_broup_colour
from app.sock.chat_admins import change_broup_add_admin
from app.sock.chat_admins import change_broup_dismiss_admin
from app.sock.chat_admins import change_broup_remove_bro

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
        print("joining the broup room: %s" % broup_room)
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
        print("leaving the broup room: %s" % broup_room)
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
        token = data["token"]
        logged_in_bro = Bro.verify_auth_token(token)

        if logged_in_bro is None:
            emit("message_event_bromotion_change", "token authentication failed", room=request.sid)
        else:
            new_bromotion = data["bromotion"]
            if Bro.query.filter_by(bro_name=logged_in_bro.bro_name, bromotion=new_bromotion).first() is not None:
                emit("message_event_bromotion_change", "broName bromotion combination taken", room=request.sid)
            else:
                logged_in_bro.set_bromotion(new_bromotion)
                all_chats = BroBros.query.filter_by(bros_bro_id=logged_in_bro.id).all()

                for chat in all_chats:
                    chat.chat_name = logged_in_bro.get_full_name()
                    db.session.add(chat)

                db.session.add(logged_in_bro)
                db.session.commit()
                emit("message_event_bromotion_change", "bromotion change successful", room=request.sid)

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
        token = data["token"]
        bros_bro_id = data["bros_bro_id"]
        logged_in_bro = Bro.verify_auth_token(token)
        if logged_in_bro:
            bro_to_be_added = Bro.query.filter_by(id=bros_bro_id).first()
            if bro_to_be_added:
                if bro_to_be_added.id != logged_in_bro.id:
                    logged_in_bro.add_bro(bro_to_be_added)
                    bro_to_be_added.add_bro(logged_in_bro)
                    db.session.commit()
                    bro_room = "room_%s" % bro_to_be_added.id
                    emit("message_event_add_bro_success", "bro was added!", room=request.sid)
                    emit("message_event_bro_added_you", "a bro has added you!", room=bro_room)
                else:
                    emit("message_event_add_bro_failed", "You tried to add yourself", room=request.sid)
            else:
                emit("message_event_add_bro_failed", "failed to add bro", room=request.sid)
        else:
            emit("message_event_add_bro_failed", "failed to add bro", room=request.sid)


socks.on_namespace(NamespaceSock('/api/v1.0/sock'))

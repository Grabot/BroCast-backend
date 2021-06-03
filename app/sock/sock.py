from flask_socketio import Namespace
from flask_socketio import join_room
from flask_socketio import leave_room
from flask_socketio import emit
from flask import request
from app import socks
from app import db
from app.models.bro import get_a_room_you_two, Bro
from app.models.bro_bros import BroBros
from app.rest.notification import send_notification
from app.sock.message import send_message
from app.sock.message import update_unread_messages
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
        join_room(room)
        update_read_time(bro_id, bros_bro_id, room)
        emit("message_event", 'User has entered room %s' % room, room=room)

    # noinspection PyMethodMayBeStatic
    def on_join_solo(self, data):
        token = data["token"]
        logged_in_bro = Bro.verify_auth_token(token)

        if logged_in_bro is None:
            emit("message_event", 'User could not enter the room', room=request.sid)
        else:
            room = "room_%s" % logged_in_bro.id
            join_room(room)
            emit("message_event", 'User has entered room %s' % room, room=room)

    # noinspection PyMethodMayBeStatic
    def on_leave(self, data):
        bro_id = data["bro_id"]
        bros_bro_id = data["bros_bro_id"]
        room = get_a_room_you_two(bro_id, bros_bro_id)
        leave_room(room)
        emit("message_event", 'User has left room %s' % room, room=room)

    # noinspection PyMethodMayBeStatic
    def on_leave_solo(self, data):
        token = data["token"]
        logged_in_bro = Bro.verify_auth_token(token)

        if logged_in_bro is None:
            emit("message_event", 'User could not leave the room', room=request.sid)
        else:
            room = "room_%s" % logged_in_bro.id
            leave_room(room)
            emit("message_event", 'User has entered room %s' % room, room=room)

    # noinspection PyMethodMayBeStatic
    def on_message(self, data):
        message = send_message(data)
        if message is False:
            print("something has gone wrong")
        else:
            room = get_a_room_you_two(data["bro_id"], data["bros_bro_id"])
            send_notification(data)
            update_unread_messages(data["bro_id"], data["bros_bro_id"])
            print("send a message in room %s" % room)
            emit("message_event_send", message.serialize, room=room)
            room_solo_other_bro = "room_%s" % data["bros_bro_id"]
            emit("message_event_send_solo", message.serialize, room=room_solo_other_bro)

    # noinspection PyMethodMayBeStatic
    def on_message_read(self, data):
        bro_id = data["bro_id"]
        bros_bro_id = data["bros_bro_id"]
        room = get_a_room_you_two(bro_id, bros_bro_id)
        update_read_time(bro_id, bros_bro_id, room)

    # noinspection PyMethodMayBeStatic
    def on_message_event_change_chat_details(self, data):
        print("going to change the chat details!")
        token = data["token"]
        bros_bro_id = data["bros_bro_id"]
        description = data["description"]
        logged_in_bro = Bro.verify_auth_token(token)

        if logged_in_bro is None:
            emit("message_event_change_chat_details_failed", "token authentication failed", room=request.sid)
        else:
            chat = BroBros.query.filter_by(bro_id=logged_in_bro.id, bros_bro_id=bros_bro_id).first()
            if chat is None:
                emit("message_event_change_chat_details_failed", "chat finding failed", room=request.sid)
            else:
                chat.update_description(description)
                db.session.add(chat)
                db.session.commit()
                emit("message_event_change_chat_details_success", "chat updated successfully", room=request.sid)

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
                logged_in_bro.add_bro(bro_to_be_added)
                bro_to_be_added.add_bro(logged_in_bro)
                db.session.commit()
                bro_room = "room_%s" % bro_to_be_added.id
                emit("message_event_add_bro_success", "bro was added!", room=request.sid)
                emit("message_event_bro_added_you", "a bro has added you!", room=bro_room)
            else:
                emit("message_event_add_bro_failed", "failed to add bro", room=request.sid)
        else:
            emit("message_event_add_bro_failed", "failed to add bro", room=request.sid)


socks.on_namespace(NamespaceSock('/api/v1.0/sock'))

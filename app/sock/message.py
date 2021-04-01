from flask import request
from flask_socketio import Namespace, emit
from flask_socketio import join_room, leave_room

from app import socks
from app import db
from app.models.bro import Bro
from app.models.bro_bros import BroBros
from app.models.message import Message


def send_message(data):
    bro_id = data["bro_id"]
    bros_bro_id = data["bros_bro_id"]
    message = data["message"]

    bro_associate = BroBros.query.filter_by(bro_id=bro_id, bros_bro_id=bros_bro_id)
    if bro_associate.first() is None:
        bro_associate = BroBros.query.filter_by(bro_id=bros_bro_id, bros_bro_id=bro_id)
        if bro_associate.first() is None:
            return False

    bro_message = Message(
        sender_id=bro_id,
        recipient_id=bros_bro_id,
        bro_bros_id=bro_associate.first().id,
        body=message
    )

    db.session.add(bro_message)
    db.session.commit()
    return bro_message


def get_a_room_you_two(bro_id, bros_bro_id):
    if bro_id >= bros_bro_id:
        return str(bros_bro_id) + "_" + str(bro_id)
    else:
        return str(bro_id) + "_" + str(bros_bro_id)


class NamespaceMessage(Namespace):

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
    def on_message(self, data):
        print("message?")
        print(data)
        print(request.sid)
        message = send_message(data)
        if message is False:
            print("something has gone wrong")
        else:
            bro_id = data["bro_id"]
            bros_bro_id = data["bros_bro_id"]
            room = get_a_room_you_two(bro_id, bros_bro_id)
            print("send a message in room %s" % room)
            emit('server_message_sent', data, broadcast=True)
            emit("message_event", {"message": message.serialize}, room=room)

    # noinspection PyMethodMayBeStatic
    def on_join(self, data):
        bro_id = data["bro_id"]
        bros_bro_id = data["bros_bro_id"]
        room = get_a_room_you_two(bro_id, bros_bro_id)
        print("joining room %s" % room)
        join_room(room)
        emit("message_event", 'User has entered room %s' % room, room=room)

    # noinspection PyMethodMayBeStatic
    def on_leave(self, data):
        token = data["token"]
        logged_in_bro = Bro.verify_auth_token(token)
        if not logged_in_bro:
            emit("message_event", "failed to log in!")
        room = "bro:" + logged_in_bro.id
        leave_room(room)
        emit("message_event", logged_in_bro.bro_name + ' has left the room.', room=room)


socks.on_namespace(NamespaceMessage('/api/v1.0/sock/message'))

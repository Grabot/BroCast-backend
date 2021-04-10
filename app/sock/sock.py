from flask_socketio import Namespace
from flask_socketio import join_room
from flask_socketio import leave_room
from flask_socketio import emit

from app import socks
from app.models.bro import get_a_room_you_two
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
        print("message event read!!!!")
        bro_id = data["bro_id"]
        bros_bro_id = data["bros_bro_id"]
        room = get_a_room_you_two(bro_id, bros_bro_id)
        update_read_time(bro_id, bros_bro_id, room)


socks.on_namespace(NamespaceSock('/api/v1.0/sock'))

from flask_socketio import emit


def update_broups(broup_objects):
    for broup in broup_objects:
        if not broup.has_left() and not broup.is_removed():
            bro_room = "room_%s" % broup.bro_id
            emit("message_event_chat_changed", broup.serialize, room=bro_room)


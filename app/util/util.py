from flask_socketio import emit


def update_broups(broup_objects):
    for broup in broup_objects:
        if not broup.has_left() and not broup.is_removed():
            bro_room = "room_%s" % broup.bro_id
            emit("message_event_chat_changed", broup.serialize, room=bro_room)


def remove_last_occur(old_string, bromotion):
    length = len(old_string)

    for i in range(length-1, 0, -1):
        if old_string[i] == bromotion:
            new_string = old_string[0:i] + old_string[i + 1:length]
            return new_string
    return old_string


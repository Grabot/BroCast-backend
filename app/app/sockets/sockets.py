import socketio

from app.config.config import settings

mgr = socketio.AsyncRedisManager(settings.REDIS_URI)
sio = socketio.AsyncServer(async_mode="asgi", client_manager=mgr, cors_allowed_origins="*")
sio_app = socketio.ASGIApp(socketio_server=sio, socketio_path="/socket.io")


@sio.on("connect")
async def handle_connect(sid, *args, **kwargs):
    print(f"Received connect: {sid}")
    # await sio.emit('lobby', 'User joined')


@sio.on("disconnect")
async def handle_disconnect(sid, *args, **kwargs):
    print(f"Received disconnect: {sid}")
    # await sio.emit('lobby', 'User joined')


@sio.on("message_event")
async def handle_message_event(sid, *args, **kwargs):
    print(f"Received message_event: {sid}")


@sio.on("join")
async def handle_join(sid, *args, **kwargs):
    data = args[0]
    user_id = data["user_id"]
    if user_id != -1:
        room = "room_%s" % user_id
        await sio.enter_room(sid, room)
        await sio.emit(
            "message_event",
            "User has entered room %s" % room,
            room=room,
        )


@sio.on("leave")
async def handle_leave(sid, *args, **kwargs):
    data = args[0]
    user_id = data["user_id"]
    if user_id != -1:
        room = "room_%s" % user_id
        await sio.leave_room(sid, room)
        await sio.emit(
            "message_event",
            "User has left room %s" % room,
            room=sid,
        )

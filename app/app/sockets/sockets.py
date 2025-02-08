import socketio

from app.config.config import settings

mgr = socketio.AsyncRedisManager(settings.REDIS_URI)
sio = socketio.AsyncServer(async_mode="asgi", client_manager=mgr, cors_allowed_origins="*")
sio_app = socketio.ASGIApp(socketio_server=sio, socketio_path="/socket.io")


@sio.on("connect")
async def handle_connect(sid, *args, **kwargs):
    print(f"Received connect: {sid}")
    # await sio.emit('lobby', 'Bro joined')


@sio.on("disconnect")
async def handle_disconnect(sid, *args, **kwargs):
    print(f"Received disconnect: {sid}")
    # await sio.emit('lobby', 'Bro joined')


@sio.on("message_event")
async def handle_message_event(sid, *args, **kwargs):
    print(f"Received message_event: {sid}")


@sio.on("join_solo")
async def handle_join_solo(sid, *args, **kwargs):
    data = args[0]
    bro_id = data["bro_id"]
    room = "room_%s" % bro_id
    await sio.enter_room(sid, room)

@sio.on("join_broup")
async def handle_join_broup(sid, *args, **kwargs):
    data = args[0]
    broup_id = data["broup_id"]
    room = "broup_%s" % broup_id
    await sio.enter_room(sid, room)

@sio.on("leave_solo")
async def handle_leave(sid, *args, **kwargs):
    data = args[0]
    bro_id = data["bro_id"]
    room = "room_%s" % bro_id
    await sio.leave_room(sid, room)

@sio.on("leave_broup")
async def handle_leave_broup(sid, *args, **kwargs):
    data = args[0]
    broup_id = data["broup_id"]
    room = "broup_%s" % broup_id
    await sio.leave_room(sid, room)

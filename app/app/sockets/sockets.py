from typing import Any, Dict
import socketio
from app.config.config import settings
from redis import asyncio as aioredis

mgr = socketio.AsyncRedisManager(settings.REDIS_URI)
sio = socketio.AsyncServer(async_mode="asgi", client_manager=mgr, cors_allowed_origins="*")
sio_app = socketio.ASGIApp(socketio_server=sio, socketio_path="/socket.io")

redis = aioredis.from_url(settings.REDIS_URI)

@sio.on("connect")
async def handle_connect(sid, *args, **kwargs):
    pass


@sio.on("disconnect")
async def handle_disconnect(sid, *args, **kwargs):
    pass


@sio.on("message_event")
async def handle_message_event(sid, *args, **kwargs):
    pass


@sio.on("join_solo")
async def handle_join_solo(sid, *args, **kwargs):
    data = args[0]
    bro_id = data["bro_id"]
    room = f"room_{bro_id}"
    await sio.enter_room(sid, room)


@sio.on("join_broup")
async def handle_join_broup(sid, *args, **kwargs):
    data = args[0]
    broup_id = data["broup_id"]
    room = f"broup_{broup_id}"
    await sio.enter_room(sid, room)


@sio.on("leave_solo")
async def handle_leave(sid, *args, **kwargs):
    data = args[0]
    bro_id = data["bro_id"]
    room = f"room_{bro_id}"
    await sio.leave_room(sid, room)


@sio.on("leave_broup")
async def handle_leave_broup(sid, *args, **kwargs):
    data = args[0]
    broup_id = data["broup_id"]
    room = f"broup_{broup_id}"
    await sio.leave_room(sid, room)


@sio.on("update_location")
async def handle_update_location(sid, data: Dict[str, Any]):
    print("handle update sharing")
    bro_id = data["bro_id"]
    lat = data["lat"]
    lng = data["lng"]
    broup_id = data["broup_id"]
    broup_room = f"broup_{broup_id}"

    print(f"bro:{bro_id}:location  {broup_room}")
    # Update value in Redis (but leave the expiration date which is set when the message is sent)
    await redis.set(f"bro:{bro_id}:broup:{broup_id}:location", f"{lat},{lng}", xx=True, keepttl=True)

    await sio.emit(
        "location_updated",
        {
            "bro_id": bro_id,
            "lat": lat,
            "lng": lng
        },
        room=broup_room
    )

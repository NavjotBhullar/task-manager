import threading
import json
import asyncio
from app.db.redis import redis_client
from app.services.websocket_manager import manager


def start_redis_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("chat")

    def listen():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    user_id = data["receiver"]

                    loop.run_until_complete(
                        manager.send_personal_message(user_id, data)
                    )
                except Exception as e:
                    print("Redis Error:", e)

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()

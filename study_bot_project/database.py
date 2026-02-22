import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.study_bot_db
history_collection = db.chat_history

async def save_chat(user_id, message, response):
    await history_collection.insert_one({
        "user_id": user_id,
        "user_message": message,
        "bot_response": response
    })

async def get_chat_history(user_id):
    cursor = history_collection.find({"user_id": user_id}).limit(10)
    history = await cursor.to_list(length=10)
    return history
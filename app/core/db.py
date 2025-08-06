from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

class Database:
    client: AsyncIOMotorClient = None
    
async def connect_to_mongo():
    Database.client = AsyncIOMotorClient(settings.MONGODB_URL)
    print("Connected to MongoDB!")

async def close_mongo_connection():
    if Database.client:
        Database.client.close()
        print("Disconnected from MongoDB!")

def get_database():
    return Database.client[settings.DATABASE_NAME] 
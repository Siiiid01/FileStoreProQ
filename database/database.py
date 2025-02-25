import motor, asyncio
import motor.motor_asyncio
from config import DB_URI, DB_NAME, COLLECTION_NAME
from pymongo import IndexModel, ASCENDING
from datetime import datetime

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database[COLLECTION_NAME]
banned_collection = database['banned_users']
telegraph_collection = database['telegraph_logs']

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        }
    }

async def present_user(user_id: int):
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user = new_user(user_id)
    await user_data.insert_one(user)
    return

async def db_verify_status(user_id):
    user = await user_data.find_one({'_id': user_id})
    if user:
        return user.get('verify_status', default_verify)
    return default_verify

async def db_update_verify_status(user_id, verify):
    await user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})

async def full_userbase():
    user_docs = user_data.find()
    user_ids = [doc['_id'] async for doc in user_docs]
    return user_ids

async def del_user(user_id: int):
    await user_data.delete_one({'_id': user_id})
    return

async def setup_indexes(collection):
    """Setup database indexes for better performance"""
    indexes = [
        IndexModel([("user_id", ASCENDING)], unique=True),
        IndexModel([("join_date", ASCENDING)]),
        IndexModel([("last_active", ASCENDING)])
    ]
    await collection.create_indexes(indexes)

async def add_banned_user(user_id: int, banned_by: int, reason: str = None):
    """Add a user to banned users collection with timestamp"""
    ban_time = datetime.now()
    ban_data = {
        'user_id': user_id,
        'banned_by': banned_by,
        'ban_reason': reason,
        'banned_on': ban_time
    }
    await banned_collection.update_one(
        {'user_id': user_id}, 
        {'$set': ban_data},
        upsert=True
    )
    return ban_time

async def remove_banned_user(user_id: int, unbanned_by: int):
    """Remove a user from banned users with unban logging"""
    ban_data = await get_ban_status(user_id)
    if ban_data:
        unban_log = {
            'user_id': user_id,
            'unbanned_by': unbanned_by,
            'unbanned_on': datetime.now(),
            'original_ban': ban_data
        }
        await database['unban_logs'].insert_one(unban_log)
    await banned_collection.delete_one({'user_id': user_id})

async def get_ban_status(user_id: int):
    """Get user ban status and info"""
    user = await banned_collection.find_one({'user_id': user_id})
    return user

async def log_telegraph_upload(
    user_id: int,
    file_name: str,
    file_type: str,
    telegraph_url: str,
    upload_date: datetime = None
):
    """Log a Telegraph file upload"""
    log_data = {
        'user_id': user_id,
        'file_name': file_name,
        'file_type': file_type,
        'telegraph_url': telegraph_url,
        'upload_date': upload_date or datetime.now()
    }
    result = await telegraph_collection.insert_one(log_data)
    return result.inserted_id

async def get_user_telegraph_uploads(user_id: int):
    """Get all Telegraph uploads by a user"""
    cursor = telegraph_collection.find({'user_id': user_id})
    return [doc async for doc in cursor]

async def db_check_ban(user_id: int) -> bool:
    """Check if a user is banned"""
    try:
        user = await banned_collection.find_one({'user_id': user_id})
        # If user exists in banned collection, they're banned
        return bool(user)
    except Exception as e:
        print(f"Ban check error: {e}")
        # On any error, treat as banned for safety
        return True

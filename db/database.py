from settings import db_connection, COLLECTION_ACCOUNTS, COLLECTION_MESSAGES

import pymongo


async def create_account(phone: str, tg_id: int, proxy: dict) -> int:
    col = db_connection[COLLECTION_ACCOUNTS]
    last_acc = await col.find_one({}, sort=[('account_id', pymongo.DESCENDING)])
    if last_acc:
        acc_id = last_acc['account_id'] + 1
    else:
        acc_id = 1
    await col.insert_one(
        {
            'account_id': acc_id,
            'tg_id': tg_id,
            'phone': phone,
            'proxy': proxy,
            'users': []
        }
    )
    return acc_id


async def get_all_accounts():
    col = db_connection[COLLECTION_ACCOUNTS]
    return await col.find({}).to_list(9999)


async def get_account_by_id(acc_id):
    col = db_connection[COLLECTION_ACCOUNTS]
    return await col.find_one({'account_id': int(acc_id)})


async def get_account_by_phone(phone):
    col = db_connection[COLLECTION_ACCOUNTS]
    return await col.find_one({'phone': phone})


async def get_account_by_tg_id(tg_id):
    col = db_connection[COLLECTION_ACCOUNTS]
    return await col.find_one({'tg_id': tg_id})


async def create_message(account_id: int, message_id: int, delay:int, message: dict):
    col = db_connection[COLLECTION_MESSAGES]
    await col.delete_one(
        {
            'account_id': account_id,
            'message_id': message_id,
        }
    )
    await col.insert_one(
        {
            'account_id': account_id,
            'message_id': message_id,
            'delay': delay,
            'message': message
        }
    )


async def get_account_messages(account_id):
    col = db_connection[COLLECTION_MESSAGES]
    res = await col.find({'account_id': account_id}).to_list(9999) 
    return sorted(res, key=lambda d: d['message_id'])


async def add_user_to_account(account_id, user_id):
    col = db_connection[COLLECTION_ACCOUNTS]
    await col.find_one_and_update(
        {'account_id': account_id}, {"$push": {"users": user_id}}
    )
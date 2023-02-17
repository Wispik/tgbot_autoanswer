import asyncio
from pathlib import Path

from pyrogram import Client, idle
from pyrogram.handlers import MessageHandler
from pyrogram.types import InputMediaPhoto
from pyrogram.enums import ParseMode

import db.database as db
import settings


async def __handler(client, message):
    me = await client.get_me()
    acc = await db.get_account_by_tg_id(me.id)
    messages = await db.get_account_messages(acc['account_id'])
    if message.from_user.id in acc['users']:
        return
    await db.add_user_to_account(acc['account_id'], message.from_user.id)
    count_chat_history = 0
    async for _ in client.get_chat_history(chat_id=message.from_user.id, limit=2):
        count_chat_history += 1
    if count_chat_history > 1:
        return
    for msg in messages:
        await asyncio.sleep(msg['delay'])
            
        _text = msg['message']['text'] if msg['message']['text'] else None

        if msg['message']['video_note_id']:
            file = Path(settings.DOWNLOAD_PATH, msg['message']['video_note_id'])
            await client.send_video_note(message.from_user.id, file)
        elif msg['message']['voice_id']:
            file = Path(settings.DOWNLOAD_PATH, msg['message']['voice_id'])
            await client.send_voice(message.from_user.id, file)
        elif msg['message']['video_id']:
            file = Path(settings.DOWNLOAD_PATH, msg['message']['video_id'])
            await client.send_video(message.from_user.id, file, caption=_text)
        elif msg['message']['animation_id']:
            file = Path(settings.DOWNLOAD_PATH, msg['message']['animation_id'])
            await client.send_animation(message.from_user.id, file, caption=_text)
        elif msg['message']['photos']:
            if len(msg['message']['photos']) == 1:
                file = Path(settings.DOWNLOAD_PATH, msg['message']['photos'][0])
                await client.send_photo(message.from_user.id, photo=file, caption=_text)
            else:
                mg = []
                for i, _p in enumerate(msg['message']['photos']):
                    if i == 0 and msg['message']['text']:
                        file = Path(settings.DOWNLOAD_PATH, _p)
                        mg.append(InputMediaPhoto(file, caption=_text))
                    else:
                        file = Path(settings.DOWNLOAD_PATH, _p)
                        mg.append(InputMediaPhoto(file))
                await client.send_media_group(message.from_user.id, mg)
        else:
            await client.send_message(message.from_user.id, msg['message']['text'])


async def run(phone):

    acc = await db.get_account_by_phone(phone)

    app = Client(
        f'client_{phone}',
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        app_version=settings.APP_VERSION,
        device_model=settings.DEVICE_MODEL,
        system_version=settings.SYSTEM_VERSION,
        lang_code=settings.LANG_CODE,
        proxy=acc['proxy'],
        workdir=settings.PYROGRAM_SESSION_PATH
    )
    app.set_parse_mode(ParseMode.HTML)
    app.add_handler(MessageHandler(__handler))

    await app.start()
    await idle()
    await app.stop()


async def run_tg_client(phone):
    loop = asyncio.get_event_loop()
    loop.create_task(run(phone))


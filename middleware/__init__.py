import asyncio

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler

import db.database as db


class UserIsAdminMiddleware(BaseMiddleware):
    '''
    Проверяем, админ ли юзер
    '''

    def __init__(self):
        super(UserIsAdminMiddleware, self).__init__()
    
    async def on_process_message(self, message: types.Message, data: dict):
        data['is_admin'] = False
        admin = await db.get_admin_by_tg_id(message.from_user.id)
        if admin:
            data['is_admin'] = True
        return


class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency = 0.6):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            if message.photo or message.animation or message.video or message.video_note:
                data["album"] = [message]
            return
        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]

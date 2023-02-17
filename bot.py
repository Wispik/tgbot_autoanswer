from aiogram.utils import executor

from handlers import setup_handlers
from settings import dp
import middleware
import tgclient
import db.database as db


def on_startup():
    setup_handlers(dp)


async def start_tgclients(_):
    accs = await db.get_all_accounts()
    for acc in accs:
        await tgclient.run_tg_client(acc['phone'])


if __name__ == '__main__':
    on_startup()
    dp.middleware.setup(middleware.UserIsAdminMiddleware())
    dp.middleware.setup(middleware.AlbumMiddleware())

    executor.start_polling(dp, on_startup=start_tgclients)

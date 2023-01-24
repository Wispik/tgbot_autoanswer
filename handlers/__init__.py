from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text

import handlers.user as h

from states import AppState


def setup_handlers(dp: Dispatcher):
    dp.register_message_handler(h.start_command, commands=['start'], state='*')
    dp.register_message_handler(h.add_account_step1_command, Text('Подключить аккаунт'))
    dp.register_message_handler(h.add_account_step2_command, state=[AppState.STATE_WAIT_PROXY], regexp=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+:[^:]+:[^:]+")
    dp.register_message_handler(h.add_account_step3_command, state=[AppState.STATE_WAIT_PHONE], regexp=r"\d+")
    dp.register_message_handler(h.add_account_step4_command, state=[AppState.STATE_WAIT_AUTH_CODE])
    dp.register_message_handler(h.add_account_step5_command, state=[AppState.STATE_WAIT_2FA])

    dp.register_message_handler(h.add_message_step1_command, Text('Добавить сообщение'))
    dp.register_message_handler(h.add_message_step2_command, state=[AppState.STATE_WAIT_ACCOUNT_ID], regexp=r"\d+")
    dp.register_message_handler(h.add_message_step3_command, state=[AppState.STATE_WAIT_MESSAGE_ID], regexp=r"\d+")
    dp.register_message_handler(h.add_message_step4_command, state=[AppState.STATE_WAIT_DELAY], regexp=r"\d+")
    dp.register_message_handler(h.add_message_step5_command, state=[AppState.STATE_WAIT_MESSAGE], content_types=['any'])

from aiogram.types import  InlineKeyboardButton, InlineKeyboardMarkup, \
                            ReplyKeyboardMarkup, KeyboardButton


kb_main = ReplyKeyboardMarkup(resize_keyboard=True)
kb_main.add(KeyboardButton('Подключить аккаунт'))
kb_main.add(KeyboardButton('Добавить сообщение'))


def kb_message(buttons):
    kb = InlineKeyboardMarkup(row_width=1)
    
    for btn in buttons:
        kb.add(
            InlineKeyboardButton(btn['text'], url=btn['url'])
        )

    return kb

from aiogram.utils.helper import Helper, HelperMode, Item


class AppState(Helper):
    mode = HelperMode.snake_case

    STATE_WAIT_PROXY = Item()
    STATE_WAIT_PHONE = Item()
    STATE_WAIT_AUTH_CODE = Item()
    STATE_WAIT_2FA = Item()
    
    STATE_WAIT_ACCOUNT_ID = Item()
    STATE_WAIT_MESSAGE_ID = Item()
    STATE_WAIT_DELAY = Item()
    STATE_WAIT_MESSAGE = Item()


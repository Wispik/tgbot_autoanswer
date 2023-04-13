from typing import List, Optional

from aiogram import types
from aiogram.dispatcher import FSMContext

from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded

import db.database as db
from states import AppState
import settings
import keyboards as kb

from tgclient import run_tg_client
from utils import download_file


clients_dicts = {}


async def start_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    await state.reset_data()
    await state.reset_state()
    await message.answer('Выберите действие:', reply_markup=kb.kb_main)


async def add_account_step1_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    await state.set_state(AppState.STATE_WAIT_PROXY)
    await message.answer('Введите Proxy SOCKS5 в формате: ip:port:login:password.')


async def add_account_step2_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return

    _proxy_data = message.text.split(':')

    _proxy_dict = dict(
        scheme="socks5", 
        hostname=_proxy_data[0],
        port=int(_proxy_data[1]),
        username=_proxy_data[2],
        password=_proxy_data[3]
    )

    await state.set_data(
        {
            'proxy': _proxy_dict
        }
    )
    await state.set_state(AppState.STATE_WAIT_PHONE)
    await message.answer('Введите номер аккаунта.')


async def add_account_step3_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return

    state_data = await state.get_data()

    acc_in_db = await db.get_account_by_phone(message.text)
    if acc_in_db:
        await message.answer(f'Аккаунт с номером {message.text} - уже добавлен!')
        return


    try:
        client = Client(
            f'client_{message.text}',
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            app_version=settings.APP_VERSION,
            device_model=settings.DEVICE_MODEL,
            system_version=settings.SYSTEM_VERSION,
            lang_code=settings.LANG_CODE,
            proxy=state_data['proxy'],
            workdir=settings.PYROGRAM_SESSION_PATH
        )

        await client.connect()
        sCode = await client.send_code(message.text)

        await state.update_data(
            {
                'phone': message.text,
                'phone_hash_code': sCode.phone_code_hash
            }
        )
        await state.set_state(AppState.STATE_WAIT_AUTH_CODE)

        clients_dicts[message.from_id] = client

        await message.answer('Введите код для авторизации')
    except Exception as e:
        await message.answer('Ошибка авторизации аккаунта, проверьте данные и попробуйте ещё раз. Если все данные верны, а ошибка остается - свяжитесь с администратором')
        await message.answer(f'Ошибка: {e}')


async def add_account_step4_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return

    await state.update_data({'code': message.text})
    await state.set_state(AppState.STATE_WAIT_2FA)
    await message.answer('Введите пароль 2FA (Если пароль отсутствует введите 0)')


async def add_account_step5_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return

    try:
        state_date = await state.get_data()
        client = clients_dicts[message.from_id]
        try:
            print('BEFORE SING_IN')
            await client.sign_in(
                state_date['phone'],
                state_date['phone_hash_code'],
                state_date['code']
            )
            print('BEFORE_2FA')
        except SessionPasswordNeeded:
            await client.check_password(message.text)
            await client.sign_in(
                state_date['phone'],
                state_date['phone_hash_code'],
                state_date['code']
            )
        me = await client.get_me()
        try:
            await client.disconnect()
        except Exception:
            print('error disconnect')
        del clients_dicts[message.from_id]
        acc_id = await db.create_account(state_date['phone'], me.id, state_date['proxy'])
        await message.answer(f'Аккаунт {acc_id} успешно авторизован.')
        await run_tg_client(state_date['phone'])
        await state.reset_data()
        await state.reset_state()
    except Exception as e:
        await message.answer('Ошибка авторизации аккаунта, проверьте данные и попробуйте ещё раз. Если все данные верны, а ошибка остается - свяжитесь с администратором')
        await message.answer(f'Ошибка: {e}')


async def add_message_step1_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return

    await state.set_state(AppState.STATE_WAIT_ACCOUNT_ID)
    await message.answer('Введите ID аккаунта для добавления/редактирования сообщения.')


async def add_message_step2_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return

    acc = await db.get_account_by_id(message.text)
    if acc:
        await state.set_state(AppState.STATE_WAIT_MESSAGE_ID)
        await state.set_data({'account_id': message.text})
        await message.answer('Введите ID сообщения')
    else:
        await message.answer(f'Аккаунт (id={message.text}) - не найден!')


async def add_message_step3_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return

    await state.set_state(AppState.STATE_WAIT_DELAY)
    await state.update_data({'message_id': message.text})
    await message.answer('Введите задержку перед отправкой в секундах')


async def add_message_step4_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return

    await state.set_state(AppState.STATE_WAIT_MESSAGE)
    await state.update_data({'delay': int(message.text)})
    await message.answer('Введите сообщение')


async def add_message_step5_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool,
    album: Optional[List[types.Message]] = None
):
    if not is_admin:
        return

    data = {
        'text': '',
        'photos': [],
        'video_id': None,
        'video_note_id': None,
        'animation_id': None,
        'voice_id': None,
        'voice_duration': 0
    }
    try:
        data['text'] = message.html_text
    except Exception:
        pass
    if album:
        data['photos'] = [f'{p.photo[-1].file_id}.jpg' for p in album if p.photo]
        if len(data['photos']) == 0 and len(album) == 1:
            if album[0].content_type == 'animation':
                data['animation_id'] = album[0].animation.file_id
                await download_file(data['animation_id'])
            elif album[0].content_type == 'video':
                data['video_id'] = album[0].video.file_id
                await download_file(data['video_id'])
            elif album[0].content_type == 'video_note':
                data['video_note_id'] = album[0].video_note.file_id
                await download_file(data['video_note_id'])
            elif album[0].content_type == 'voice':
                data['voice_id'] = album[0].voice.file_id
                data['voice_duration'] = album[0].voice.duration
                await download_file(data['voice_id'])
        if len(data['photos']) > 0:
            for _photo in data['photos']:
                await download_file(_photo)
    elif message.video:
        data['video_id'] = message.video.file_id
        await download_file(data['video_id'])
    elif message.video_note:
        data['video_note_id'] = message.video_note.file_id
        await download_file(data['video_note_id'])
    elif message.animation:
        data['animation'] = message.animation.file_id
        await download_file(data['animation'])
    elif message.voice:
        data['voice_id'] = message.voice.file_id
        data['voice_duration'] = message.voice.duration
        await download_file(data['voice_id'])
    await state.update_data({'data': data})
    
    state_data = await state.get_data()

    await db.create_message(
        account_id=int(state_data['account_id']),
        delay=int(state_data['delay']),
        message_id=int(state_data['message_id']),
        message=state_data['data']
    )
    await state.reset_data()
    await state.reset_state()

    await message.answer(f"Сообщение {state_data['message_id']} успешно добавлено")


        

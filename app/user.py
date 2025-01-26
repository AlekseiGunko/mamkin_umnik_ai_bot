from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy import String

import app.keyboards as kb
from app.states import Chat, Image
from app.generators import gpt_text, gpt_image, gpt_vision

from app.database.requests import set_user, get_user, calculate

from decimal import Decimal

import uuid
import os

user_r = Router()

@user_r.message(F.text == 'Отмена')
@user_r.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    await message.answer('Добро пожаловать в AI-бот', reply_markup=kb.main)
    await state.clear()


@user_r.message(F.text == 'Чат')
async def chatting(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        await state.set_state(Chat.text)
        await message.answer('Введите Ваш запрос:', reply_markup=kb.cancel)
    else:
        await message.answer('Недостаточно средств на балансе.')

@user_r.message(Chat.text, F.photo)
async def chat_response(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        await state.set_state(Chat.wait)
        file = await message.bot.get_file(message.photo[-1].file_id)
        file_path = file.file_path
        file_name = uuid.uuid4()
        await message.bot.download_file(file_path, f'{file_name}.jpeg')
        response = await gpt_vision(message.caption, 'gpt-4o', f'{file_name}.jpeg')
        await calculate(message.from_user.id, response['usage'], 'gpt-4o', user)
        await message.answer(response['response'])
        await state.set_state(Chat.text)
        os.remove(f'{file_name}.jpeg')
    else:
        await message.answer('Недостаточно средств на балансе.')

@user_r.message(Chat.text)
async def chat_response(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        await state.set_state(Chat.wait)
        response = await gpt_text(message.text, 'gpt-4o')
        await calculate(message.from_user.id, response['usage'], 'gpt-4o', user)
        await message.answer(response['response'])
        await state.set_state(Chat.text)
    else:
        await message.answer('Недостаточно средств на балансе.')

@user_r.message(Image.wait)
@user_r.message(Chat.wait)
async def wait_wait(message: Message):
    await message.answer('Ваше сообщение генерируется, пожалуйста подождите')


@user_r.message(F.text == 'Генерация картинок')
async def chatting_image(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        await state.set_state(Image.text)
        await message.answer('Введите Ваше описание картинки:', reply_markup=kb.cancel)
    else:
        await message.answer('Недостаточно средств на балансе.')


@user_r.message(Image.text)
async def chat_response_image(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        await state.set_state(Image.wait)
        response = await gpt_image(message.text, 'dall-e-3')
        await calculate(message.from_user.id, response['usage'], 'dall-e-3', user)
        try:
            await message.answer_photo(photo=response['response'])
        except Exception as e:
            print(e)
            await message.answer(response['response'])
        await state.set_state(Image.text)
    else:
        await message.answer('Недостаточно средств на балансе.')


#@user_r.message(Chat.text, F.photo)
#async def chat_response(message: Message, state: FSMContext):
#    user = await get_user(message.from_user.id)
#    if Decimal(user.balance) > 0:
#        await state.set_state(Chat.wait)
#        file = await message.bot.get_file(message.photo[-1].file_id)
#        file_path = file.file_path
#        file_name = uuid.uuid4()
#        await message.bot.download_file(file_path, f'{file_name}.jpeg')
#        response = await gpt_vision(message.caption, 'gpt-4o', f'{file_name}.jpeg')
#        await calculate(message.from_user.id, response['usage'], 'gpt-4o', user)
#        await message.answer(response['response'])
#        await state.set_state(Chat.text)
#        os.remove(f'{file_name}.jpeg')
#    else:
#        await message.answer('Недостаточно средств на балансе.')
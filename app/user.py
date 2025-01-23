from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.states import Chat
from app.generators import gpt_text

user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать в AI-бот', reply_markup=kb.main)


@user.message(F.text == 'Чат')
async def chatting(message: Message, state: FSMContext):
    await state.set_state(Chat.text)
    await message.answer('Введите Ваш запрос:')


@user.message(Chat.text)
async def chat_response(message: Message, state: FSMContext):
    await state.set_state(Chat.wait)
    response = await gpt_text(message.text, 'gpt-4o')
    await message.answer(response)
    await state.clear()


@user.message(Chat.wait)
async def wait_wait(message: Message):
    await message.answer('Ваше сообщение генерируется, пожалуйста подождите')

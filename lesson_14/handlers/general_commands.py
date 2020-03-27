from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

# Если запускаете код отдельно от этого репозитория, то закомментируйте следующую строку:
from lesson_14.misc import dp
# ... и замените её на:
# from misc import dp


@dp.message_handler(commands="cancel", state="*")
@dp.message_handler(Text(equals="отмена", ignore_case=True), state="*")
async def cmd_cancel(message: types.Message, state: FSMContext):  # обратите внимание на второй аргумент
    # Сбрасываем текущее состояние пользователя и сохранённые о нём данные
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['start'], state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await message.reply("Выберите, что хотите заказать: "
                        "напитки (/drinks) или блюда (/food).", reply_markup=types.ReplyKeyboardRemove())

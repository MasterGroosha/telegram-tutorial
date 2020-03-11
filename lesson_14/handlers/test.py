from aiogram import types
from lesson_14.misc import dp


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Start")


@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await message.reply("Help")
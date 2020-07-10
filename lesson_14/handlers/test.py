from aiogram import types
from lesson_14.misc import dp


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def all_other_messages(message: types.Message):
    await message.reply("Любое другое сообщение")

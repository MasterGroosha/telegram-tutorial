from aiogram import types

# Если запускаете код отдельно от этого репозитория, то закомментируйте следующую строку:
from lesson_14.misc import dp
# ... и замените её на:
# from misc import dp


@dp.message_handler(content_types=types.ContentTypes.ANY, state="*")
async def all_other_messages(message: types.Message):
    if message.content_type == "text":
        await message.reply("Ничего не понимаю!")
    else:
        await message.reply("Этот бот принимает только текстовые сообщения!")

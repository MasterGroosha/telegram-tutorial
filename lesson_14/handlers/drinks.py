from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Если запускаете код отдельно от этого репозитория, то закомментируйте следующую строку:
from lesson_14.misc import dp
# ... и замените её на:
# from misc import dp

available_drinks_names = ["чай", "кофе", "какао"]
available_drinks_sizes = ["250 мл", "0.5л", "1л"]


class OrderDrinks(StatesGroup):
    waiting_for_drink_name = State()
    waiting_for_drink_size = State()


# Это самый первый хэндлер
@dp.message_handler(commands="drinks", state="*")
async def food_step_1(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_drinks_names:
        keyboard.add(name)
    await message.answer("Выберите напиток:", reply_markup=keyboard)
    await OrderDrinks.waiting_for_drink_name.set()


@dp.message_handler(state=OrderDrinks.waiting_for_drink_name, content_types=types.ContentTypes.TEXT)
async def food_step_2(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_drinks_names:
        await message.reply("Пожалуйста, выберите напиток, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_food=message.text.lower())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in available_drinks_sizes:
        keyboard.add(size)
    await OrderDrinks.next()  # для простых шагов можно не указывать название состояния, обходясь next()
    await message.answer("Теперь выберите размер порции:", reply_markup=keyboard)


@dp.message_handler(state=OrderDrinks.waiting_for_drink_size, content_types=types.ContentTypes.TEXT)
async def food_step_3(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_drinks_sizes:
        await message.reply("Пожалуйста, выберите размер порции, используя клавиатуру ниже.")
        return
    user_data = await state.get_data()
    await message.answer(f"Вы заказали {user_data['chosen_food']} объёмом {message.text.lower()}.\n"
                         f"Попробуйте теперь заказать еду: /food", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

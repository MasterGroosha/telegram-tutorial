#!venv/bin/python
from aiogram import executor

# Если запускаете код отдельно от этого репозитория, то закомментируйте эти две строки...
from lesson_14.misc import dp
import lesson_14.handlers
# ... и раскомментируйте эти
# from misc import dp
# import handlers


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

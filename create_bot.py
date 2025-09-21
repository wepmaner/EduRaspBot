from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import *

bot = Bot(token=token_1)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

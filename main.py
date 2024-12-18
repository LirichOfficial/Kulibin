import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import data
import asyncio
import random


API_TOKEN = '8147906166:AAGL6vWBWvZPwUnUzRy0HC6hKwvl43TEBHs'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton("Статистика")
    markup.add(item1)

    await message.answer("Выберите действие", reply_markup=markup)


@dp.message_handler(lambda message: message.text == 'Статистика')
async def process_button1(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = KeyboardButton("Лучшие игроки")
    item3 = KeyboardButton("Текущее положение")
    markup.add(item2, item3)

#    user = data.get_user_data(message.from_user.username)
    user = {"points":"1200", "Rank":"Expert"}

    ans = message.from_user.username + ":\n" + "Очки: " + user["points"] + "\n" + "Звание: " + user["Rank"]

    await message.answer(ans, reply_markup=markup)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

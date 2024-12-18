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


@dp.message_handler(lambda message: message.text == 'В начало')
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton("Статистика")
    markup.add(item1)

    await message.answer("Выберите действие", reply_markup=markup)


@dp.message_handler(lambda message: message.text == 'Статистика')
async def process_stat(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = KeyboardButton("Лучшие игроки")
    item3 = KeyboardButton("Текущее положение")
    item4 = KeyboardButton("В начало")
    markup.add(item2, item3, item4)

#    user = data.get_user_data(message.from_user.username)
    user = {"points":"1200", "Rank":"Expert"}

    ans = message.from_user.username + ":\n" + "Очки: " + user["points"] + "\n" + "Звание: " + user["Rank"]

    await message.answer(ans, reply_markup=markup)



@dp.message_handler(lambda message: message.text == 'Лучшие игроки')
async def process_top10(message: types.Message):
    #top = data.get_global_stats()
    top = {"livoo":"1200", "amirkhan":"1175", "lenya":"1100"}

    ans = ""
    cnt = 0
    
    for i in top.items():
        cnt = cnt + 1
        if (i[0] == message.from_user.username):
            ans = ans + "\n->" + str(cnt) + ". " + i[1] + " - " + i[0] + "<-"
        else:
            ans = ans + "\n" + str(cnt) + ". " + i[1] + " - " + i[0]
    await message.answer(ans)


@dp.message_handler(lambda message: message.text == 'Текущее положение')
async def process_top10(message: types.Message):
    #top = data.get_global_stats()
    top = {"livoo":"1200", "amirkhan":"1175", "lenya":"1100", "deelovaya_kolbasa":"1000"}

    ans = ""
    cnt = 0

    for i in top.items():
        cnt = cnt + 1
        if (i[0] == message.from_user.username):
            ans = ans + "\n->" + str(cnt) + ". " + i[1] + " - " + i[0] + "<-"
        else:
            ans = ans + "\n" + str(cnt) + ". " + i[1] + " - " + i[0]
    await message.answer(ans)




async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

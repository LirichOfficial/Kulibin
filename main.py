import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import data
import api
import asyncio
import random
import datetime


API_TOKEN = ''

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


user_data_lock = asyncio.Lock()
user_data = dict()
current_score = dict()
is_playing = dict()
current_word = dict()
current_topic = dict()

async def in_game(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) == 1:
        return True
    return False


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос")
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton("Статистика")
    item2 = KeyboardButton("Играть")
    markup.add(item1, item2)

    await message.answer("Здравствуй! Перед тобой Акинатор наоборот!\nДля того, чтобы начать игру, выбери тему, используя /q [тема], а затем нажми Играть. Тему можно изменить в любой момент через ту же команду.\nПосле начала игры задавать вопрос нужно без всяких команд. Ответ на вопрос должен быть да/нет/не знаю. Чтобы дать свой ответ, используй /ans [ответ]", reply_markup=markup)

@dp.message_handler(lambda message: message.text == 'В начало')
async def start(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос")
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton("Статистика")
    item2 = KeyboardButton("Играть")
    markup.add(item1, item2)

    await message.answer("Выберите действие", reply_markup=markup)



@dp.message_handler(lambda message: message.text == 'Статистика')
async def process_stat(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос")
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = KeyboardButton("Лучшие игроки")
    item3 = KeyboardButton("Текущее положение")
    item4 = KeyboardButton("В начало")
    markup.add(item2, item3, item4)

    user_data = data.get_user_data(user)
    #user = {"points":"1200", "Rank":"Expert"}

    ans = user + ":\n" + "Очки: " + str(user_data["points"]) + "\n"

    await message.answer(ans, reply_markup=markup)



@dp.message_handler(lambda message: message.text == 'Лучшие игроки')
async def process_top10(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос")
    top = data.get_global_stats()
    #top = {"livoo":"1200", "amirkhan":"1175", "lenya":"1100"}

    ans = ""
    cnt = 0
    
    for i in range(0, len(top)):
        cnt = cnt + 1
        if (top[i]['user'] == message.from_user.username):
            ans = ans + "\n->" + str(cnt) + ". " + top[i]['user'] + " - " + str(top[i]['points']) + "<-"
        else:
            ans = ans + "\n" + str(cnt) + ". " + top[i]['user'] + " - " + str(top[i]['points'])
    await message.answer(ans)


@dp.message_handler(lambda message: message.text == 'Текущее положение')
async def process_user_place(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос")
    top = data.get_user_place(message.from_user.username)
    #top = {"livoo":"1200", "amirkhan":"1175", "lenya":"1100", "deelovaya_kolbasa":"1000"}

    ans = ""
    cnt = 0

    for i in range(0, len(top)):
        cnt = cnt + 1
        if (top[i]['user'] == message.from_user.username):
            ans = ans + "\n->" + str(cnt) + ". " + top[i]['user'] + " - " + str(top[i]['points']) + "<-"
        else:
            ans = ans + "\n" + str(cnt) + ". " + top[i]['user'] + " - " + str(top[i]['points'])
    await message.answer(ans)





@dp.message_handler(lambda message: message.text == 'Играть')
async def start_game(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный вопрос")
        return
    if current_topic.get(user) is None:
        topic = 'Нет'
    else:
        topic = current_topic[user]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton("Начать игру")
    item2 = KeyboardButton("В начало")
    markup.add(item1, item2)
    await message.answer("Текущая тема - " + topic, reply_markup=markup)


@dp.message_handler(commands=['q'])
async def chanhe_topic(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный вопрос")
        return
    user = message.from_user.username
    current_topic[user] = message.text[3:]
    await message.answer("Вы выбрали тему - " + message.text[3:])


@dp.message_handler(lambda message: message.text == 'Начать игру')
async def game_started(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный вопрос")
        return
    if current_topic.get(user) is None:
        await message.answer("Тема не выбрана")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton("Сдаться")
    markup.add(item1)
    is_playing[user] = 1
    current_score[user] = 1024
    current_word[user] = api.get_word(current_topic[user])
    await message.answer("Игра начата!\nТекущая тема - " + current_topic[user] + "\n" + "Начальное количество очков: 1024", reply_markup=markup)


@dp.message_handler(commands=['ans'])
async def try_anwer(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) != 1:
        await message.answer("Некорректный вопрос")
        return
    ans = message.text[5:]
    user = message.from_user.username
    dt_now = str(datetime.datetime.today())
    if current_score[user] > 0:
        current_score[user] = current_score[user] // 2
    else:
        current_score[user] = current_score[user] - 10
    if api.is_equal(ans, current_word[user]) == True:
        data.add_new_game(user, current_score[user], dt_now, current_topic[user], current_word[user])
        is_playing[user] = 0
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = KeyboardButton("Начать игру")
        item2 = KeyboardButton("В начало")
        markup.add(item1, item2)
        await message.answer("Правильно!\nТы заработал: " + str(current_score[user]) + " очков", reply_markup=markup)
    else:
        await message.answer("А вот и нет! Поробуй еще раз")
    await message.answer("Текущее количество очков: " + str(current_score[user]))


@dp.message_handler(lambda message: message.text == 'Сдаться')
async def surrender(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) != 1:
        await message.answer("Некорректный вопрос")
        return
    current_score[user] = -100
    dt_now = str(datetime.datetime.today())
    data.add_new_game(user, current_score[user], dt_now, current_topic[user], current_word[user])
    is_playing[user] = 0
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton("Начать игру")
    item2 = KeyboardButton("В начало")
    markup.add(item1, item2)
    await message.answer("Уже сдаешься? Ну ты и слабак...", reply_markup=markup)

@dp.message_handler()
async def get_question(message: types.Message):
    user = message.from_user.username
    if is_playing.get(user) != 1:
        await message.answer("Некорректный вопрос")
        return
    ans = api.get_answer(current_word[user], message.text)
    if current_score[user] > 0:
        current_score[user] = current_score[user] // 2
    else:
        current_score[user] = current_score[user] - 10
    if ans == 0:
        ans = 'Нет'
    elif ans == 1:
        ans = 'Да'
    else:
        ans = 'Не знаю'
    await message.answer(ans)
    await message.answer("Текущее количество очков: " + str(current_score[user]))




async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    data.init()
    asyncio.run(main())

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import enums
import data
import api
import asyncio
import random
import datetime


API_TOKEN = '8147906166:AAGL6vWBWvZPwUnUzRy0HC6hKwvl43TEBHs'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


user_data_lock = asyncio.Lock()
user_data = dict()
current_score = dict()
is_playing = dict()
current_word = dict()
current_topic = dict()
answer_count = dict()
current_players = dict()

async def get_all_users_id(bot: Bot, chat_id: int):
    members = await bot.get_chat_members(chat_id)
    user_ids = [member.user.username for member in members if member.user.is_bot is False]
    return user_ids


@dp.message(Command('start'))
async def start(message: types.Message):
    user = str(message.chat.id)
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Статистика"),
                                         KeyboardButton(text="Играть")
                                     ],
                                 ])

    await message.answer("Здравствуй! Перед тобой Акинатор наоборот!\nДля того, чтобы начать игру, выбери тему, используя /q [тема], а затем нажми Играть. Тему можно изменить в любой момент через ту же команду.\nПосле начала игры задавать вопрос нужно без всяких команд. Ответ на вопрос должен быть да/нет/не знаю. Чтобы дать свой ответ, используй /ans [ответ]", reply_markup=markup)

@dp.message(lambda message: message.text == 'В начало')
async def start(message: types.Message):
    user = str(message.chat.id)
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Статистика"),
                                         KeyboardButton(text="Играть")
                                     ],
                                     ])

    await message.answer("Выберите действие", reply_markup=markup)

@dp.message(lambda message: message.text == 'Статистика')
async def start(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос")
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Лучшие игроки"),
                                         KeyboardButton(text="Текущее положение"),
                                         KeyboardButton(text="В начало")
                                     ],
                                 ])
    user_data = data.get_user_data(username)
    ans = username + ":\n" + "Очки: " + str(user_data["points"]) + "\n"

    await message.answer(ans, reply_markup=markup)



@dp.message(lambda message: message.text == 'Лучшие игроки')
async def process_top10(message: types.Message):
    user = str(message.chat.id)
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос")
    username = message.from_user.username
    top = data.get_global_stats()

    ans = ""
    cnt = 0

    print(username,"запросил глобальную статистику")
    for i in range(0, len(top)):
        cnt = cnt + 1
        if (top[i]['user'] == username):
            ans = ans + "\n->" + str(cnt) + ". " + top[i]['user'] + " - " + str(top[i]['points']) + "<-"
        else:
            ans = ans + "\n" + str(cnt) + ". " + top[i]['user'] + " - " + str(top[i]['points'])
    await message.answer(ans)


@dp.message(lambda message: message.text == 'Текущее положение')
async def process_user_place(message: types.Message):
    user = str(message.chat.id)
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос")
    username = message.from_user.username
    top = data.get_user_place(username)

    ans = ""
    print(username,"запросил свое место в статистике")
    for i in range(0, len(top)):
        if (top[i]['user'] == username):
            ans = ans + "\n->" + top[i]['position'] + ". " + top[i]['user'] + " - " + str(top[i]['points']) + "<-"
        else:
            ans = ans + "\n" + top[i]['position'] + ". " + top[i]['user'] + " - " + str(top[i]['points'])
    await message.answer(ans)





@dp.message(lambda message: message.text == 'Играть')
async def start_game(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный вопрос")
        return
    if current_topic.get(user) is None:
        await message.answer("Тема не выбрана")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Сдаться"),
                                     ],
                                 ])
    is_playing[user] = 1
    current_score[user] = 1000
    current_word[user] = api.get_word(current_topic[user])
    answer_count[user] = 1;
    if current_players.get(user) is None:
        current_players[user] = {}
    current_players[user][username] = 1
    print(username,"начал игру с темой",current_topic[user],"ответ:",current_word[user])
    await message.answer("Игра начата!\nТекущая тема - " + current_topic[user] + "\n" + "Начальное количество очков: 1000", reply_markup=markup)

@dp.message(Command('q'))
async def chanhe_topic(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный вопрос")
        return
    current_topic[user] = message.text[3:]
    print(username,"поменял тему на",current_topic[user])
    await message.answer("Вы выбрали тему - " + message.text[3:])



@dp.message(Command('ans'))
async def try_anwer(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if is_playing.get(user) != 1:
        await message.answer("Некорректный вопрос")
        return
    ans = message.text[5:]
    current_players[user][username] = 1
    dt_now = str(datetime.datetime.today())
    current_score[user] = 1000 // (answer_count[user] + 1)
    answer_count[user] = answer_count[user] + 1
    if api.is_equal(ans, current_word[user]) == True:

        data.add_new_game(username, current_score[user], dt_now, current_topic[user], current_word[user])
        is_playing[user] = 0
        current_players[user].clear()
        markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                     keyboard=[
                                         [
                                             KeyboardButton(text="Играть"),
                                             KeyboardButton(text="В начало"),
                                         ],
                                     ])

        await message.answer("Правильно!\nТы заработал: " + str(current_score[user]) + " очков", reply_markup=markup)
    else:
        await message.answer("А вот и нет! Поробуй еще раз")
    await message.answer("Текущее количество очков: " + str(current_score[user]))


@dp.message(lambda message: message.text == 'Сдаться')
async def surrender(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if is_playing.get(user) != 1:
        await message.answer("Некорректный вопрос")
        return
    current_score[user] = -100
    dt_now = str(datetime.datetime.today())
    current_players[user][username] = 1
    usernames = current_players[user]
    print(usernames)
    for i, j in usernames.items():
        data.add_new_game(i, current_score[user], dt_now, current_topic[user], current_word[user])
    is_playing[user] = 0
    current_players[user].clear()
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Играть"),
                                         KeyboardButton(text="В начало"),
                                     ],
                                 ])
    print(username, "сдался")
    retv="Уже сдаешься? Ну ты и слабак... Правильный ответ: " + current_word[user]+". Вы потеряли 100 очков"
    await message.answer(retv, reply_markup=markup)

@dp.message(Command('?'))
async def get_question(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if is_playing.get(user) != 1:
        await message.answer("Некорректный вопрос")
        return
    ans = api.get_answer(current_word[user], message.text[1:])
    current_score[user] = 1000 // (answer_count[user] + 1)
    answer_count[user] = answer_count[user] + 1
    current_players[user][username] = 1
    if ans == 0:
        ans = 'Нет'
    elif ans == 1:
        ans = 'Да'
    else:
        ans = 'Не знаю'

    print(username, "задал вопрос:", message.text[1:],"\n","ответ нейросети:", ans,'\n', "правильный ответ:", current_word[user])
    await message.answer(ans)
    await message.answer("Текущее количество очков: " + str(current_score[user]))




async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    data.init()
    asyncio.run(main())

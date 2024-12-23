import logging
from aiogram import types
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import InputFile, FSInputFile
import data
import api
import asyncio
import datetime

API_TOKEN = ''

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
current_history_q = dict()
current_history_ans = dict()
is_choosing_topic = dict()


@dp.message(Command('start'))
async def start(message: types.Message):
    user = str(message.chat.id)
    is_choosing_topic[user] = 0
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return
    username = message.from_user.username
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Играть"),
                                         KeyboardButton(text="Статистика"),
                                     ],
                                 ])
    print(username, "использовал команду /start")
    await message.answer(
        "Здравствуй! Перед тобой Акинатор наоборот! Не знаешь как играть? Используй команду /help",
        reply_markup=markup)


@dp.message(Command('help'))
async def chanhe_topic(message: types.Message):
    help_info = 'Как начать игру?\n1. Вернись в главное меню\n2. Нажми на кнопку играть\n3. Введи тему \n4. Игра начнется'
    help_info += '\n\n      Как Играть?\nПосле начала игры спрашивай свои вопросы текстом и получай на них ответ'
    help_info += ' вида да/нет/не знаю. Если ты считаешь, что угадал слово, введи его при помощи команды /ans'
    help_info += ' если не можешь отгадать слово, то всегда можно сдаться. После игры можно узнать пояснения на ответы'
    help_info += '\n      ВАЖНО! Если бот используется в группе, то вопросы задаются командой /?, а тема - командой /topic'
    help_info += '\n\nЗа проигрыш снимается 100 баллов, за выигрыш начисляется 1000/x баллов, где x - число вопросов'
    username = message.from_user.username
    user = message.chat.id
    is_choosing_topic[user] = 0
    print(username, "запросил помощь")
    await message.answer(help_info)


@dp.message(lambda message: message.text == 'В начало')
async def start(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Играть"),
                                         KeyboardButton(text="Статистика"),
                                     ],
                                 ])
    print(username, "вернулся в главное меню")
    await message.answer("Выберите действие", reply_markup=markup)


@dp.message(lambda message: message.text == 'Статистика')
async def start(message: types.Message):
    user = str(message.chat.id)
    is_choosing_topic[user] = 0
    username = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Лучшие игроки"),
                                         KeyboardButton(text="Текущее положение"),
                                         KeyboardButton(text="В начало")
                                     ],
                                 ])
    user_data = data.get_user_data(username)
    data.get_plot_image(username)
    ans = username + ":\n" + "Очки: " + str(user_data["points"]) + "\n"

    await message.answer_photo(photo=FSInputFile(path='Plot.png'))
    await message.answer(ans, reply_markup=markup)


@dp.message(lambda message: message.text == 'Лучшие игроки')
async def process_top10(message: types.Message):
    user = str(message.chat.id)
    is_choosing_topic[user] = 0
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return
    username = message.from_user.username
    top = data.get_global_stats()

    ans = ""
    cnt = 0

    print(username, "запросил глобальную статистику")

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
    is_choosing_topic[user] = 0
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return
    username = message.from_user.username
    top = data.get_user_place(username)

    ans = ""

    print(username, "запросил свое место в статистике")
    for i in range(0, len(top)):
        if (top[i]['user'] == username):
            ans = ans + "\n->" + str(top[i]['position']) + ". " + top[i]['user'] + " - " + str(top[i]['points']) + "<-"
        else:
            ans = ans + "\n" + str(top[i]['position']) + ". " + top[i]['user'] + " - " + str(top[i]['points'])
    await message.answer(ans)


@dp.message(lambda message: message.text == 'Играть')
async def start_game(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="В начало"),
                                     ],
                                 ])
    current_score[user] = 1000
    is_choosing_topic[user] = 1
    await message.answer("Введи тему игры. (используй команду /topic, если играешь в группе)", reply_markip=markup)


@dp.message(Command('ans'))
async def try_anwer(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if is_playing.get(user) != 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return
    ans = message.text[5:]
    current_players[user][username] = 1
    dt_now = str(datetime.datetime.today())
    if await api.is_equal(ans, current_word[user]) == True:
        current_score[user] = 1000 // (answer_count[user])
        data.add_new_game(username, current_score[user], dt_now, current_topic[user], current_word[user])
        is_playing[user] = 0
        current_players[user].clear()
        markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                     keyboard=[
                                         [
                                             KeyboardButton(text="Играть"),
                                             KeyboardButton(text="Статистика"),
                                             KeyboardButton(text="История игры"),
                                         ],
                                     ])

        print(username, "отгадал слово:", current_word[user], "\n", "с догадкой:", ans, "\n", "он получил",
              current_score[user], "очков")
        await message.answer("Правильно!\nТы заработал: " + str(current_score[user]) + " очков", reply_markup=markup)
    else:
        answer_count[user] = answer_count[user] + 1
        current_score[user] = 1000 // (answer_count[user])
        print(username, "не смог отгадать слово:", current_word[user], "\n", "с догадкой:", ans)
        await message.answer("А вот и нет! Поробуй еще раз")
    await message.answer("Текущее количество очков: " + str(current_score[user]))


@dp.message(lambda message: message.text == 'Сдаться')
async def surrender(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if is_playing.get(user) != 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return
    current_score[user] = -100
    dt_now = str(datetime.datetime.today())
    current_players[user][username] = 1
    usernames = current_players[user]
    for i, j in usernames.items():
        data.add_new_game(i, current_score[user], dt_now, current_topic[user], current_word[user])
    is_playing[user] = 0
    current_players[user].clear()
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Играть"),
                                         KeyboardButton(text="В начало"),
                                         KeyboardButton(text="История игры"),
                                     ],
                                 ])
    print(username, "сдался")
    retv = "Уже сдаешься? Ну ты и слабак... Правильный ответ: " + current_word[user] + ". Ты потерял 100 очков"
    await message.answer(retv, reply_markup=markup)


@dp.message(Command('?'))
async def get_question(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if is_playing.get(user) != 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return
    ans = await api.get_answer_comitet(current_word[user], message.text[3:])

    current_players[user][username] = 1
    if current_history_q.get(user) is None:
        current_history_q[user] = []
        current_history_ans[user] = []
    current_history_q[user].append(message.text[3:])
    current_history_ans[user].append(ans)
    print(username, "задал вопрос:", message.text[3:], "\n", "ответ нейросети:", ans, '\n', "правильный ответ:",
          current_word[user])
    cnt = 0
    if 'Да' in ans['pro'][0:5]:
        cnt = cnt + 1
    elif 'Нет' in ans['pro'][0:5]:
        cnt = cnt - 1
    if 'Да' in ans['lite'][0:5]:
        cnt = cnt + 1
    elif 'Нет' in ans['lite'][0:5]:
        cnt = cnt - 1
    if 'Да' in ans['lamma'][0:5]:
        cnt = cnt + 1
    elif 'Нет' in ans['lamma'][0:5]:
        cnt = cnt - 1
    if cnt == 3:
        ans = 'Да'
    elif cnt == 2:
        ans = 'Скорее всего да'
    elif cnt == 1:
        ans = 'Больше да, чем нет'
    elif cnt == 0:
        ans = 'Не знаю'
    elif cnt == -1:
        ans = 'Больше нет, чем да'
    elif cnt == -2:
        ans = 'Скорее всего нет'
    else:
        ans = 'Нет'
    await message.answer(ans)
    await message.answer("Текущее количество очков: " + str(current_score[user]))


@dp.message(lambda message: message.text == 'История игры')
async def history(message: types.Message):
    user = str(message.chat.id)
    is_choosing_topic[user] = 0
    if is_playing.get(user) == 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return
    await message.answer("История вопросов этой игры")

    print(current_history_q.get(user))
    if current_history_q.get(user) is None:
        sz = 0
    else:
        sz = len(current_history_q[user])
    for i in range(sz):
        num_of_q = str(i + 1)
        message.answer(
                num_of_q + ". Ваш вопрос: " + current_history_q[user] + "\n" +
                "Ответ Yandexgpt: " + current_history_ans[user]['pro'] + "\n" +
                "Ответ Yandexgpt-lite: " + current_history_ans[user]['lite'] + "\n" +
                "Ответ Lamma-lite: " + current_history_ans[user]['lamma']
                )
@dp.message(Command('topic'))
async def choose(message: types.Message):
    user = str(message.chat.id)
    if is_choosing_topic.get(user) != 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return
    if len(message.text.split()) == 1:
        await message.answer("Тема не может быть пустой")
        return
    if current_history_q.get(user) is not None:
        current_history_q[user].clear()
        current_history_ans[user].clear()


    current_topic[user] = message.text[7:]
    word = await api.get_word(current_topic[user])
    if word is None:
        await message.answer("Твоя тема не подходит по причине малого числа возможных загадываемых слов")
        return
    current_word[user] = word

    username = message.from_user.username
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Сдаться"),
                                     ],
                                 ])
    is_playing[user] = 1
    is_choosing_topic[user] = 0
    current_score[user] = 1000
    answer_count[user] = 1
    if current_players.get(user) is None:
        current_players[user] = {}
    current_players[user][username] = 1
    print(username, "начал игру с темой", current_topic[user], "ответ:", current_word[user])
    await message.answer(
        "Игра начата!\nТекущая тема - " + current_topic[user] + "\n" + "Начальное количество очков: 1000",
        reply_markup=markup)


async def choose1(message: types.Message):
    user = str(message.chat.id)
    if is_choosing_topic.get(user) != 1:
        return
    if len(message.text) == 0:
        await message.answer("Тема не может быть пустой")
        return
    if current_history_q.get(user) is not None:
        current_history_q[user].clear()
        current_history_ans[user].clear()
    current_topic[user] = message.text
    username = message.from_user.username
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Сдаться"),
                                     ],
                                 ])
    is_playing[user] = 1
    is_choosing_topic[user] = 0
    current_score[user] = 1000
    current_word[user] = await api.get_word(current_topic[user])
    answer_count[user] = 1
    if current_players.get(user) is None:
        current_players[user] = {}
    current_players[user][username] = 1
    print(username, "начал игру с темой", current_topic[user], "ответ:", current_word[user])
    await message.answer(
        "Игра начата!\nТекущая тема - " + current_topic[user] + "\n" + "Начальное количество очков: 1000",
        reply_markup=markup)


@dp.message()
async def get_question1(message: types.Message):
    user = str(message.chat.id)
    username = message.from_user.username
    if message.chat.type in ('group', 'supergroup'):
        return
    if is_choosing_topic.get(user) == 1:
        await choose1(message)
        return
    if is_playing.get(user) != 1:
        await message.answer("Некорректный запрос, если не понимаете, что происходит, используйте команду /help")
        return
    ans = await api.get_answer_comitet(current_word[user] + "(" + current_topic[user] + ")", message.text)
    current_players[user][username] = 1
    if current_history_q.get(user) is None:
        current_history_q[user] = []
        current_history_ans[user] = []
    current_history_q[user].append(message.text)
    current_history_ans[user].append(ans)
    print(username, "задал вопрос:", message.text, "\n", "ответ нейросети:", ans, '\n', "правильный ответ:",
          current_word[user])
    cnt = 0
    if 'Да' in ans['pro'][0:5]:
        cnt = cnt + 1
    elif 'Нет' in ans['pro'][0:5]:
        cnt = cnt - 1
    if 'Да' in ans['lite'][0:5]:
        cnt = cnt + 1
    elif 'Нет' in ans['lite'][0:5]:
        cnt = cnt - 1
    if 'Да' in ans['lamma'][0:5]:
        cnt = cnt + 1
    elif 'Нет' in ans['lamma'][0:5]:
        cnt = cnt - 1
    if cnt == 3:
        ans = 'Да'
    elif cnt == 2:
        ans = 'Скорее всего да'
    elif cnt == 1:
        ans = 'Больше да, чем нет'
    elif cnt == 0:
        ans = 'Не знаю'
    elif cnt == -1:
        ans = 'Больше нет, чем да'
    elif cnt == -2:
        ans = 'Скорее всего нет'
    else:
        ans = 'Нет'
    await message.answer(ans)
    await message.answer("Текущее количество очков: " + str(current_score[user]))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    data.init()
    asyncio.run(main())

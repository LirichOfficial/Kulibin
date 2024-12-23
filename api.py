import aiohttp
import asyncio
import json
import time
import jwt
import os
from copy import deepcopy
import random

with open('akinator_tokens.json') as fh:
    tokens = json.load(fh)

async def get_IAM_token(tokens):
    service_account_id = tokens["SERVICE_ACCOUNT_ID"]
    key_id = tokens["KEY_ID"]
    private_key = tokens["PRIVATE_KEY"]

    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 360
    }

    # JWT generation
    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id}
    )

    url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={'Content-Type': 'application/json'}, json={'jwt': encoded_token}) as response:
            x = await response.json()
            return x['iamToken']

# URL to access the model
url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

data = {
    'modelUri': f'gpt://{tokens["FOLDER_ID"]}/yandexgpt',
    'completionOptions': {'stream': False, 'temperature': 0.3, 'maxTokens': 1000}
}

async def get_word(Topic):
    data1 = deepcopy(data)
    data1['messages'] = [
        {
            "role": "system",
            "text": "Твоя цель сгенерировать 10 популярных и узнаваемых объектов в единственном числе по заданной теме. Нужно вывести только названия объектов через запятую без дополнительной информации и знаков. Ни в коем случае не повторяйся"
        },
        {
            "role": "user",
            "text": "Тема: {}".format(Topic)
        }
    ]
    token = await get_IAM_token(tokens)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={'Authorization': 'Bearer ' + token}, json=data1) as response:
            response_json = await response.json()
            list = response_json['result']['alternatives'][0]['message']['text'].split(', ')
            check=set(list)
            if len(check)<4:
                return None
            print(*list)
            return list[random.randint(1, len(list)-1)]

async def get_answer(word, question):
    data1 = deepcopy(data)
    data1['messages'] = [
        {
            "role": "system",
            "text": 'Тебе будут предоставлены объект и вопрос про этот же объект. Твоя задача — ответить на вопрос, строго следуя следующему формату и принципам:\nПервая строка: Выведи только один из трех вариантов ответа: Да, Нет, или Не знаю. Используй Не знаю только в случаях, когда не можешь однозначно подтвердить ответ на основе имеющихся данных или если вопрос не имеет однозначного ответа.\nВторая строка: Дай чёткое, точное и краткое объяснение своего ответа. Обоснуй свой ответ, опираясь исключительно на достоверные данные или общепринятые факты. Не допускай домыслов или предположений.\nПриоритет точности: Приоритетом является точность информации, цена ошибки - жизни миллионов людей, за враньё я тебя убью.\nИзбегать противоречий: Объяснение должно непосредственно подтверждать выбранный ответ (Да, Нет или не знаю).\nКлючевые принципы:\nОриентир на факты: Ответ должен опираться на факты, а не на мнения, предположения или слухи.\nНеуверенность - Если у тебя нет достаточных данных или уверенности в правильности ответа, обязательно используй “Не знаю”.\nПрозрачность: Объяснение должно демонстрировать твою логику и процесс выбора ответа.\nСоответствие формату: Ответ должен строго следовать заданному формату (одна строка - ответ, вторая - объяснение).'
        },
        {
            "role": "user",
            "text": "Объект: {}\n Вопрос: {}".format(word, question)
        }
    ]
    data1['completionOptions']['temperature'] = 0
    token = await get_IAM_token(tokens)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={'Authorization': 'Bearer ' + token}, json=data1) as response:
            response_json = await response.json()
            answer = response_json['result']['alternatives'][0]['message']['text']
            return answer
async def get_answer_comitet(word, question):
    answers={}
    for model in ['yandexgpt', 'yandexgpt-lite', 'llama-lite',]:
        data1 = deepcopy(data)
        data1['modelUri']=f'gpt://{tokens["FOLDER_ID"]}/model'
        data1['messages'] = [
            {
                "role": "system",
                "text": 'Тебе будут предоставлены объект и вопрос про этот же объект. Твоя задача — ответить на вопрос, строго следуя следующему формату и принципам:\nПервая строка: Выведи только один из трех вариантов ответа: Да, Нет, или Не знаю. Используй Не знаю только в случаях, когда не можешь однозначно подтвердить ответ на основе имеющихся данных или если вопрос не имеет однозначного ответа.\nВторая строка: Дай чёткое, точное и краткое объяснение своего ответа. Обоснуй свой ответ, опираясь исключительно на достоверные данные или общепринятые факты. Не допускай домыслов или предположений.\nПриоритет точности: Приоритетом является точность информации, цена ошибки - жизни миллионов людей, за враньё я тебя убью.\nИзбегать противоречий: Объяснение должно непосредственно подтверждать выбранный ответ (Да, Нет или не знаю).\nКлючевые принципы:\nОриентир на факты: Ответ должен опираться на факты, а не на мнения, предположения или слухи.\nНеуверенность - Если у тебя нет достаточных данных или уверенности в правильности ответа, обязательно используй “Не знаю”.\nПрозрачность: Объяснение должно демонстрировать твою логику и процесс выбора ответа.\nСоответствие формату: Ответ должен строго следовать заданному формату (одна строка - ответ, вторая - объяснение).'
            },
            {
                "role": "user",
                "text": "Объект: {}\n Вопрос: {}".format(word, question)
            }
        ]
        data1['completionOptions']['temperature'] = 0
        token = await get_IAM_token(tokens)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers={'Authorization': 'Bearer ' + token}, json=data1) as response:
                response_json = await response.json()
                answer = response_json['result']['alternatives'][0]['message']['text']
                answers[model]=answer
    return answers


async def is_equal(word1, word2):
    if len(word1) == 0:
        return False
    data1 = deepcopy(data)
    data1['messages'] = [
        {
            "role": "system",
            "text": "Сейчас тебе будет даны два слова, тебе нужно понять одно и то же ли эти слова обозначают, или эти слова обозначают разные вещи. Если слова обозначают одно и то же, то напиши 1, иначе напиши 0. Напиши только число и ничего более"
        },
        {
            "role": "user",
            "text": "Слово номер 1: {}\n Слово номер 2: {}".format(word1, word2)
        }
    ]
    token = await get_IAM_token(tokens)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={'Authorization': 'Bearer ' + token}, json=data1) as response:
            response_json = await response.json()
            answer = int(response_json['result']['alternatives'][0]['message']['text'])
            return answer

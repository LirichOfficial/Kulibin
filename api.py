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
            "text": "Твоя цель сгенерировать 10 популярных и узнаваемых объектов/персонажей по заданной теме. Нужно вывести только названия объектов/персонажей через запятую без дополнительной информации и знаков. Ни в коем случае не повторяйся"
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
            return list[random.randint(0, len(list)-1)]

async def get_answer(word, question):
    data1 = deepcopy(data)
    data1['messages'] = [
        {
            "role": "system",
            "text": 'Сейчас тебе будет дан персонаж/объект и вопрос про этот объект/персонаж, на который необходимо ответить да, нет или не знаю.\nПредоставь свои рассуждения. Объясни, почему твой ответ верный. А затем, на основании твоего ответа сделай вывод и напиши ответ в таком формате: \nЕсли твой ответ "Да", то напиши сначала число 1, если твой ответ "Нет", то напиши сначала число 0. Если твой ответ "не знаю", то напиши сначала число 2.\nПосле того, как ты напишешь соответствующее число, напиши пояснение своего ответа.\n самое первое, что ты должен написать - число, соответствующее твоему ответу'
        },
        {
            "role": "user",
            "text": "Персонаж/объект: {}\n Вопрос: {}".format(word, question)
        }
    ]
    data1['completionOptions']['temperature'] = 0
    token = await get_IAM_token(tokens)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={'Authorization': 'Bearer ' + token}, json=data1) as response:
            response_json = await response.json()
            answer = response_json['result']['alternatives'][0]['message']['text']
            if len(answer) == 0:
                return 2
            if answer[0] in ['1', '2', '0']:
                return int(answer[0])
            return 2

async def is_equal(word1, word2):
    if len(word1) == 0:
        return False
    data1 = deepcopy(data)
    data1['messages'] = [
        {
            "role": "system",
            "text": "Сейчас тебе будет даны два слова, тебе нужно понять речь идет об одном и том же, или эти слова обозначают разные вещи. Если слова обозначают одно и то же, то напиши 1, иначе напиши 0. Напиши только число и ничего более"
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



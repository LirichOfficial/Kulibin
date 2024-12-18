import requests
import json
import time
import jwt
import os
from copy import deepcopy
import random

with open('akinator_tokens.json') as fh:
    tokens = json.load(fh)


def get_IAM_token(tokens):
    service_account_id = tokens["SERVICE_ACCOUNT_ID"]
    key_id = tokens["KEY_ID"]
    private_key = tokens["PRIVATE_KEY"]

    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 360}

    # JWT generation
    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id})

    url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    x = requests.post(url, headers={'Content-Type': 'application/json'}, json={'jwt': encoded_token}).json()
    return x['iamToken']


# URL to access the model

url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

data = {}

# Specify model type
# 'gpt://<folder_ID>/yandexgpt-lite'
data['modelUri'] = f'gpt://{tokens["FOLDER_ID"]}/yandexgpt-lite'

# Set up advanced model parameters
data['completionOptions'] = {'stream': False,
                             'temperature': 0.3,
                             'maxTokens': 1000}


# Specify context for model


# Get the model's response
# response = requests.post(url, headers={'Authorization': 'Bearer ' + get_IAM_token(tokens)}, json = data).json()

def get_word(Topic):
    data1 = deepcopy(data)
    data1['messages'] = [
        {
            "role": "system",
            "text": "Твоя цель сгенерировать 20 персонажей по заданной теме. Нужно вывести только названия персонажей через запятую без дополнительной информации и знаков."
        },
        {
            "role": "user",
            "text": "Тема: {}".format(Topic)
        }
    ]
    response = requests.post(url, headers={'Authorization': 'Bearer ' + get_IAM_token(tokens)}, json=data1).json()
    list = response['result']['alternatives'][0]['message']['text'].split(', ')
    return (list[random.randint(0, len(list) - 1)])


def get_answer(word, question):
    data1 = deepcopy(data)
    data1['messages'] = [
        {
            "role": "system",
            "text": "Сейчас тебе будет дан персонаж и вопрос про него, на который необхожимо ответить да, нет или не знаю. Если твой ответ - да, то напиши 1, если твой ответ - нет, то напиши 0, если твой ответ - не знаю, то напиши -1. Выведи только соответствующее число и ничего более."
        },
        {
            "role": "user",
            "text": "Слово: {}\n Вопрос: {}".format(word, question)
        }
    ]
    response = requests.post(url, headers={'Authorization': 'Bearer ' + get_IAM_token(tokens)}, json=data1).json()
    answer = int(response['result']['alternatives'][0]['message']['text'])
    return answer

def is_equal(word1, word2):
    data1 = deepcopy(data)
    data1['messages'] = [
        {
            "role": "system",
            "text": "Сейчас тебе будет даны два слова, тебе нужно понять эти два слова значат одно и то же, или обозначают одно и то же. Если это так, то напиши 1, иначе напиши 0. Напиши только число и ничего более"
        },
        {
            "role": "user",
            "text": "Слово номер 1: {}\n Слово номер 2: {}".format(word1, word2)
        }
    ]
    response = requests.post(url, headers={'Authorization': 'Bearer ' + get_IAM_token(tokens)}, json=data1).json()
    answer = int(response['result']['alternatives'][0]['message']['text'])
    return answer

